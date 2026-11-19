import { expect, test } from "@playwright/test";

/** Parcours principal de l'automobiliste (section 2), critère de l'étape 9. */
test("panne décrite -> causes -> magasins -> contact -> pièce trouvée", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toContainText("Qu'est-ce qui ne va pas");

  // 1. Véhicule
  await page.getByLabel("Marque").selectOption({ label: "Dacia" });
  await page.getByLabel("Modèle").selectOption({ label: "Logan" });
  await page.getByLabel("Année").selectOption("2015");
  await page.getByLabel("Motorisation").selectOption({ label: "1.5 dCi (diesel, 2013–2020)" });
  await expect(page.getByText("Dacia Logan 1.5 dCi 2015")).toBeVisible();

  // 2. Description de la panne
  await page.getByLabel("Décrivez le problème").fill("ça grince fort quand je freine, bruit de métal");
  await page.getByRole("button", { name: "Trouver la panne" }).click();

  // 4. Causes classées, consigne de sûreté, étiquette de pièce
  await expect(page.getByRole("heading", { name: "Causes probables" })).toBeVisible();
  await expect(page.getByRole("alert").first()).toContainText("Ne roulez pas");
  const label = page.locator(".part-label").first();
  await expect(label).toContainText("Plaquettes de frein avant");
  await expect(label).toContainText("FICTIF-PL-001"); // référence lue en base (pilote, donnée fictive)

  // 5. Magasins classés avec raisons
  await label.getByRole("link", { name: "Voir les magasins" }).click();
  await expect(page.getByRole("heading", { level: 1 })).toContainText("plaquettes de frein avant");
  const first = page.locator(".shop").first();
  await expect(first).toContainText("a la pièce au catalogue");
  await expect(first).toContainText("vend Dacia");

  // 6. Contact (magasin fictif : lien bloqué) puis « pièce trouvée ? »
  await first.getByRole("link", { name: "WhatsApp" }).click();
  await expect(first.getByText("Ce magasin est fictif")).toBeVisible();
  await first.getByRole("button", { name: "Oui, trouvée" }).click();
  await expect(first.getByText("Merci. Votre réponse aide")).toBeVisible();

  // Carte
  await page.getByRole("button", { name: "Carte" }).click();
  await expect(page.locator(".leaflet-marker-icon").first()).toBeVisible();
});

test("parcours direct du mécanicien", async ({ page }) => {
  await page.goto("/pieces");
  await page.getByLabel("Nom de la pièce").fill("amortisseur");
  await page.getByRole("button", { name: "Voir les magasins" }).first().click();
  await expect(page.getByRole("heading", { level: 1 })).toContainText("amortisseurs");
  await expect(page.locator(".shop").first()).toBeVisible();
});

test("entrée hors sujet : je ne sais pas", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("Décrivez le problème").fill("quel temps fera-t-il demain à Oran ?");
  await page.getByRole("button", { name: "Trouver la panne" }).click();
  await expect(page.getByRole("heading", { name: "Panne non identifiée" })).toBeVisible();
});

test("saisie vocale : la dictée remplit la zone de texte, puis diagnostic", async ({ page }) => {
  // Reconnaissance vocale factice (pas de micro en test) : elle « entend » une phrase au démarrage.
  await page.addInitScript(() => {
    class FakeRecognition {
      lang = "";
      interimResults = false;
      continuous = false;
      onresult: (e: unknown) => void = () => {};
      onend: () => void = () => {};
      onerror: () => void = () => {};
      start() {
        setTimeout(() => {
          this.onresult({ results: [[{ transcript: "ça grince fort quand je freine" }]] });
          this.onend();
        }, 50);
      }
      stop() {
        this.onend();
      }
    }
    // Chromium récent expose SpeechRecognition (prioritaire dans l'application) : remplacer les deux noms.
    const w = window as unknown as Record<string, unknown>;
    w.SpeechRecognition = FakeRecognition;
    w.webkitSpeechRecognition = FakeRecognition;
  });
  await page.goto("/");
  await page.getByRole("button", { name: "Dicter" }).click();
  await expect(page.getByLabel("Décrivez le problème")).toHaveValue("ça grince fort quand je freine");
  await expect(page.getByText("Relisez et corrigez le texte")).toBeVisible();
  await page.getByRole("button", { name: "Trouver la panne" }).click();
  await expect(page.getByRole("heading", { name: "Causes probables" })).toBeVisible();
});

test("saisie vocale absente du navigateur : message clair", async ({ page }) => {
  await page.addInitScript(() => {
    const w = window as unknown as Record<string, unknown>;
    delete w.SpeechRecognition;
    delete w.webkitSpeechRecognition;
  });
  await page.goto("/");
  await expect(page.getByText("La dictée n'est pas disponible sur ce navigateur")).toBeVisible();
});

test("le site est installable", async ({ page, request }) => {
  const res = await request.get("/manifest.webmanifest");
  expect((await res.json()).display).toBe("standalone");
  await page.goto("/");
  await expect(page.locator('link[rel="manifest"]')).toHaveCount(1);
});

test("écran de 360 px : aucune page ne déborde en largeur (section 10)", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 740 });
  const noOverflow = async (what: string) => {
    await page.waitForLoadState("networkidle");
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    expect(overflow, `débordement horizontal : ${what}`).toBeLessThanOrEqual(0);
  };
  for (const path of ["/", "/pieces", "/connexion", "/espace-magasin"]) {
    await page.goto(path);
    await noOverflow(path);
  }
  // Pages à contenu : résultat de diagnostic, liste de magasins, fiche magasin
  await page.goto("/");
  await page.getByLabel("Décrivez le problème").fill("ça grince fort quand je freine, bruit de métal");
  await page.getByRole("button", { name: "Trouver la panne" }).click();
  await expect(page.getByRole("heading", { name: "Causes probables" })).toBeVisible();
  await noOverflow("résultat du diagnostic");
  await page.locator(".part-label").first().getByRole("link", { name: "Voir les magasins" }).click();
  await expect(page.locator(".shop").first()).toBeVisible();
  await noOverflow("liste des magasins");
  await page.locator(".shop").first().getByRole("link").first().click();
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  await noOverflow("fiche magasin");
});

test("saisie vocale refusée par le navigateur : message clair, pas de silence", async ({ page }) => {
  // Sur un téléphone, le micro peut être refusé (réglages, adresse non sécurisée) : l'utilisateur doit le savoir.
  await page.addInitScript(() => {
    class DeniedRecognition {
      lang = "";
      interimResults = false;
      continuous = false;
      onresult: (e: unknown) => void = () => {};
      onend: () => void = () => {};
      onerror: (e: { error: string }) => void = () => {};
      start() {
        setTimeout(() => {
          this.onerror({ error: "not-allowed" });
          this.onend();
        }, 50);
      }
      stop() {}
    }
    const w = window as unknown as Record<string, unknown>;
    w.SpeechRecognition = DeniedRecognition;
    w.webkitSpeechRecognition = DeniedRecognition;
  });
  await page.goto("/");
  await page.getByRole("button", { name: "Dicter" }).click();
  await expect(page.getByRole("alert").filter({ hasText: "Le micro n'est pas autorisé" })).toBeVisible();
  await expect(page.getByText("Relisez et corrigez le texte")).toHaveCount(0);
});
