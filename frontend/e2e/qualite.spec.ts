import { expect, test } from "@playwright/test";

/** Défauts trouvés en explorant l'application le 17/11/2026 (agent-browser), corrigés et gardés ici. */

test("la liste des années se limite à celles du modèle choisi", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("Marque").selectOption({ label: "Chery" });
  await page.getByLabel("Modèle").selectOption({ label: "Tiggo 4" });
  // Les années arrivent avec les motorisations du modèle (requête) : attendre que la liste soit remplie.
  await expect.poll(() => page.getByLabel("Année").locator("option").count()).toBeGreaterThan(1);
  const years = (await page.getByLabel("Année").locator("option").allTextContents()).map(Number).filter(Boolean);
  expect(years.length).toBeGreaterThan(0);
  expect(Math.min(...years)).toBeGreaterThanOrEqual(2020); // Tiggo 4 : à partir de 2020, pas de « Tiggo 4 de 2010 »
  await page.getByLabel("Année").selectOption(String(Math.max(...years)));
  await expect(page.getByText(/Chery Tiggo 4/)).toBeVisible(); // une seule motorisation : choisie d'office
});

test("code OBD-II impossible : message clair, sans jargon technique", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("Code défaut OBD-II (facultatif)").fill("P9999");
  await page.getByRole("button", { name: "Trouver la panne" }).click();
  const alert = page.getByRole("alert").filter({ hasText: "OBD-II" }); // pas l'annonceur de route vide de Next.js
  await expect(alert).toContainText("Code OBD-II invalide : P9999");
  await expect(alert).toContainText("de 0 à 3");
  await expect(alert).not.toContainText("Value error");
});

test("diagnostic et magasin inexistants : message juste, pas « le serveur ne répond pas »", async ({ page }) => {
  await page.goto("/diagnostic/999999");
  await expect(page.getByText("Ce diagnostic n'existe pas")).toBeVisible();
  await page.goto("/magasins/999999");
  await expect(page.getByText("Ce magasin n'existe pas")).toBeVisible();
  await expect(page.getByText("Le serveur ne répond pas")).toHaveCount(0);
});

test("page inconnue : 404 en français", async ({ page }) => {
  const res = await page.goto("/nimporte-quoi");
  expect(res?.status()).toBe(404);
  await expect(page.getByRole("heading", { name: "Page introuvable" })).toBeVisible();
  await expect(page.getByText("could not be found")).toHaveCount(0);
});

test("magasin fictif : aucun numéro dans les liens d'appel et de WhatsApp", async ({ page }) => {
  await page.goto("/pieces");
  await page.getByLabel("Nom de la pièce").fill("amortisseur");
  await page.getByRole("button", { name: "Voir les magasins" }).first().click();
  const demo = page.locator(".shop", { has: page.locator(".tag-demo") }).first();
  await expect(demo).toBeVisible();
  for (const name of ["Appeler", "WhatsApp"]) {
    const href = (await demo.getByRole("link", { name }).getAttribute("href")) ?? "";
    expect(href).not.toMatch(/\d{6,}/);
  }
});
