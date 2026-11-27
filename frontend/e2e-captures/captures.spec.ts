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
      await page.getByRole("button", { name: "Pression d'huile" }).click();
      await page.getByRole("button", { name: "Moteur", exact: true }).click();
      await page.locator(".lights").screenshot({ path: `${OUT}/${scheme}-01b-voyants.png` });
      await page.getByRole("button", { name: "Pression d'huile" }).click();
      await page.getByRole("button", { name: "Moteur", exact: true }).click();
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

test.describe("magasin", () => {
  test.use({ geolocation: { latitude: 35.6987, longitude: -0.6349 }, permissions: ["geolocation"] });
  test("écrans du magasin (clair)", async ({ page, request }) => {
    test.setTimeout(240_000);
    const scheme = "light";
    const r = await request.post(`${BASE}/api/v1/auth/register`, { data: { first_name: "Rachid", last_name: "Kaci",
      phone: `0558${uniq}`, password: "capture-123", consent: true } });
    const { token, user } = await r.json();
    await page.goto(`${BASE}/`);
    await page.evaluate(([tk, u]) => { localStorage.setItem("dalil.token", tk); localStorage.setItem("dalil.user", u); },
      [token, JSON.stringify(user)]);
    await page.goto(`${BASE}/espace-magasin`);
    await page.getByLabel("Nom du magasin").fill("Pièces Auto El Bahia");
    await shot(page, "10-magasin-etape1", scheme);
    await page.getByRole("button", { name: "Continuer" }).click();
    await page.getByRole("button", { name: "Je suis au magasin : prendre ma position" }).click();
    await page.locator(".pin").waitFor();
    await page.getByLabel("Repère (facultatif)").fill("en face de la poste");
    await shot(page, "11-magasin-etape2", scheme);
    await page.getByRole("button", { name: "Continuer" }).click();
    const notMine = page.getByRole("button", { name: "Non, c'est un autre magasin" });
    await page.getByRole("button", { name: "Dacia", exact: true }).or(notMine).waitFor();
    if (await notMine.isVisible()) await notMine.click();
    await page.getByRole("button", { name: "+ Marques françaises" }).click();
    await page.getByRole("button", { name: "Freinage", exact: true }).click();
    await shot(page, "12-magasin-etape4", scheme);
    await page.getByRole("button", { name: "Continuer" }).click();
    await shot(page, "13-magasin-recap", scheme);
    await page.getByRole("button", { name: "Inscrire mon magasin" }).click();
    await page.getByText("En attente de vérification", { exact: false }).waitFor();
    await shot(page, "14-magasin-statut", scheme);
    await page.getByRole("tab", { name: /Catalogue/ }).click();
    for (const [name, price] of [["Plaquettes de frein avant", "4500"], ["Filtre à huile", "900"]]) {
      await page.getByRole("button", { name, exact: true }).click();
      await page.getByLabel("Prix en DA").fill(price);
      await page.getByRole("button", { name: "Ajouter le produit" }).click();
      await page.getByText("Produit ajouté.").waitFor();
    }
    await page.locator(".product-row").nth(1).waitFor();
    await shot(page, "15-magasin-catalogue", scheme);
  });
});
