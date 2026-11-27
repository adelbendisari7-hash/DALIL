import { expect, test, type Page } from "@playwright/test";

// Numéros et matricules uniques à chaque exécution : les tests se rejouent sur la même base sans se gêner
const uniq = () => String(Date.now() % 1_000_000 + Math.floor(Math.random() * 1000)).padStart(6, "0").slice(-6);
const phone = () => `0555${uniq()}`;
const plate = () => `${uniq()}-1${String(10 + Math.floor(Math.random() * 15))}-31`;

/** Inscription par mot de passe (les SMS sont payants) : prénom, nom, numéro, mot de passe, consentement. */
async function inscrire(page: Page, tel: string, prenom: string, nom: string, next = "/") {
  await page.goto(`/connexion?inscription=1&next=${next}`);
  await page.getByLabel("Prénom").fill(prenom);
  await page.getByLabel("Nom", { exact: true }).fill(nom);
  await page.getByLabel("Numéro de mobile").fill(tel);
  await page.getByLabel("Mot de passe (8 caractères au moins)").fill("motdepasse-e2e");
  await page.getByRole("checkbox").check();
  await page.getByRole("button", { name: "Créer mon compte" }).click();
  await expect(page.getByRole("heading", { name: "Bienvenue sur DALIL" })).toBeVisible();
}

/** Suppression du compte sur demande (loi 18-07, section 10) : promise à la connexion, faisable depuis le site. */
test("un utilisateur supprime son compte depuis « Mon compte »", async ({ page }) => {
  const tel = phone();
  await inscrire(page, tel, "Samir", "Toumi", "/compte");
  await expect(page.getByText(`+213${tel.slice(1)}`)).toBeVisible();
  await expect(page.getByRole("link", { name: "Mon compte", exact: true })).toBeVisible(); // menu : connecté

  page.once("dialog", (d) => d.accept()); // confirmation « action définitive »
  await page.getByRole("button", { name: "Supprimer mon compte" }).click();
  await expect(page.getByText("Votre compte a été supprimé.")).toBeVisible();
  await expect(page.getByRole("link", { name: "Connexion" })).toBeVisible(); // menu : déconnecté
  expect(await page.evaluate(() => localStorage.getItem("dalil.token"))).toBeNull();
});

test("connexion par mot de passe : bon mot de passe accepté, mauvais refusé, numéro déjà pris refusé", async ({ page }) => {
  const tel = phone();
  await inscrire(page, tel, "Lina", "Saadi");
  await page.getByRole("button", { name: "Déconnexion" }).click();
  await page.goto("/connexion?next=/compte");
  await page.getByLabel("Numéro de mobile").fill(tel);
  await page.getByLabel("Mot de passe", { exact: true }).fill("mauvais-mdp");
  await page.getByRole("button", { name: "Me connecter" }).click();
  await expect(page.getByRole("alert").filter({ hasText: "Numéro ou mot de passe incorrect" })).toBeVisible();
  await page.getByLabel("Mot de passe", { exact: true }).fill("motdepasse-e2e");
  await page.getByRole("button", { name: "Me connecter" }).click();
  await expect(page.getByRole("heading", { name: "Mon compte", exact: true })).toBeVisible();
  // Le même numéro, écrit autrement, ne peut pas créer un second compte
  await page.evaluate(() => localStorage.clear());
  await page.goto("/connexion?inscription=1");
  await page.getByLabel("Prénom").fill("Autre");
  await page.getByLabel("Nom", { exact: true }).fill("Personne");
  await page.getByLabel("Numéro de mobile").fill(`+213 ${tel.slice(1)}`);
  await page.getByLabel("Mot de passe (8 caractères au moins)").fill("autre-mdp-123");
  await page.getByRole("checkbox").check();
  await page.getByRole("button", { name: "Créer mon compte" }).click();
  await expect(page.getByRole("alert").filter({ hasText: "déjà un compte" })).toBeVisible();
});

async function ajouterVoiture(page: Page, matricule: string) {
  await page.getByLabel("Matricule").fill(matricule);
  await page.getByLabel("Marque").selectOption({ label: "Renault" });
  await page.getByLabel("Modèle", { exact: true }).selectOption({ label: "Clio 4" });
  await expect.poll(() => page.getByLabel("Année").locator("option").count()).toBeGreaterThan(1);
  await page.getByLabel("Année").selectOption({ index: 1 });
  // Une seule motorisation pour cette année : choisie d'office ; sinon la liste des motorisations s'affiche
  const engine = page.getByLabel("Motorisation");
  const chosen = page.locator(".ok", { hasText: "Clio 4" });
  await expect(chosen.or(engine)).toBeVisible();
  // (la liste peut s'afficher un instant puis se refermer quand l'année ne laisse qu'une motorisation)
  if (!(await chosen.isVisible())) await engine.selectOption({ index: 1 }, { timeout: 3000 }).catch(() => undefined);
  await expect(chosen).toBeVisible();
  await page.getByLabel("Kilométrage").fill("85000");
  await page.getByRole("button", { name: "Enregistrer la voiture" }).click();
}

test("compte client : créé après la connexion, une voiture ajoutée, diagnostic rangé dans l'historique", async ({ page }) => {
  await inscrire(page, phone(), "Amina", "Benali");
  const p = plate();
  await ajouterVoiture(page, p.replaceAll("-", " "));
  await expect(page.locator(".plate", { hasText: p })).toBeVisible();
  await expect(page.getByText("85 000 km", { exact: false })).toBeVisible();

  await page.getByRole("button", { name: "Continuer" }).click();   // retour à l'accueil
  await expect(page.getByRole("button", { name: /Clio 4/ })).toHaveAttribute("aria-pressed", "true");
  await page.getByLabel("Décrivez le problème").fill("ça grince quand je freine");
  await page.getByRole("button", { name: "Trouver la panne" }).click();
  await expect(page.getByRole("heading", { name: "Causes probables" })).toBeVisible({ timeout: 60_000 });
  await expect(page.getByText(/Pour Renault Clio 4/)).toBeVisible();

  await page.goto("/compte");
  await expect(page.getByRole("heading", { name: "Mon compte", exact: true })).toBeVisible();
  await expect(page.getByRole("link", { name: /→/ }).first()).toBeVisible();   // le diagnostic est dans l'historique
});

test("matricule déjà enregistré par un autre client : refusé, puis signalé", async ({ page }) => {
  const p = plate();
  await inscrire(page, phone(), "Karim", "Haddad", "/compte");
  await ajouterVoiture(page, p);
  await expect(page.locator(".plate", { hasText: p })).toBeVisible();
  await page.getByRole("button", { name: "Déconnexion" }).click();
  await page.evaluate(() => localStorage.clear());

  await inscrire(page, phone(), "Yacine", "Mansouri", "/compte");
  await ajouterVoiture(page, p.replaceAll("-", " "));
  await expect(page.getByRole("alert").filter({ hasText: "déjà enregistré" })).toBeVisible();
  await expect(page.getByText("Karim")).toHaveCount(0);   // rien n'est dévoilé du propriétaire
  await page.getByLabel("Message pour l'équipe DALIL (facultatif)").fill("Achetée le mois dernier");
  await page.getByRole("button", { name: "C'est ma voiture : signaler" }).click();
  await expect(page.getByText("Signalement envoyé.")).toBeVisible();
});
