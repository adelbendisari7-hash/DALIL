import { expect, test, type Page } from "@playwright/test";
import { execFileSync } from "node:child_process";
import { resolve } from "node:path";
import { PY_PATH } from "./helpers";

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

test("entretien d'une voiture : échéance « à faire », noté « fait », lien vers les magasins", async ({ page }) => {
  await inscrire(page, phone(), "Farid", "Entretien", "/compte");
  await ajouterVoiture(page, plate());
  // Kilométrage du formulaire : 85 000 km, rien de noté : la distribution est « à vérifier »
  await page.getByRole("button", { name: "Entretien" }).click();
  const distribution = page.locator(".maint", { hasText: "Courroie (kit) de distribution" });
  await expect(distribution.locator(".maint-pill")).toHaveText("À vérifier");
  await expect(distribution.getByRole("link", { name: "Voir les magasins" })).toHaveAttribute("href", /category=\d+/);
  // Vidange faite aujourd'hui à 85 000 km : à jour, prochaine à 95 000 km
  const vidange = page.locator(".maint", { hasText: "Vidange et filtre à huile" });
  await vidange.getByRole("button", { name: "Noter : Vidange et filtre à huile fait" }).click();
  await vidange.getByRole("button", { name: "Noter l'entretien" }).click();
  await expect(vidange.locator(".maint-pill")).toHaveText("À jour");
  await expect(vidange.getByText(/95.000 km/)).toBeVisible();
  await expect(page.getByText("le carnet d'entretien de votre voiture fait foi", { exact: false })).toBeVisible();
});

test("rappel d'entretien sur l'accueil : vidange dépassée, masquable, mène au panneau de la voiture", async ({ page }) => {
  await inscrire(page, phone(), "Nadia", "Rappel", "/compte");
  await ajouterVoiture(page, plate());   // 85 000 km
  // Vidange notée à 70 000 km : dépassée de 5 000 km (intervalle indicatif de 10 000 km)
  const token = await page.evaluate(() => localStorage.getItem("dalil.token"));
  const headers = { Authorization: `Bearer ${token}` };
  const cars = await (await page.request.get("/api/v1/me/vehicles", { headers })).json();
  const id = cars[0].id;
  expect((await page.request.post(`/api/v1/me/vehicles/${id}/maintenance`, { headers, data: { item: "vidange", km: 70000 } })).status()).toBe(201);

  await page.goto("/");
  const banner = page.locator(".upkeep-banner");
  await expect(banner.getByRole("heading", { name: "Entretien à prévoir" })).toBeVisible();
  await expect(banner).toContainText(/vidange et filtre à huile \(dépassé de 5.000 km\)/);
  await banner.getByRole("link").first().click();
  await expect(page).toHaveURL((u) => u.pathname === "/compte" && u.searchParams.get("entretien") === String(id));
  await expect(page.locator(".maint", { hasText: "Vidange et filtre à huile" }).locator(".maint-pill")).toHaveText("À faire");

  await page.goto("/");
  await page.locator(".upkeep-banner").getByRole("button", { name: "Plus tard" }).click();
  await expect(page.locator(".upkeep-banner")).toHaveCount(0);
  await page.reload();
  await expect(page.getByRole("heading", { name: "Qu'est-ce qui ne va pas", exact: false })).toBeVisible();
  await expect(page.locator(".upkeep-banner")).toHaveCount(0);   // masqué pour la journée
});

test("carnet d'entretien : un passage avec plusieurs opérations, prix, kilométrage, garage ; corrigé puis supprimé", async ({ page }) => {
  await inscrire(page, phone(), "Rachid", "Carnet", "/compte");
  await ajouterVoiture(page, plate());   // 85 000 km
  await page.getByRole("button", { name: "Entretien" }).click();
  const carnet = page.locator(".carnet");
  await expect(carnet).toContainText("Rien de noté pour l'instant");

  await carnet.getByRole("button", { name: "Noter un passage au garage" }).click();
  const form = carnet.locator(".visit-form");
  await form.getByRole("button", { name: "Vidange et filtre à huile" }).click();
  await form.getByRole("button", { name: "Filtre à air" }).click();
  await form.getByLabel("Autre chose (facultatif)").fill("Pneus avant");
  await form.getByLabel("Kilométrage", { exact: true }).fill("86200");
  await form.getByLabel("Prix payé (DA)").fill("18500");
  await form.getByLabel("Garage ou magasin (facultatif)").fill("Garage du quartier");
  await form.getByRole("button", { name: "Enregistrer dans le carnet" }).click();

  const visit = carnet.locator(".visit").first();
  await expect(visit).toContainText(/86.200 km/);
  await expect(visit).toContainText(/18.500 DA/);
  await expect(visit).toContainText("Vidange et filtre à huile, Filtre à air, Pneus avant");
  await expect(visit).toContainText("Garage du quartier");
  await expect(carnet.locator(".carnet-total")).toContainText(/18.500 DA dépensés sur 12 mois/);
  // Les échéances partent de ce passage, et le kilométrage de la voiture a suivi
  const vidange = page.locator(".maint", { hasText: "Vidange et filtre à huile" });
  await expect(vidange.locator(".maint-pill")).toHaveText("À jour");
  await expect(vidange.getByText(/96.200 km/)).toBeVisible();
  await expect(page.getByText(/86.200 km/).first()).toBeVisible();

  await visit.getByRole("button", { name: /Modifier le passage/ }).click();
  await carnet.getByLabel("Prix payé (DA)").fill("19000");
  await carnet.getByRole("button", { name: "Enregistrer les corrections" }).click();
  await expect(carnet.locator(".visit").first()).toContainText(/19.000 DA/);

  page.once("dialog", (d) => d.accept());
  await carnet.locator(".visit").first().getByRole("button", { name: /Supprimer le passage/ }).click();
  await expect(carnet).toContainText("Rien de noté pour l'instant");
});

const isoIn = (days: number) => new Date(Date.now() + days * 86_400_000).toISOString().slice(0, 10);

test("papiers : assurance qui finit dans 5 jours -> rappel urgent, agenda, renouvellement", async ({ page }) => {
  await inscrire(page, phone(), "Sofiane", "Papiers", "/compte");
  await ajouterVoiture(page, plate());
  await page.getByRole("button", { name: "Papiers" }).click();
  const assurance = page.locator(".paper", { hasText: "Assurance" });
  await expect(assurance.locator(".paper-pill")).toHaveText("Non renseigné");
  await assurance.getByRole("button", { name: "Renseigner : Assurance" }).click();
  await assurance.getByLabel("Début de l'assurance").fill(isoIn(-360));
  await assurance.getByLabel("Valable jusqu'au").fill(isoIn(5));
  await assurance.getByLabel("Compagnie d'assurance (facultatif)").fill("Assureur test");
  await assurance.getByRole("button", { name: "Enregistrer" }).click();
  await expect(assurance.locator(".paper-pill")).toHaveText("Urgent");
  await expect(assurance).toContainText("finit dans 5 jours");

  // Le téléphone préviendra 7 jours avant et la veille, à 9 h
  const [download] = await Promise.all([page.waitForEvent("download"), assurance.getByRole("button", { name: "Ajouter à mon agenda" }).click()]);
  expect(download.suggestedFilename()).toMatch(/^dalil-assurance-.*\.ics$/);
  const ics = await (await import("node:fs/promises")).readFile(await download.path(), "utf-8");
  expect(ics).toContain("BEGIN:VEVENT");
  expect(ics).toContain(`DTSTART;VALUE=DATE:${isoIn(5).replaceAll("-", "")}`);
  expect(ics).toContain("TRIGGER:-PT159H");
  expect(ics).toContain("TRIGGER:-PT15H");

  // Accueil : rappel rouge, impossible à masquer ; onglet Compte : repère
  await page.goto("/");
  const banner = page.locator(".papers-banner");
  await expect(banner).toContainText("Assurance");
  await expect(banner).toContainText("finit dans 5 jours");
  await expect(banner.getByRole("button", { name: "Plus tard" })).toHaveCount(0);
  await expect(page.getByRole("link", { name: /Mon compte \(1 papiers à renouveler\)/ })).toBeVisible();

  // Renouvelée pour un an : plus de rappel
  await banner.getByRole("link").first().click();
  const again = page.locator(".paper", { hasText: "Assurance" });
  await again.getByRole("button", { name: "Noter le renouvellement : Assurance" }).click();
  await again.getByRole("button", { name: "+ 1 an" }).click();
  await again.getByRole("button", { name: "Enregistrer" }).click();
  await expect(again.locator(".paper-pill")).toHaveText("Valable");
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Qu'est-ce qui ne va pas", exact: false })).toBeVisible();
  await expect(page.locator(".papers-banner")).toHaveCount(0);
});

test("carnet : passage relié à un magasin DALIL contacté, lien vers sa fiche", async ({ page }) => {
  await inscrire(page, phone(), "Walid", "Magasin", "/compte");
  await ajouterVoiture(page, plate());
  const shops = await (await page.request.get("/api/v1/shops")).json();
  const shop = shops[0];
  expect((await page.request.post("/api/v1/contact-events", { data: { shop_id: shop.id, channel: "call" } })).status()).toBe(201);
  await page.reload();
  await page.getByRole("button", { name: "Entretien" }).click();
  const carnet = page.locator(".carnet");
  await carnet.getByRole("button", { name: "Noter un passage au garage" }).click();
  await carnet.getByRole("button", { name: "Vidange et filtre à huile" }).click();
  await carnet.locator(".chip", { hasText: shop.name }).click();   // pastille « nom · commune »
  await expect(carnet.getByLabel("Garage ou magasin (facultatif)")).toHaveValue(shop.name);
  await carnet.getByRole("button", { name: "Enregistrer dans le carnet" }).click();
  await expect(carnet.locator(".visit").first().getByRole("link", { name: shop.name })).toHaveAttribute("href", `/magasins/${shop.id}`);
  await expect(carnet.getByRole("button", { name: "Envoyer le carnet au mécanicien" })).toBeVisible();
});

test("prix suivi : baisse signalée sur l'accueil et dans le compte, « Vu » retire l'alerte", async ({ page }) => {
  await inscrire(page, phone(), "Hakim", "Prix", "/compte");
  const fams = await (await page.request.get("/api/v1/parts/categories")).json();
  const plaq = fams.flatMap((f: { children: { id: number; name: string }[] }) => f.children)
    .find((c: { name: string }) => c.name === "Plaquettes de frein avant");
  await page.goto(`/magasins?category=${plaq.id}&part=${encodeURIComponent(plaq.name)}`);
  await page.getByRole("button", { name: "Suivre le prix de cette pièce" }).click();
  await expect(page.getByText("Prix suivi : DALIL vous préviendra s'il baisse.")).toBeVisible();

  // Un magasin baisse son prix de moitié (point de prix écrit dans la base des tests)
  execFileSync(PY_PATH, ["-c", `
import sqlite3, sys
from datetime import datetime, timezone
c = sqlite3.connect(sys.argv[1])
cat = int(sys.argv[2])
row = c.execute("select product_id, shop_id, category_id, condition, min(price) from price_points where category_id = ? and price is not null", (cat,)).fetchone()
c.execute("insert into price_points (product_id, shop_id, category_id, condition, price, recorded_at) values (?,?,?,?,?,?)",
          (row[0], row[1], row[2], row[3], round(row[4] / 2), datetime.now(timezone.utc).isoformat()))
c.commit()
`, resolve(__dirname, "../../backend/e2e.db"), String(plaq.id)]);

  await page.goto("/");
  const banner = page.locator(".price-banner");
  await expect(banner).toContainText("Plaquettes de frein avant");
  await expect(banner).toContainText("− 50 %");
  await page.goto("/compte");
  const watch = page.locator(".watch", { hasText: "Plaquettes de frein avant" });
  await expect(watch).toContainText("En baisse");
  await watch.getByRole("button", { name: "Vu" }).click();
  await expect(watch).not.toContainText("En baisse");
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Qu'est-ce qui ne va pas", exact: false })).toBeVisible();
  await expect(page.locator(".price-banner")).toHaveCount(0);
});
