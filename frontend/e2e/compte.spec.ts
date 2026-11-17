import { expect, test } from "@playwright/test";
import { OTP } from "./helpers";

/** Suppression du compte sur demande (loi 18-07, section 10) : promise à la connexion, faisable depuis le site. */
test("un utilisateur supprime son compte depuis « Mon compte »", async ({ page }) => {
  await page.goto("/connexion?next=/compte");
  await page.getByLabel("Numéro de mobile").fill("0555987654");
  await page.getByRole("button", { name: "Recevoir le code" }).click();
  await page.getByLabel("Code reçu par SMS").fill(OTP);
  await page.getByRole("checkbox").check();
  await page.getByRole("button", { name: "Me connecter" }).click();

  await expect(page.getByRole("heading", { name: "Mon compte", exact: true })).toBeVisible();
  await expect(page.getByText("+213555987654")).toBeVisible();
  await expect(page.getByRole("link", { name: "Mon compte", exact: true })).toBeVisible(); // menu : connecté

  page.once("dialog", (d) => d.accept()); // confirmation « action définitive »
  await page.getByRole("button", { name: "Supprimer mon compte" }).click();
  await expect(page.getByText("Votre compte a été supprimé.")).toBeVisible();
  await expect(page.getByRole("link", { name: "Connexion" })).toBeVisible(); // menu : déconnecté
  expect(await page.evaluate(() => localStorage.getItem("dalil.token"))).toBeNull();
});
