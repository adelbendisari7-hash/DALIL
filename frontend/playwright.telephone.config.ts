import { defineConfig, devices } from "@playwright/test";

/**
 * Vérification « comme sur un téléphone » (docs/test-telephone.md), contre un DALIL déjà lancé :
 *   TEL_URL=http://192.168.1.20:3000 npx playwright test -c playwright.telephone.config.ts
 * Options : TEL_SHOTS (dossier des captures), TEL_API_LOG (journal de l'API, pour lire le code SMS « console »),
 * TEL_LENT=0 (sans réseau 3G ni processeur ralenti).
 * Le parcours écrit dans la base de l'instance visée (diagnostics, « pièce trouvée ») : viser une copie, pas la vraie base.
 */
export default defineConfig({
  testDir: "./e2e-telephone",
  timeout: 300_000,
  workers: 1,
  reporter: [["list"]],
  use: {
    ...devices["Pixel 5"],
    baseURL: process.env.TEL_URL || "http://localhost:3000",
    viewport: { width: 360, height: 780 },   // Android d'entrée de gamme (Galaxy A, Redmi)
    hasTouch: true,
    isMobile: true,
    locale: "fr-FR",
    geolocation: { latitude: 35.6971, longitude: -0.6308 },   // centre d'Oran
    permissions: ["geolocation"],
  },
});
