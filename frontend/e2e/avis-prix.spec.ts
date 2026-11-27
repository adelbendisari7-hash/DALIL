import { expect, test, type Page } from "@playwright/test";

/** Deuxième série d'améliorations (28/11/2026) : avis vérifiés sur la fiche, historique des prix, dernier diagnostic
 * relisible sans réseau. */

async function diagnostic(page: Page) {
  await page.goto("/");
  await page.getByLabel("Marque").selectOption({ label: "Dacia" });
  await page.getByLabel("Modèle").selectOption({ label: "Logan" });
  await page.getByLabel("Année").selectOption("2015");
  await page.getByLabel("Motorisation").selectOption({ label: "1.5 dCi (diesel, 2013–2020)" });
  await page.getByLabel("Décrivez le problème").fill("ça grince fort quand je freine, bruit de métal");
  await page.getByRole("button", { name: "Trouver la panne" }).click();
  await expect(page.getByRole("heading", { name: "Causes probables" })).toBeVisible({ timeout: 60_000 });
}

test("contact puis « pièce trouvée » : avis vérifié sur la fiche ; prix de la pièce sous les magasins", async ({ page }) => {
  await diagnostic(page);
  await page.locator(".part-label").first().getByRole("link", { name: "Voir les magasins" }).click();
  const first = page.locator(".shop").first();
  await expect(first).toBeVisible();

  // Historique des prix : chiffres écrits, prix fictifs signalés comme tels (seuls des magasins de démo ont des prix)
  const prices = page.locator(".price-history");
  await expect(prices.getByRole("heading", { name: "Prix de cette pièce sur DALIL" })).toBeVisible();
  await expect(prices).toContainText("le moins cher aujourd'hui");
  await expect(prices).toContainText("Prix fictifs de démonstration");

  await first.getByRole("link", { name: "WhatsApp" }).click();
  await first.getByRole("button", { name: "Oui, trouvée" }).click();
  await expect(first.getByText("Merci. Votre réponse aide")).toBeVisible();

  await first.getByRole("heading").getByRole("link").click();
  const reviews = page.locator(".reviews");
  await expect(reviews.getByRole("heading", { name: "Avis vérifiés des clients" })).toBeVisible();
  await expect(reviews).toContainText(/trouvé (sa|leur) pièce ici/);
  await expect(reviews.locator("li").first()).toContainText("Plaquettes de frein avant · Dacia Logan");
  await expect(reviews.locator("li").first()).toContainText("aujourd'hui");
});

test.describe("sans service worker (téléphone en http)", () => {
  // Sur un téléphone en http, pas de service worker : c'est la mémoire de l'appareil qui sert
  test.use({ serviceWorkers: "block" });

test("réseau coupé : le dernier diagnostic et ses magasins se relisent, on peut encore appeler", async ({ page }) => {
  await diagnostic(page);
  const url = page.url();
  const cause = await page.locator(".cause h3").first().innerText();
  await page.locator(".part-label").first().getByRole("link", { name: "Voir les magasins" }).click();
  await expect(page.locator(".shop").first()).toBeVisible();
  const shopsUrl = page.url();
  const shopName = await page.locator(".shop h3 a").first().innerText();

  // L'API ne répond plus (3G coupée), le site reste ouvert
  await page.route("**/api/v1/**", (route) => route.abort("internetdisconnected"));
  await page.goto("/");
  const card = page.locator(".last-diagnosis");
  await expect(card).toContainText("Votre dernier diagnostic");
  await expect(card).toContainText(cause);
  await card.click();
  await expect(page).toHaveURL(url);
  await expect(page.getByText("Pas de réseau : voici ce diagnostic", { exact: false })).toBeVisible();
  await expect(page.locator(".cause h3").first()).toHaveText(cause);

  await page.goto(shopsUrl);
  await expect(page.getByText("Pas de réseau : magasins enregistrés", { exact: false })).toBeVisible();
  await expect(page.locator(".shop h3 a").first()).toHaveText(shopName);
  await expect(page.locator(".shop").first().getByRole("link", { name: /Appeler|WhatsApp/ }).first()).toBeVisible();

  // Un autre diagnostic, jamais ouvert sur ce téléphone : message clair
  await page.goto("/diagnostic/999999");
  await expect(page.getByText("Pas de réseau. Seul le dernier diagnostic", { exact: false })).toBeVisible();
});
});
