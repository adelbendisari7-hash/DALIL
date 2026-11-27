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

test("description en darija : DALIL dit ce qu'il a compris et propose des causes", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("Décrivez le problème").fill("el moteur ysakhen bezaf f la route");
  await page.getByRole("button", { name: "Trouver la panne" }).click();
  await expect(page.getByText("Nous avons compris :")).toBeVisible();
  await expect(page.getByText(/chauffe/).first()).toBeVisible();
  await expect(page.getByRole("heading", { name: "Causes probables" })).toBeVisible();
});

test("question sans panne en darija : je ne sais pas", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("Décrivez le problème").fill("chhal soum el gasoil lyoum");
  await page.getByRole("button", { name: "Trouver la panne" }).click();
  await expect(page.getByRole("heading", { name: "Panne non identifiée" })).toBeVisible();
});

test("recherche du véhicule par saisie : « clio 2 » choisit la marque et le modèle", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("Rechercher votre voiture").fill("clio 2");
  await page.getByRole("option", { name: "Renault Clio 2" }).click();
  await expect(page.getByLabel("Marque")).toHaveValue(/\d+/);
  await expect(page.getByLabel("Modèle", { exact: true }).locator("option:checked")).toHaveText("Clio 2");
  await expect.poll(() => page.getByLabel("Année").locator("option").count()).toBeGreaterThan(1);
  const years = (await page.getByLabel("Année").locator("option").allTextContents()).map(Number).filter(Boolean);
  expect(Math.max(...years)).toBeLessThanOrEqual(2008); // Clio 2 : années 1998 à 2006 environ
});

test("véhicule absent de la liste : la saisie est envoyée", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Mon véhicule n'est pas dans la liste" }).click();
  await page.getByLabel("Marque", { exact: true }).last().fill("Zastava");
  await page.getByLabel("Modèle", { exact: true }).last().fill("Yugo");
  await page.getByRole("button", { name: "Envoyer" }).click();
  await expect(page.getByText("Merci, votre véhicule sera ajouté.")).toBeVisible();
});

test("exemple touché : la description se remplit et le résultat peut être envoyé au mécanicien", async ({ page, context }) => {
  await context.grantPermissions(["clipboard-read", "clipboard-write"]).catch(() => undefined);
  await page.goto("/");
  await page.getByRole("button", { name: "Ça grince quand je freine" }).click();
  await expect(page.getByLabel("Décrivez le problème")).toHaveValue("Ça grince quand je freine");
  await expect(page.getByRole("button", { name: "Ça grince quand je freine" })).toHaveCount(0); // exemples masqués
  await page.getByRole("button", { name: "Trouver la panne" }).click();
  await expect(page.getByRole("heading", { name: "Causes probables" })).toBeVisible({ timeout: 60_000 });
  await expect(page.getByRole("button", { name: "Envoyer à mon mécanicien" })).toBeVisible();
});

test("API qui charge encore ses modèles : l'accueil dit que DALIL se prépare", async ({ page }) => {
  await page.route("**/api/v1/health", (route) => route.fulfill({ json: { status: "ok", ready: false } }));
  await page.goto("/");
  await expect(page.getByText("DALIL se prépare")).toBeVisible();
  await page.unroute("**/api/v1/health");
  await expect(page.getByText("DALIL se prépare")).toHaveCount(0, { timeout: 10_000 }); // l'API répond « prête »
});

test("diagnostic faux : l'utilisateur dit quelle pièce était en cause", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("Décrivez le problème").fill("la voiture ne démarre pas le matin, le démarreur tourne lentement");
  await page.getByRole("button", { name: "Trouver la panne" }).click();
  await expect(page.getByRole("heading", { name: "Causes probables" })).toBeVisible({ timeout: 60_000 });
  await page.getByRole("button", { name: "Non", exact: true }).click();
  const send = page.getByRole("button", { name: "Envoyer", exact: true });
  await expect(send).toBeDisabled(); // pas de pièce choisie
  await page.getByRole("button", { name: "Une autre pièce…" }).click();
  await expect(page.getByLabel("Choisir dans la liste").locator("option")).not.toHaveCount(1); // liste chargée
  await page.getByLabel("Choisir dans la liste").selectOption({ label: "Batterie" });
  await page.getByLabel("Ce que le mécanicien a trouvé (facultatif)").fill("batterie changée");
  const posted = page.waitForRequest((r) => r.url().endsWith("/api/v1/feedback") && r.method() === "POST");
  await send.click();
  const body = (await posted).postDataJSON();
  expect(body).toMatchObject({ diagnosis_correct: false, comment: "batterie changée" });
  expect(typeof body.category_id).toBe("number");
  await expect(page.getByText("Merci, votre réponse améliore DALIL.")).toBeVisible();
});

test("voyant touché : description remplie, conseil de sûreté immédiat pour l'huile, diagnostic « ne roulez pas »", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Pression d'huile" }).click();
  await expect(page.getByRole("button", { name: "Pression d'huile" })).toHaveAttribute("aria-pressed", "true");
  await expect(page.getByLabel("Décrivez le problème")).toHaveValue("le voyant de pression d'huile rouge s'est allumé");
  await expect(page.getByRole("alert").filter({ hasText: "arrêtez-vous dès que possible" })).toBeVisible();
  await page.getByRole("button", { name: "Batterie", exact: true }).click();
  await expect(page.getByLabel("Décrivez le problème")).toHaveValue(/huile.*, le voyant batterie rouge/);
  await page.getByRole("button", { name: "Batterie", exact: true }).click();   // retiré : la phrase disparaît
  await expect(page.getByLabel("Décrivez le problème")).toHaveValue("le voyant de pression d'huile rouge s'est allumé");
  await page.getByRole("button", { name: "Trouver la panne" }).click();
  await expect(page.getByRole("heading", { name: "Causes probables" })).toBeVisible({ timeout: 60_000 });
  await expect(page.getByRole("alert").filter({ hasText: "Ne roulez pas" })).toBeVisible();
});
