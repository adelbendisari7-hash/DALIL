// Captures d'écran de l'interface (revue de design), format téléphone, clair et sombre. Pas un test du parcours.
import { execFileSync } from "node:child_process";
import { resolve } from "node:path";
import { test, devices, type Page } from "@playwright/test";
import { PY_PATH } from "../e2e/helpers";

/** Base des tests seulement (recréée à chaque lancement) : prix plus anciens des produits de démonstration, pour que
 * l'historique des prix ait plusieurs mois à montrer. */
function backdatePrices() {
  const script = `
import sqlite3, sys
from datetime import datetime, timedelta, timezone
c = sqlite3.connect(sys.argv[1])
now = datetime.now(timezone.utc)
rows = c.execute("select product_id, shop_id, category_id, condition, price from price_points where price is not null").fetchall()
if not c.execute("select 1 from price_points where recorded_at < ?", ((now - timedelta(days=60)).isoformat(),)).fetchone():
    for pid, sid, cat, cond, price in rows:
        for days, k in ((150, 0.86), (110, 0.9), (75, 0.93), (40, 0.97)):
            c.execute("insert into price_points (product_id, shop_id, category_id, condition, price, recorded_at) values (?,?,?,?,?,?)",
                      (pid, sid, cat, cond, round(price * k, -1), (now - timedelta(days=days)).isoformat()))
    c.commit()
`;
  execFileSync(PY_PATH, ["-c", script, resolve(__dirname, "../../backend/e2e.db")]);
}
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
      backdatePrices();
      await page.reload();
      const prices = page.locator(".price-history");
      await prices.waitFor();
      await prices.locator("svg g").nth(5).click();   // un mois touché : son libellé s'affiche
      await prices.screenshot({ path: `${OUT}/${scheme}-03a-prix.png` });
      const first = page.locator(".shop").first();
      await first.getByRole("link", { name: "WhatsApp" }).click();
      await first.getByRole("button", { name: "Oui, trouvée" }).click();
      await first.getByRole("heading").getByRole("link").click();
      await page.locator(".reviews").waitFor();
      await shot(page, "03b-fiche-avis", scheme);
      await page.goto(`${BASE}/`);
      await page.locator(".last-diagnosis").waitFor();
      await page.locator(".hero").screenshot({ path: `${OUT}/${scheme}-01c-accueil-dernier.png`});
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
      // Carnet d'entretien : une voiture et un passage au garage noté (base des tests seulement)
      const token = await page.evaluate(() => localStorage.getItem("dalil.token"));
      const headers = { Authorization: `Bearer ${token}` };
      const car = await (await page.request.post(`${BASE}/api/v1/me/vehicles`, { headers, data: {
        plate: `${uniq}-1${scheme === "light" ? "12" : "13"}-31`, label: "Renault Clio 4", year: 2016, mileage_km: 92000 } })).json();
      await page.request.post(`${BASE}/api/v1/me/vehicles/${car.id}/maintenance`, { headers, data: {
        items: ["vidange", "filtre-air"], other: "Pneus avant", km: 91500, price: 18500, place: "Garage du quartier, Hai Sabah",
        note: "Huile 5W40" } });
      await page.goto(`${BASE}/compte`);
      await page.getByRole("button", { name: "Entretien" }).click();
      await page.locator(".carnet .visit").first().waitFor();
      await page.locator(".carnet").screenshot({ path: `${OUT}/${scheme}-06b-carnet.png` });
      await page.locator(".carnet").getByRole("button", { name: /Modifier le passage/ }).click();
      await page.locator(".carnet").screenshot({ path: `${OUT}/${scheme}-06c-carnet-modifier.png` });
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
