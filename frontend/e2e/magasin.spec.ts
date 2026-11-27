import { expect, test, type APIRequestContext } from "@playwright/test";
import { ADMIN_PHONE, OTP, makeCatalog } from "./helpers";

/** Critère de l'étape 10 : un magasin test s'inscrit sur son téléphone et publie 20 produits (import Excel). */

test.use({ geolocation: { latitude: 35.6987, longitude: -0.6349 }, permissions: ["geolocation"] });

async function apiToken(request: APIRequestContext, phone: string): Promise<string> {
  await request.post("/api/v1/auth/otp/request", { data: { phone } });
  const r = await request.post("/api/v1/auth/otp/verify", { data: { phone, code: OTP } });
  return (await r.json()).token;
}

test("un magasin test s'inscrit et publie 20 produits par import Excel", async ({ page, request }, info) => {
  // 1. Inscription par mot de passe, depuis l'espace magasin (les SMS sont payants)
  await page.goto("/espace-magasin");
  await page.getByRole("link", { name: "Connexion" }).last().click();
  await page.getByRole("tab", { name: "Créer un compte" }).click();
  await page.getByLabel("Prénom").fill("Rachid");
  await page.getByLabel("Nom", { exact: true }).fill("Test");
  await page.getByLabel("Numéro de mobile").fill(`0555${String(Date.now()).slice(-6)}`);
  await page.getByLabel("Mot de passe (8 caractères au moins)").fill("magasin-e2e");
  await page.getByRole("checkbox").check();
  await page.getByRole("button", { name: "Créer mon compte" }).click();
  await expect(page).toHaveURL(/espace-magasin/);

  // 2. Inscription du magasin en cinq étapes, chronométrée (cahier des charges : moins de 3 minutes)
  const t0 = Date.now();
  await page.getByLabel("Nom du magasin").fill("[TEST] Pièces Auto Es-Senia");
  await page.getByRole("button", { name: "Continuer" }).click();
  await page.getByRole("button", { name: "Je suis au magasin : prendre ma position" }).click();
  await expect(page.getByText("Position enregistrée", { exact: false })).toBeVisible();
  await expect(page.locator(".pin")).toBeVisible();   // épingle posée sur la carte
  await page.getByRole("button", { name: "Continuer" }).click();
  const notMine = page.getByRole("button", { name: "Non, c'est un autre magasin" });
  await expect(page.getByRole("button", { name: "Dacia", exact: true }).or(notMine)).toBeVisible();
  if (await notMine.isVisible()) await notMine.click();   // fiche de l'équipe proche : ce n'est pas la nôtre
  await page.getByRole("button", { name: "Dacia", exact: true }).click();
  await page.getByRole("button", { name: "Freinage", exact: true }).click();
  await page.getByRole("button", { name: "Continuer" }).click();
  await expect(page.getByRole("heading", { name: "Vérifiez et envoyez" })).toBeVisible();
  await page.getByRole("button", { name: "Inscrire mon magasin" }).click();
  await expect(page.getByText("En attente de vérification", { exact: false })).toBeVisible();
  expect(Date.now() - t0).toBeLessThan(180_000);

  // 3. Catalogue : modèle Excel téléchargeable, puis import de 20 produits
  await page.getByRole("tab", { name: /Catalogue/ }).click();
  const modele = page.getByRole("link", { name: "Télécharger le modèle Excel" });
  const res = await request.get((await modele.getAttribute("href"))!);
  expect(res.ok()).toBeTruthy();
  const file = info.outputPath("catalogue.xlsx");
  makeCatalog(file, 20);
  await page.getByLabel("Importer un fichier Excel").setInputFiles(file);
  await expect(page.getByText("20 ajoutés, 0 mis à jour, 0 lignes en erreur.")).toBeVisible();
  await expect(page.getByRole("tab", { name: "Catalogue (20)" })).toBeVisible();

  // 4. Validation par l'équipe (appel de vérification), puis fiche publique avec ses 20 produits
  const owner = await page.evaluate(() => localStorage.getItem("dalil.token"));
  const mine = await (await request.get("/api/v1/shops/mine", { headers: { Authorization: `Bearer ${owner}` } })).json();
  const shopId = mine[0].id;
  const admin = await apiToken(request, ADMIN_PHONE);
  const v = await request.post(`/api/v1/admin/shops/${shopId}/verify`, {
    headers: { Authorization: `Bearer ${admin}` }, data: { phone_ok: true, address_ok: true, activity_ok: true } });
  expect(v.ok()).toBeTruthy();

  await page.evaluate(() => localStorage.clear()); // visiteur anonyme
  await page.goto(`/magasins/${shopId}`);
  await expect(page.getByRole("heading", { level: 1 })).toContainText("[TEST] Pièces Auto Es-Senia");
  await expect(page.getByText("Vérifié par DALIL")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Catalogue" })).toBeVisible();
  await expect(page.locator("ul.list li")).toHaveCount(20);
});


/** Se connecter dans le navigateur avec un jeton obtenu par l'API (compte administrateur des tests). */
async function asUser(page: import("@playwright/test").Page, request: APIRequestContext, token: string) {
  const me = await (await request.get("/api/v1/auth/me", { headers: { Authorization: `Bearer ${token}` } })).json();
  await page.goto("/");
  await page.evaluate(([tk, u]) => { localStorage.setItem("dalil.token", tk); localStorage.setItem("dalil.user", u); },
    [token, JSON.stringify(me)]);
}

test("adresse tapée : suggestions de lieux à Oran, épingle posée puis vérification par appel dans l'administration", async ({ page, request }) => {
  // Recherche d'adresse simulée (pas de requête vers OpenStreetMap pendant les tests)
  await page.route("**/api/v1/geo/geocode*", (route) =>
    route.fulfill({ json: [{ label: "Rue Larbi Ben M'hidi, Oran", lat: 35.6995, lng: -0.6402 }] }));
  const phone = `0556${String(Date.now()).slice(-6)}`;
  const r = await request.post("/api/v1/auth/register", { data: { first_name: "Nadia", last_name: "Test", phone,
    password: "magasin-e2e", consent: true } });
  await asUser(page, request, (await r.json()).token);
  await page.goto("/espace-magasin");
  await page.getByLabel("Nom du magasin").fill("[TEST] Pièces El Bahia");
  await page.getByRole("button", { name: "Continuer" }).click();
  await page.getByLabel("Adresse").fill("12 rue Larbi Ben M'hidi");
  await page.getByRole("option", { name: /Larbi Ben M'hidi/ }).click();
  await expect(page.locator(".pin")).toBeVisible();
  await page.getByLabel("Repère (facultatif)").fill("en face de la poste");
  await page.getByRole("button", { name: "Continuer" }).click();
  const notMine = page.getByRole("button", { name: "Non, c'est un autre magasin" });
  await expect(page.getByRole("button", { name: "Dacia", exact: true }).or(notMine)).toBeVisible();
  if (await notMine.isVisible()) await notMine.click();
  await page.getByRole("button", { name: "Freinage", exact: true }).click();
  await page.getByRole("button", { name: "Continuer" }).click();
  await page.getByRole("button", { name: "Inscrire mon magasin" }).click();
  await expect(page.getByText("En attente de vérification", { exact: false })).toBeVisible();

  // L'administrateur appelle, coche la liste de contrôle et valide
  await asUser(page, request, await apiToken(request, ADMIN_PHONE));
  await page.goto("/admin");
  const card = page.locator(".card", { hasText: "[TEST] Pièces El Bahia" });
  await expect(card.getByRole("link", { name: /Appeler/ })).toHaveAttribute("href", /^tel:\+213/);
  const valider = card.getByRole("button", { name: "Valider le magasin" });
  await expect(valider).toBeDisabled();   // tant que les trois points ne sont pas vérifiés
  for (const c of await card.getByRole("checkbox").all()) await c.check();
  await valider.click();
  await expect(card).toHaveCount(0);

  // Le magasin voit son badge et imprime son affiche avec le code QR
  await asUser(page, request, (await r.json()).token);
  await page.goto("/espace-magasin");
  await expect(page.getByText("Vérifié par DALIL").first()).toBeVisible();
  await page.getByRole("link", { name: "Affiche pour le comptoir" }).click();
  await expect(page.getByRole("heading", { name: "Trouvez-nous sur DALIL", exact: true })).toBeVisible();
  await expect(page.locator(".poster-qr svg")).toBeVisible();
});
