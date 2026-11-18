"""ml/relecture_etiquettes.py : tirage stratifié, fiche Excel, mesure par niveau de confiance."""
import json
import sys
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "ml"))

import relecture_etiquettes as R  # noqa: E402


def _rows():
    rows = []
    for i in range(60):
        q = "solution+component" if i < 10 else "reponses"   # niveau rare et niveau fréquent
        rows.append({"id": f"largus_forum:{i}", "lang": "fr", "text": f"Question {i}", "categories": ["plaquettes-avant"],
                     "family": "freinage", "label_quality": q, "url": f"https://exemple/{i}",
                     "meta": {"solution": "plaquettes changées"}})
    rows.append({"id": "largus_forum:999", "lang": "fr", "text": "sans étiquette", "categories": [], "family": None})
    return rows


def test_tirage_stratifie_et_mesure(tmp_path):
    src = tmp_path / "largus_forum.jsonl"
    src.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in _rows()), encoding="utf-8")
    picked, population = R.sample(R.labelled(src), 20)
    assert population == {"solution+component": 10, "reponses": 50}       # la ligne sans étiquette n'est pas relue
    assert sum(r["label_quality"] == "solution+component" for r in picked) == 10   # autant par niveau
    assert R.sample(R.labelled(src), 20)[0] == picked                     # graine fixe : même tirage

    xlsx = tmp_path / "relecture.xlsx"
    R.write_sheet(picked, population, xlsx, "largus_forum")
    wb = load_workbook(xlsx)
    ws = wb["Relecture"]
    header = [c.value for c in ws[1]]
    assert ws.max_row == 21 and ws.cell(row=2, column=header.index("Pièce proposée") + 1).value == "Plaquettes de frein avant"
    col = header.index("Juste ?") + 1
    k = 0
    for r in range(2, 22):  # relecteur : niveau sûr toujours juste ; niveau faible : 1 « ? », puis juste 1 fois sur 3
        if ws.cell(row=r, column=2).value == "solution+component":
            ws.cell(row=r, column=col, value="oui")
        else:
            ws.cell(row=r, column=col, value="?" if k == 0 else ("oui" if k % 3 == 0 else "non"))
            k += 1
    wb.save(xlsx)

    res = R.measure(xlsx)
    sure, faible = res["niveaux"]["solution+component"], res["niveaux"]["reponses"]
    assert sure["piece_juste"] == 1.0 and sure["decision"] == "garder" and sure["population"] == 10
    assert faible["n"] == 9 and faible["ignores"] == 1 and faible["oui"] == 3 and faible["decision"] == "écarter"
    expected = (1.0 * 10 + faible["piece_juste"] * 50) / 60                # repondéré par la population
    assert abs(res["justesse_globale_repondérée"] - expected) < 0.002
    assert "| solution+component |" in R.report_md(res)


def test_intervalle_wilson():
    assert R.wilson(10, 10)[0] > 0.65 and R.wilson(0, 10)[1] < 0.35
