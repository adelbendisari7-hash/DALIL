import { execFileSync } from "node:child_process";
import { existsSync } from "node:fs";
import { resolve } from "node:path";

// Python du backend : variable PYTHON si elle est donnée, sinon l'environnement backend/.venv s'il existe
// (portable), sinon « python » (intégration continue).
const VENV = resolve(__dirname, "../../backend/.venv", process.platform === "win32" ? "Scripts/python.exe" : "bin/python");
export const PY_PATH = process.env.PYTHON ? resolve(process.env.PYTHON) : existsSync(VENV) ? VENV : "python";

/** Code de connexion fixe des tests (DALIL_OTP_TEST_CODE, accepté seulement avec les SMS « console »). */
export const OTP = "424242";
export const ADMIN_PHONE = "0550000099";

/** Fichier Excel de `n` produits au format du modèle DALIL, écrit avec openpyxl (dépendance du backend). */
export function makeCatalog(path: string, n: number): void {
  const script = `
import sys
from openpyxl import Workbook
wb = Workbook()
ws = wb.active
ws.append(["Titre", "Famille", "Reference", "Marque_piece", "Etat", "Prix", "En_stock", "Compatibilite"])
fams = ["plaquettes avant", "filtre à huile", "bougies", "amortisseurs", "kit embrayage"]
for i in range(int(sys.argv[2])):
    ws.append([f"[TEST] Article {i + 1}", fams[i % 5], f"FICTIF-E2E-{i + 1:03d}", "Marque test", "adaptable",
               1000 + 100 * i, "oui", "Dacia Logan 1.5 dCi 2015"])
wb.save(sys.argv[1])
`;
  execFileSync(PY_PATH, ["-c", script, path, String(n)]);
}
