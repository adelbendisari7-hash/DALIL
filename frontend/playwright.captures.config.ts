// Captures d'écran pour la revue de design (format téléphone, clair et sombre), sur les serveurs et la base des
// tests de bout en bout : aucun compte créé dans la vraie base. Sortie : test-results/captures/.
//   E2E_API_PORT=8100 E2E_WEB_PORT=3100 npx playwright test -c playwright.captures.config.ts
import { defineConfig } from "@playwright/test";
import base from "./playwright.config";

export default defineConfig({
  ...base,
  testDir: "./e2e-captures",
  projects: undefined,
  workers: 1,
});
