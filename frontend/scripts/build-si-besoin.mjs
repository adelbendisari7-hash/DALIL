// Construit la version de production du site seulement si le code a changé depuis la dernière construction.
// Appelé par DEMARRER-DALIL.bat avant `npm run start` : la version construite pèse plusieurs fois moins que le mode
// développement (premier affichage de 17 s en 3G mesuré le 19/11/2026, docs/test-telephone.md).
import { execSync } from "node:child_process";
import { existsSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";

const SOURCES = ["app", "components", "lib", "messages", "public", "next.config.mjs", "package.json", "package-lock.json", "tsconfig.json"];
const stamp = join(".next", "BUILD_ID");

function newest(path) {
  if (!existsSync(path)) return 0;
  const st = statSync(path);
  if (!st.isDirectory()) return st.mtimeMs;
  return Math.max(st.mtimeMs, ...readdirSync(path).map((name) => newest(join(path, name))));
}

const built = existsSync(stamp) ? statSync(stamp).mtimeMs : 0;
const changed = Math.max(...SOURCES.map(newest));
if (built && changed <= built) {
  console.log("Site deja construit, aucun changement depuis.");
} else {
  console.log("Construction de la version de production du site (1 a 3 minutes la premiere fois)...");
  execSync("npx next build", { stdio: "inherit", env: { ...process.env, NEXT_TELEMETRY_DISABLED: "1" } });
}
