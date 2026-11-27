import { expect, test, type APIRequestContext } from "@playwright/test";
import { ADMIN_PHONE, OTP } from "./helpers";

/** « Mes demandes » : un client sans compte demande une pièce aux magasins et voit leurs réponses (prix, dispo). */

async function adminToken(request: APIRequestContext) {
  await request.post("/api/v1/auth/otp/request", { data: { phone: ADMIN_PHONE } });
  return (await (await request.post("/api/v1/auth/otp/verify", { data: { phone: ADMIN_PHONE, code: OTP } })).json()).token as string;
}

test("demande aux magasins sans compte : suivie, puis réponse avec le prix", async ({ page, request }) => {
  const stamp = String(Date.now()).slice(-6);
  const auth = (tk: string) => ({ Authorization: `Bearer ${tk}` });
  // Un magasin validé, géré, qui vend le freinage : il reçoit les demandes de plaquettes
  const gerant = (await (await request.post("/api/v1/auth/register", { data: { first_name: "Gérant", last_name: "Demandes",
    phone: `0552${stamp}`, password: "demandes-e2e", consent: true } })).json()).token as string;
  await request.patch("/api/v1/auth/me", { headers: auth(gerant), data: { role: "shop_owner" } });
  const cats = await (await request.get("/api/v1/parts/categories")).json();
  const freinage = cats.find((f: { slug: string }) => f.slug === "freinage");
  const plaquettes = freinage.children.find((c: { slug: string }) => c.slug === "plaquettes-avant");
  const shop = await (await request.post("/api/v1/shops", { headers: auth(gerant),
    data: { name: `[TEST] Freins ${stamp}`, lat: 35.70, lng: -0.63, category_ids: [freinage.id], brand_ids: [] } })).json();
  await request.post(`/api/v1/admin/shops/${shop.id}/verify`, { headers: auth(await adminToken(request)),
    data: { phone_ok: true, address_ok: true, activity_ok: true } });

  // Le client demande la pièce depuis la liste des magasins, puis suit sa demande
  await page.goto(`/magasins?category=${plaquettes.id}&part=${encodeURIComponent("Plaquettes de frein avant")}`);
  await page.getByRole("button", { name: "Demander aux magasins" }).click();
  await expect(page.getByText("Demande envoyée", { exact: false })).toBeVisible();
  await page.getByRole("link", { name: "Suivre ma demande" }).click();
  await expect(page.getByRole("heading", { name: "Mes demandes" })).toBeVisible();
  await expect(page.getByText("Les magasins n'ont pas encore répondu.")).toBeVisible();

  // Le magasin répond « disponible, 4 300 DA »
  const inbox = await (await request.get("/api/v1/part-requests/inbox", { headers: auth(gerant) })).json();
  const mine = inbox.find((r: { shop_id: number }) => r.shop_id === shop.id);
  await request.post(`/api/v1/part-requests/${mine.request_id}/responses?shop_id=${shop.id}`, { headers: auth(gerant),
    data: { available: true, price: 4300 } });

  await page.reload();
  const answer = page.locator(".answer", { hasText: `[TEST] Freins ${stamp}` });
  await expect(answer.getByText(/4.300 DA/)).toBeVisible();
  await expect(answer.getByRole("link", { name: "Appeler" })).toBeVisible();
});

test("demande avec la photo de la pièce : visible dans « Mes demandes »", async ({ page }) => {
  await page.goto("/pieces");
  await page.getByLabel("Nom de la pièce").fill("plaquettes");
  await page.getByRole("button", { name: "Voir les magasins" }).first().click();
  await expect(page.locator(".shop").first()).toBeVisible();
  // Une vraie image JPEG, dessinée par le navigateur
  const b64 = await page.evaluate(() => {
    const c = document.createElement("canvas");
    c.width = 200; c.height = 120;
    const g = c.getContext("2d")!;
    g.fillStyle = "#c33"; g.fillRect(0, 0, 200, 120);
    return c.toDataURL("image/jpeg").split(",")[1];
  });
  await page.locator(".request-box input[type=file]").setInputFiles({ name: "piece.jpg", mimeType: "image/jpeg", buffer: Buffer.from(b64, "base64") });
  await expect(page.getByRole("img", { name: "Photo de la pièce jointe à la demande" })).toBeVisible();
  await page.getByRole("button", { name: "Demander aux magasins" }).click();
  await expect(page.locator(".request-box [role=status]")).toBeVisible();   // demande partie
  await page.goto("/demandes");   // suivie depuis ce téléphone, même sans compte
  const photo = page.locator(".request-photo img").first();
  await expect(photo).toBeVisible();
  await expect(photo).toHaveAttribute("src", /\/api\/v1\/media\/demandes\//);
});
