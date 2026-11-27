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

  // 2. Inscription du magasin (nom, position prise au magasin, marques, familles)
  await page.getByLabel("Nom du magasin").fill("[TEST] Pièces Auto Es-Senia");
  await page.getByRole("button", { name: "Je suis au magasin : prendre ma position" }).click();
  await expect(page.getByText("Position enregistrée", { exact: false })).toBeVisible();
  await page.getByRole("button", { name: "Dacia", exact: true }).click();
  await page.getByRole("button", { name: "Freinage", exact: true }).click();
  await page.getByRole("button", { name: "Inscrire mon magasin" }).click();
  await expect(page.getByText("En attente de validation")).toBeVisible();

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
  const v = await request.post(`/api/v1/admin/shops/${shopId}/verify`, { headers: { Authorization: `Bearer ${admin}` } });
  expect(v.ok()).toBeTruthy();

  await page.evaluate(() => localStorage.clear()); // visiteur anonyme
  await page.goto(`/magasins/${shopId}`);
  await expect(page.getByRole("heading", { level: 1 })).toContainText("[TEST] Pièces Auto Es-Senia");
  await expect(page.getByRole("heading", { name: "Catalogue" })).toBeVisible();
  await expect(page.locator("ul.list li")).toHaveCount(20);
});
