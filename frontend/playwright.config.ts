import { existsSync } from "node:fs";
import { resolve } from "node:path";
import { defineConfig, devices } from "@playwright/test";

// Python du backend : variable PYTHON si elle est donnée, sinon l'environnement backend/.venv s'il existe
// (portable), sinon « python » (intégration continue). Chemin rendu absolu et entre guillemets : la commande
// s'exécute dans ../backend, et l'invite de commandes Windows ne comprend pas « ../backend/... ».
const VENV = resolve(__dirname, "../backend/.venv", process.platform === "win32" ? "Scripts/python.exe" : "bin/python");
const PY_RAW = process.env.PYTHON ? resolve(process.env.PYTHON) : existsSync(VENV) ? VENV : "python";
const PY = PY_RAW === "python" ? PY_RAW : `"${PY_RAW}"`;
const E2E_DB = "sqlite:///./e2e.db";
// Ports et dossier de construction à part (E2E_API_PORT, E2E_WEB_PORT) : les tests tournent même quand DALIL est
// lancé sur le portable (3000 et 8000), sans toucher au dossier .next du serveur de développement.
const API_PORT = process.env.E2E_API_PORT || "8000";
const WEB_PORT = process.env.E2E_WEB_PORT || "3000";
const DIST = ".next-e2e";
const WEB_ENV = { NEXT_DIST_DIR: DIST, DALIL_API_INTERNAL: `http://127.0.0.1:${API_PORT}` };

export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  retries: process.env.CI ? 1 : 0,
  use: { baseURL: `http://localhost:${WEB_PORT}`, trace: "retain-on-failure", ...devices["Pixel 5"] },
  projects: [{ name: "mobile-chromium", use: { ...devices["Pixel 5"] } }],
  webServer: [
    {
      command: `${PY} -c "import pathlib; pathlib.Path('e2e.db').unlink(missing_ok=True)" && ${PY} -m alembic upgrade head && ${PY} -m app.seed && ${PY} -m uvicorn app.main:app --port ${API_PORT}`,
      cwd: "../backend",
      url: `http://localhost:${API_PORT}/health`,
      env: { DALIL_DATABASE_URL: E2E_DB, DALIL_ADMIN_PHONES: "0550000099", DALIL_OTP_RATE_PER_MINUTE: "100" },
      reuseExistingServer: false,
      timeout: 120_000,
    },
    {
      // Toujours reconstruit : le relais vers l'API (next.config.mjs) est figé à la construction, avec le port de l'API.
      command: `npx next build && npx next start -p ${WEB_PORT}`,
      url: `http://localhost:${WEB_PORT}`,
      env: WEB_ENV,
      // Pas de NEXT_PUBLIC_API_URL : le site joint l'API par son relais (next.config.mjs), comme sur un téléphone.
      reuseExistingServer: false,
      timeout: 300_000,
    },
  ],
});
