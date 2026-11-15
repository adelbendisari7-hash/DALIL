import { defineConfig, devices } from "@playwright/test";

// Python de l'environnement du backend (PYTHON=../backend/.venv/Scripts/python sous Windows).
const PY = process.env.PYTHON || "python";
const E2E_DB = "sqlite:///./e2e.db";

export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  retries: process.env.CI ? 1 : 0,
  use: { baseURL: "http://localhost:3000", trace: "retain-on-failure", ...devices["Pixel 5"] },
  projects: [{ name: "mobile-chromium", use: { ...devices["Pixel 5"] } }],
  webServer: [
    {
      command: `${PY} -c "import pathlib; pathlib.Path('e2e.db').unlink(missing_ok=True)" && ${PY} -m alembic upgrade head && ${PY} -m app.seed && ${PY} -m uvicorn app.main:app --port 8000`,
      cwd: "../backend",
      url: "http://localhost:8000/health",
      env: { DALIL_DATABASE_URL: E2E_DB, DALIL_ADMIN_PHONES: "0550000099", DALIL_OTP_RATE_PER_MINUTE: "100" },
      reuseExistingServer: false,
      timeout: 120_000,
    },
    {
      // Reconstruit le site si la version de production manque (le mode développement l'écrase).
      command: `(node -e "process.exit(require('fs').existsSync('.next/BUILD_ID') ? 0 : 1)" || npx next build) && npx next start -p 3000`,
      url: "http://localhost:3000",
      env: { NEXT_PUBLIC_API_URL: "http://localhost:8000/api/v1" },
      reuseExistingServer: false,
      timeout: 300_000,
    },
  ],
});
