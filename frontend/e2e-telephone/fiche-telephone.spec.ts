import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { type CDPSession, type Page, expect, test } from "@playwright/test";

/**
 * La fiche docs/test-telephone.md, déroulée sur un téléphone simulé : 360 px, tactile, réseau 3G et processeur 4 fois
 * plus lent (TEL_LENT=0 pour les retirer). Chaque constat est noté (expect.soft) sans arrêter le parcours ; les mesures
 * et constats sont écrits dans TEL_SHOTS/rapport.json, avec une capture de chaque écran.
 */
const SHOTS = process.env.TEL_SHOTS || "test-results/telephone";
const SLOW = process.env.TEL_LENT !== "0";
const report: Record<string, unknown> = { url: process.env.TEL_URL, lent: SLOW, mesures: {}, constats: [] as string[] };
const mesures = report.mesures as Record<string, unknown>;
const constats = report.constats as string[];

async function slowDown(page: Page): Promise<CDPSession | null> {
  if (!SLOW) return null;
  const cdp = await page.context().newCDPSession(page);
  await cdp.send("Network.enable");
  // « Fast 3G » des outils de Chrome : 1,6 Mbit/s descendant, 750 kbit/s montant, 150 ms de latence (x 3,75 côté requête)
  await cdp.send("Network.emulateNetworkConditions", {
    offline: false, latency: 562, downloadThroughput: (1.6 * 1024 * 1024) / 8, uploadThroughput: (750 * 1024) / 8,
  });
  await cdp.send("Emulation.setCPUThrottlingRate", { rate: 4 });
  return cdp;
}

async function shot(page: Page, name: string) {
  mkdirSync(SHOTS, { recursive: true });
  await page.screenshot({ path: join(SHOTS, `${name}.png`), fullPage: true });
}

/** Défilement horizontal, cibles tactiles trop petites, champs qui font zoomer (police < 16 px). */
async function ergonomie(page: Page, ecran: string) {
  const r = await page.evaluate(() => {
    const visible = (el: Element) => {
      const b = el.getBoundingClientRect();
      const s = getComputedStyle(el);
      return b.width > 0 && b.height > 0 && s.visibility !== "hidden" && s.display !== "none";
    };
    const label = (el: Element) => ((el as HTMLElement).innerText || el.getAttribute("aria-label") || (el as HTMLInputElement).placeholder || el.tagName).trim().slice(0, 40);
    const small = [...document.querySelectorAll("a, button, select, input:not([type=hidden]), [role=option]")]
      .filter(visible)
      .filter((el) => !el.closest(".leaflet-control-attribution"))
      .map((el) => ({ el, b: el.getBoundingClientRect() }))
      .filter(({ el, b }) => {
        const inline = el.tagName === "A" && getComputedStyle(el).display === "inline";   // lien dans une phrase
        return !inline && (b.height < 40 || b.width < 40);
      })
      .map(({ el, b }) => `${label(el)} (${Math.round(b.width)}x${Math.round(b.height)})`);
    const zoom = [...document.querySelectorAll("input, select, textarea")].filter(visible)
      .filter((el) => parseFloat(getComputedStyle(el).fontSize) < 16).map(label);
    return { overflow: document.documentElement.scrollWidth - window.innerWidth, small, zoom };
  });
  expect.soft(r.overflow, `${ecran} : défilement horizontal`).toBeLessThanOrEqual(0);
  if (r.overflow > 0) constats.push(`${ecran} : déborde de ${r.overflow} px en largeur`);
  if (r.small.length) constats.push(`${ecran} : cibles tactiles < 40 px : ${[...new Set(r.small)].slice(0, 8).join(" ; ")}`);
  if (r.zoom.length) constats.push(`${ecran} : champs en police < 16 px (zoom automatique sur iPhone) : ${r.zoom.join(" ; ")}`);
}

/** Glisser d'un doigt sur un élément (événements tactiles réels via le protocole de Chrome), depuis un coin vide
 *  (bas à gauche, loin des marqueurs et des boutons de zoom), à la vitesse d'un doigt. */
async function swipe(page: Page, selector: string, dx: number, dy: number) {
  await page.locator(selector).first().scrollIntoViewIfNeeded();
  const b = (await page.locator(selector).first().boundingBox())!;
  const vh = page.viewportSize()!.height;
  const cdp = await page.context().newCDPSession(page);
  // le doigt doit se poser dans l'écran visible : bas de la carte, ou bas de l'écran si la carte dépasse
  const x = b.x + 40, y = Math.max(b.y + 60, Math.min(b.y + b.height - 60, vh - 80));
  await cdp.send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: [{ x, y }] });
  for (let i = 1; i <= 8; i++) {
    await cdp.send("Input.dispatchTouchEvent", { type: "touchMove", touchPoints: [{ x: x + (dx * i) / 8, y: y + (dy * i) / 8 }] });
    await page.waitForTimeout(16);
  }
  await cdp.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
  await cdp.detach();
}

// Après chaque test (un échec relance le processus et vide les variables) : fusion avec le rapport déjà écrit.
test.afterEach(() => {
  mkdirSync(SHOTS, { recursive: true });
  const path = join(SHOTS, "rapport.json");
  const old = existsSync(path) ? JSON.parse(readFileSync(path, "utf-8")) : { mesures: {}, constats: [] };
  const merged = { ...report, mesures: { ...old.mesures, ...mesures },
                   constats: [...new Set([...(old.constats || []), ...constats])] };
  writeFileSync(path, JSON.stringify(merged, null, 2), "utf-8");
});

test("automobiliste : accueil, véhicule, diagnostic, magasins, carte, contact, pièce trouvée", async ({ page }) => {
  await slowDown(page);
  // Accueil : premier chargement (cache vide, comme un premier passage)
  let t0 = Date.now();
  const resp = await page.goto("/", { waitUntil: "load" });
  mesures.accueil_premier_chargement_s = (Date.now() - t0) / 1000;
  expect(resp?.ok()).toBeTruthy();
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  mesures.accueil_octets = await page.evaluate(() =>
    performance.getEntriesByType("resource").reduce((s, e) => s + ((e as PerformanceResourceTiming).transferSize || 0), 0)
    + ((performance.getEntriesByType("navigation")[0] as PerformanceResourceTiming)?.transferSize || 0));
  await shot(page, "01-accueil");
  await ergonomie(page, "accueil");
  t0 = Date.now();
  await page.reload({ waitUntil: "load" });
  mesures.accueil_second_chargement_s = (Date.now() - t0) / 1000;

  // Véhicule : recherche « logan », puis année et motorisation, au doigt
  const search = page.getByLabel("Rechercher votre voiture");
  await search.tap();
  await search.fill("logan");
  const hit = page.getByRole("option").filter({ hasText: "Logan" }).first();
  await expect.soft(hit, "recherche de véhicule : « logan » trouvé").toBeVisible({ timeout: 30_000 });
  if (await hit.isVisible()) await hit.tap();
  else await page.getByLabel("Marque").selectOption({ label: "Dacia" });
  await page.getByLabel("Modèle").selectOption({ label: "Logan" }).catch(() => {});
  await page.getByLabel("Année").selectOption("2015");
  const motor = page.getByLabel("Motorisation");
  await expect(motor.locator("option", { hasText: "1.5 dCi" }).first()).toBeAttached({ timeout: 30_000 });   // liste chargée en 3G
  const dci = await motor.locator("option", { hasText: "1.5 dCi" }).first().getAttribute("value");
  if (dci) await motor.selectOption(dci, { timeout: 15_000 });
  await shot(page, "02-vehicule");
  await ergonomie(page, "choix du véhicule");

  // Diagnostic : progression visible, temps de réponse (exigence : moins de 10 s)
  const box = page.getByLabel("Décrivez le problème");
  await box.tap();
  await box.fill("ça grince fort quand je freine");
  t0 = Date.now();
  await page.getByRole("button", { name: "Trouver la panne" }).tap();
  const busy = page.getByText("Analyse en cours…");
  const sawProgress = await busy.isVisible().catch(() => false) || await busy.waitFor({ timeout: 1500 }).then(() => true, () => false);
  await expect(page.getByRole("heading", { name: "Causes probables" })).toBeVisible({ timeout: 120_000 });
  mesures.diagnostic_s = (Date.now() - t0) / 1000;
  if (!sawProgress) constats.push("diagnostic : l'indicateur « Analyse en cours… » n'a pas été vu");
  if ((mesures.diagnostic_s as number) > 10) constats.push(`diagnostic : ${mesures.diagnostic_s} s (exigence : moins de 10 s)`);
  await expect.soft(page.getByText("Dacia Logan"), "le véhicule choisi est rappelé sur le résultat").toBeVisible();
  const firstAlert = page.getByRole("alert").first();
  await expect.soft(firstAlert, "« Ne roulez pas » en premier").toContainText("Ne roulez pas");
  await expect.soft(page.getByText("aide au diagnostic, pas un diagnostic certifié"), "mention « aide, pas diagnostic certifié »").toBeVisible();
  const label = page.locator(".part-label").first();
  await expect.soft(label, "pièce proposée").toContainText("Plaquettes");
  await shot(page, "03-diagnostic");
  await ergonomie(page, "résultat du diagnostic");

  // Magasins : raisons du classement
  t0 = Date.now();
  await label.getByRole("link", { name: "Voir les magasins" }).tap();
  const shop = page.locator(".shop").first();
  await expect(shop).toBeVisible({ timeout: 60_000 });
  mesures.magasins_s = (Date.now() - t0) / 1000;
  await expect.soft(shop, "raison du classement affichée").toContainText(/vend|catalogue|km/);
  await shot(page, "04-magasins");
  await ergonomie(page, "liste des magasins");

  // Contact WhatsApp d'un magasin de démonstration, puis « pièce trouvée ? »
  const demo = page.locator(".shop").filter({ hasText: "[DÉMO]" }).first();
  if (await demo.count()) {
    await demo.getByRole("link", { name: "WhatsApp" }).tap();
    await expect.soft(demo.getByText("Ce magasin est fictif"), "WhatsApp d'un magasin [DÉMO] : « fictif »").toBeVisible();
    await demo.getByRole("button", { name: "Oui, trouvée" }).tap();
    await expect.soft(demo.getByText("Merci. Votre réponse aide"), "« pièce trouvée » enregistrée").toBeVisible();
  } else constats.push("magasins : aucun magasin [DÉMO] dans la liste");

  // Carte : déplacement au doigt
  await page.getByRole("button", { name: "Carte" }).tap();
  await expect(page.locator(".leaflet-marker-icon").first()).toBeVisible({ timeout: 60_000 });
  const pane = page.locator(".leaflet-map-pane");
  const before = await pane.getAttribute("style");
  await swipe(page, ".leaflet-container", 120, -60);
  await page.waitForTimeout(800);
  const after = await pane.getAttribute("style");
  expect.soft(after, "la carte se déplace au doigt").not.toBe(before);
  if (after === before) constats.push("carte : ne bouge pas quand on la fait glisser au doigt");
  await shot(page, "05-carte");
  await ergonomie(page, "carte");
});

test("darija, dictée sur l'adresse du PC (non sécurisée), installation", async ({ page }) => {
  await slowDown(page);
  await page.goto("/");
  await page.getByLabel("Décrivez le problème").fill("el frein ysoni ki nfreini");
  await page.getByRole("button", { name: "Trouver la panne" }).tap();
  await expect(page.getByRole("heading", { name: "Causes probables" })).toBeVisible({ timeout: 120_000 });
  await expect.soft(page.getByText("Nous avons compris"), "darija : « Nous avons compris : … »").toBeVisible();
  await shot(page, "06-darija");

  // Dictée : sur http://<adresse du PC>, Chrome refuse le micro. Que voit l'utilisateur ?
  await page.goto("/");
  const secure = await page.evaluate(() => window.isSecureContext);
  const dicter = page.getByRole("button", { name: "Dicter" });
  mesures.contexte_securise = secure;
  const explained = page.getByText("La dictée demande une adresse sécurisée");
  await page.waitForLoadState("networkidle");   // le composant décide après hydratation (lente en 3G)
  await expect(explained.or(dicter)).toBeVisible({ timeout: 60_000 });
  await page.waitForTimeout(1000);
  if (!secure && (await explained.isVisible())) {
    mesures.dictee_apres_appui = "adresse non sécurisée : message affiché, pas de bouton inutile";
    await shot(page, "07-dictee");
  } else if (await dicter.isVisible()) {
    await dicter.tap();
    await page.waitForTimeout(2500);
    const voiceText = await page.locator("form").first().innerText();
    mesures.dictee_apres_appui = voiceText.split("\n").filter((l) => /dict|écoute|micro|disponible/i.test(l));
    await shot(page, "07-dictee");
    if (!/micro|autoris|disponible|https|sécurisée/i.test(voiceText)) {
      constats.push(`dictée (${secure ? "contexte sécurisé" : "adresse non sécurisée"}) : après l'appui sur « Dicter », aucun message n'explique pourquoi rien ne se passe`);
    }
  } else {
    mesures.dictee_apres_appui = "bouton absent : " + (await page.getByText("La dictée n'est pas disponible").isVisible());
  }

  // Installation : manifeste et service worker
  const manifest = await page.evaluate(async () => (await fetch("/manifest.webmanifest")).ok);
  const sw = await page.evaluate(async () => "serviceWorker" in navigator && !!(await navigator.serviceWorker.getRegistration()));
  mesures.installation = { manifeste: manifest, service_worker: sw, contexte_securise: secure };
});

test("mécanicien et magasin : chercher une pièce, se connecter", async ({ page }) => {
  await slowDown(page);
  let t0 = Date.now();
  await page.goto("/pieces");
  await page.getByLabel("Nom de la pièce").fill("amortisseur");
  await page.getByRole("button", { name: "Voir les magasins" }).first().tap();
  await expect(page.getByRole("heading", { level: 1 })).toContainText("amortisseurs", { timeout: 60_000 });
  await shot(page, "08-mecanicien");
  await ergonomie(page, "recherche de pièce");

  await page.goto("/connexion?next=/espace-magasin");
  await ergonomie(page, "connexion");
  await page.getByLabel("Numéro de mobile").fill("0550000000");
  await page.getByRole("button", { name: "Recevoir le code" }).tap();
  await expect.soft(page.getByRole("note"), "connexion : message « mode démonstration »").toContainText("DALIL - API");
  await shot(page, "09-connexion");
  const log = process.env.TEL_API_LOG;
  if (log && existsSync(log)) {
    await page.waitForTimeout(1000);
    const codes = [...readFileSync(log, "utf-8").matchAll(/\+213550000000 : DALIL : votre code est (\d{6})/g)];
    if (codes.length) {
      await page.getByLabel("Code reçu par SMS").fill(codes[codes.length - 1][1]);
      await page.getByRole("checkbox").check();
      await page.getByRole("button", { name: "Me connecter" }).tap();
      t0 = Date.now();
      await expect.soft(page, "connexion réussie, retour à l'espace magasin")
        .toHaveURL((u) => u.pathname.startsWith("/espace-magasin"), { timeout: 60_000 });
      mesures.connexion_s = (Date.now() - t0) / 1000;
      if (new URL(page.url()).pathname.startsWith("/connexion")) {
        const err = await page.locator(".err").textContent().catch(() => null);
        constats.push(`connexion : toujours sur la page de connexion après 60 s${err ? " (" + err + ")" : ""}`);
      }
      const dacia = page.getByRole("button", { name: "Dacia", exact: true });
      await expect.soft(dacia, "espace magasin : marques proposées").toBeVisible({ timeout: 60_000 });
      await expect.soft(page.getByRole("button", { name: "Freinage", exact: true }), "espace magasin : familles proposées").toBeVisible();
      mesures.espace_magasin_listes_s = (Date.now() - t0) / 1000;
      await shot(page, "10-espace-magasin");
      await ergonomie(page, "espace magasin");
    } else constats.push("connexion : code introuvable dans le journal de l'API");
  }
});
