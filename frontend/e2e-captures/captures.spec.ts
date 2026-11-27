// Captures d'écran de l'interface (revue de design), format téléphone, clair et sombre. Pas un test du parcours.
import { test, devices, type Page } from "@playwright/test";
const OUT = process.env.CAPTURES || "test-results/captures";
const BASE = process.env.CAP_URL || `http://localhost:${process.env.E2E_WEB_PORT || "3000"}`;
const uniq = String(Date.now()).slice(-6);

async function shot(page: Page, name: string, scheme: string) {
  await page.waitForTimeout(700);
  await page.screenshot({ path: `${OUT}/${scheme}-${name}.png`, fullPage: true });
}

const { defaultBrowserType: _ignored, ...pixel } = devices["Pixel 5"];
test.use({ ...pixel, viewport: { width: 360, height: 780 } });

for (const scheme of ["light", "dark"] as const) {
  test.describe(scheme, () => {
    test.use({ colorScheme: scheme });
    test(`écrans ${scheme}`, async ({ page }) => {
      test.setTimeout(240_000);
      await page.goto(`${BASE}/`);
      await shot(page, "01-accueil", scheme);
      await page.getByLabel("Décrivez le problème").fill("ça grince quand je freine et le volant vibre");
      await page.getByRole("button", { name: "Trouver la panne" }).click();
      await page.getByRole("heading", { name: "Causes probables" }).waitFor({ timeout: 120_000 });
      await shot(page, "02-resultat", scheme);
      await page.getByRole("link", { name: "Voir les magasins" }).first().click();
      await page.locator(".shop").first().waitFor({ timeout: 60_000 });
      await shot(page, "03-magasins", scheme);
      await page.goto(`${BASE}/pieces`);
      await shot(page, "04-pieces", scheme);
      await page.goto(`${BASE}/connexion?inscription=1`);
      await shot(page, "05-inscription", scheme);
      await page.getByLabel("Prénom").fill("Amina");
      await page.getByLabel("Nom", { exact: true }).fill("Benali");
      await page.getByLabel("Numéro de mobile").fill(`0${scheme === "light" ? "556" : "557"}${uniq}`);
      await page.getByLabel("Mot de passe (8 caractères au moins)").fill("capture-123");
      await page.getByRole("checkbox").check();
      await page.getByRole("button", { name: "Créer mon compte" }).click();
      await page.getByRole("heading", { name: "Bienvenue sur DALIL" }).waitFor();
      await shot(page, "06-compte", scheme);
      await page.goto(`${BASE}/espace-magasin`);
      await shot(page, "07-espace-magasin", scheme);
    });
  });
}
