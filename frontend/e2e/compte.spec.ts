import { expect, test, type Page } from "@playwright/test";
import { OTP } from "./helpers";

// Numéros et matricules uniques à chaque exécution : les tests se rejouent sur la même base sans se gêner
const uniq = () => String(Date.now() % 1_000_000 + Math.floor(Math.random() * 1000)).padStart(6, "0").slice(-6);
const phone = () => `0555${uniq()}`;
const plate = () => `${uniq()}-1${String(10 + Math.floor(Math.random() * 15))}-31`;

/** Suppression du compte sur demande (loi 18-07, section 10) : promise à la connexion, faisable depuis le site. */
test("un utilisateur supprime son compte depuis « Mon compte »", async ({ page }) => {
  await page.goto("/connexion?next=/compte");
  const tel = phone();
  await page.getByLabel("Numéro de mobile").fill(tel);
  await page.getByRole("button", { name: "Recevoir le code" }).click();
  await page.getByLabel("Code reçu par SMS").fill(OTP);
  await page.getByRole("checkbox").check();
  await page.getByRole("button", { name: "Me connecter" }).click();

  // Nouveau compte : la page demande d'abord le prénom et le nom
  await expect(page.getByRole("heading", { name: "Créez votre compte" })).toBeVisible();
  await expect(page.getByText(`+213${tel.slice(1)}`)).toBeVisible();
  await expect(page.getByRole("link", { name: "Mon compte", exact: true })).toBeVisible(); // menu : connecté

  page.once("dialog", (d) => d.accept()); // confirmation « action définitive »
  await page.getByRole("button", { name: "Supprimer mon compte" }).click();
  await expect(page.getByText("Votre compte a été supprimé.")).toBeVisible();
  await expect(page.getByRole("link", { name: "Connexion" })).toBeVisible(); // menu : déconnecté
  expect(await page.evaluate(() => localStorage.getItem("dalil.token"))).toBeNull();
});


async function connecter(page: Page, phone: string, next = "/") {
  await page.goto(`/connexion?next=${next}`);
  await page.getByLabel("Numéro de mobile").fill(phone);
  await page.getByRole("button", { name: "Recevoir le code" }).click();
  await page.getByLabel("Code reçu par SMS").fill(OTP);
  await page.getByRole("checkbox").check();
  await page.getByRole("button", { name: "Me connecter" }).click();
}

async function creerCompte(page: Page, prenom: string, nom: string) {
  await expect(page.getByRole("heading", { name: "Créez votre compte" })).toBeVisible();
  await page.getByLabel("Prénom").fill(prenom);
  await page.getByLabel("Nom", { exact: true }).fill(nom);
  await page.getByRole("button", { name: "Enregistrer", exact: true }).click();
  await expect(page.getByText("Informations enregistrées.")).toBeVisible();
}

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
  await connecter(page, phone());
  await creerCompte(page, "Amina", "Benali");
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
  await connecter(page, phone(), "/compte");
  await creerCompte(page, "Karim", "Haddad");
  await ajouterVoiture(page, p);
  await expect(page.locator(".plate", { hasText: p })).toBeVisible();
  await page.getByRole("button", { name: "Déconnexion" }).click();
  await page.evaluate(() => localStorage.clear());

  await connecter(page, phone(), "/compte");
  await creerCompte(page, "Yacine", "Mansouri");
  await ajouterVoiture(page, p.replaceAll("-", " "));
  await expect(page.getByRole("alert").filter({ hasText: "déjà enregistré" })).toBeVisible();
  await expect(page.getByText("Karim")).toHaveCount(0);   // rien n'est dévoilé du propriétaire
  await page.getByLabel("Message pour l'équipe DALIL (facultatif)").fill("Achetée le mois dernier");
  await page.getByRole("button", { name: "C'est ma voiture : signaler" }).click();
  await expect(page.getByText("Signalement envoyé.")).toBeVisible();
});
