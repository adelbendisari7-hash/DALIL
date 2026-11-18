"""Pilote Kaggle de l'étape 7 : envoie les données, lance les carnets sur GPU, suit et rapatrie les résultats.

    ml/kaggle/.venv/Scripts/python ml/kaggle/kaggle_run.py whoami
    ml/kaggle/.venv/Scripts/python ml/kaggle/kaggle_run.py dataset              # crée ou met à jour « dalil-pipeline » (privé)
    ml/kaggle/.venv/Scripts/python ml/kaggle/kaggle_run.py push 01_traduction   # lance un carnet sur GPU T4
    ml/kaggle/.venv/Scripts/python ml/kaggle/kaggle_run.py status 01_traduction
    ml/kaggle/.venv/Scripts/python ml/kaggle/kaggle_run.py output 01_traduction # télécharge les sorties utiles
    ml/kaggle/.venv/Scripts/python ml/kaggle/kaggle_run.py adapter              # envoie ml/artifacts/lora_adapter (carnet 04)

Identifiants : clé API Kaggle (Settings > API) dans %USERPROFILE%\\.kaggle\\kaggle.json ou variable KAGGLE_API_TOKEN.
Tout est privé : le jeu de données et les carnets ne sont visibles que par le titulaire du compte.
"""
from __future__ import annotations

import json
import os
import shutil
import tempfile
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).parent
# Dossier de préparation hors de OneDrive : la synchronisation verrouille les fichiers en cours de copie.
STAGING = Path(os.environ.get("LOCALAPPDATA", tempfile.gettempdir())) / "dalil-kaggle" / "staging"
KERNELS = HERE / "_kernels"
OUTPUTS = HERE / "_outputs"
# « python -m kaggle » plutôt que le lanceur kaggle.exe : celui-ci garde le chemin absolu du dossier au moment
# de l'installation et ne répond plus (sans message) si le projet est déplacé.
KAGGLE = [sys.executable, "-m", "kaggle"]
DATASET_SLUG = "dalil-pipeline"
ADAPTER_SLUG = "dalil-lora-adapter"
ADAPTER_DIR = ROOT / "ml" / "artifacts" / "lora_adapter"
NOTEBOOKS = {
    "01_traduction": {"slug": "dalil-01-traduction", "outputs": ["dalil_processed.zip"]},
    "02_encodeur_fr": {"slug": "dalil-02-encodeur-fr", "outputs": ["*_onnx.zip"]},
    "02_encodeur_enfr": {"slug": "dalil-02-encodeur-enfr", "outputs": ["*_onnx.zip"]},
    "02_encodeur_camembert": {"slug": "dalil-02-encodeur-camembert", "outputs": ["*_onnx.zip"]},
    "03_lora_llm": {"slug": "dalil-03-lora-llm", "outputs": ["*.gguf", "*-evaluation.json"]},
    "04_fusion_gguf": {"slug": "dalil-04-fusion-gguf", "outputs": ["*.gguf", "*-evaluation.json"],
                       "datasets": [ADAPTER_SLUG]},
    "05_vecteurs": {"slug": "dalil-05-vecteurs", "outputs": ["chunk_vectors.npy", "chunk_ids.json", "check_queries.json", "*.zip"]},
}
# Ce qui part sur Kaggle : le code et les données traitées, jamais les données brutes ni les environnements.
INCLUDE = ["backend", "data/pipeline", "data/seed", "data/test", "data/processed"]
IGNORE = shutil.ignore_patterns(".venv", "__pycache__", "*.db", "*.db-journal", ".pytest*", "tests", "*.tmp", "_staging")


def kaggle(*args: str, check: bool = True) -> str:
    res = subprocess.run([*KAGGLE, *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = (res.stdout or "") + (res.stderr or "")
    if check and res.returncode != 0:
        raise SystemExit(f"kaggle {' '.join(args)} a échoué :\n{out}")
    return out


def username() -> str:
    from kaggle.api.kaggle_api_extended import KaggleApi

    api = KaggleApi()
    api.authenticate()
    user = api.get_config_value("username") or getattr(api, "config_values", {}).get("username")
    if not user:
        raise SystemExit("nom d'utilisateur Kaggle introuvable : ajouter \"username\" dans kaggle.json")
    return user


def _force_remove(func, path, _exc):
    """Supprime aussi les fichiers en lecture seule (copiés depuis OneDrive)."""
    import stat

    os.chmod(path, stat.S_IWRITE)
    func(path)


def stage() -> Path:
    folder = STAGING
    if folder.exists():
        try:
            shutil.rmtree(folder, onexc=_force_remove)
        except OSError:  # dossier encore verrouillé : on en prend un neuf
            import time

            folder = STAGING.with_name(f"staging-{int(time.time())}")
    for rel in INCLUDE:
        src = ROOT / rel
        if src.exists():
            shutil.copytree(src, folder / rel, ignore=IGNORE)
    size = sum(p.stat().st_size for p in folder.rglob("*") if p.is_file()) / 1e6
    print(f"préparé : {folder} ({size:.0f} Mo)")
    return folder


def cmd_dataset() -> None:
    user = username()
    folder = stage()
    (folder / "dataset-metadata.json").write_text(json.dumps({
        "title": DATASET_SLUG, "id": f"{user}/{DATASET_SLUG}", "licenses": [{"name": "other"}],
        "subtitle": "Code et données traitées du projet DALIL (privé)",
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    exists = DATASET_SLUG in kaggle("datasets", "list", "--mine", "-s", DATASET_SLUG, check=False)
    if exists:
        print(kaggle("datasets", "version", "-p", str(folder), "-m", "mise à jour depuis le portable", "-r", "zip"))
    else:
        print(kaggle("datasets", "create", "-p", str(folder), "-r", "zip"))  # privé par défaut
    print(kaggle("datasets", "status", f"{user}/{DATASET_SLUG}", check=False))


def cmd_adapter() -> None:
    """Envoie l'adaptateur LoRA entraîné par le carnet 03 (ml/artifacts/lora_adapter) comme jeu de données privé,
    pour que le carnet 04 fasse évaluation, fusion et GGUF sans réentraîner."""
    user = username()
    if not (ADAPTER_DIR / "adapter_config.json").exists():
        raise SystemExit(f"adaptateur absent : {ADAPTER_DIR}")
    folder = STAGING.with_name("staging-adapter")
    if folder.exists():
        shutil.rmtree(folder, onexc=_force_remove)
    shutil.copytree(ADAPTER_DIR, folder)
    (folder / "dataset-metadata.json").write_text(json.dumps({
        "title": ADAPTER_SLUG, "id": f"{user}/{ADAPTER_SLUG}", "licenses": [{"name": "other"}],
        "subtitle": "Adaptateur LoRA DALIL (Qwen3-4B-Instruct-2507)",
    }, indent=2), encoding="utf-8")
    if ADAPTER_SLUG in kaggle("datasets", "list", "--mine", "-s", ADAPTER_SLUG, check=False):
        print(kaggle("datasets", "version", "-p", str(folder), "-m", "nouvel adaptateur"))
    else:
        print(kaggle("datasets", "create", "-p", str(folder)))
    print(kaggle("datasets", "status", f"{user}/{ADAPTER_SLUG}", check=False))


def cmd_push(name: str) -> None:
    user = username()
    nb = NOTEBOOKS[name]
    folder = KERNELS / name
    folder.mkdir(parents=True, exist_ok=True)
    shutil.copy(HERE / f"{name}.ipynb", folder / f"{name}.ipynb")
    (folder / "kernel-metadata.json").write_text(json.dumps({
        "id": f"{user}/{nb['slug']}", "title": nb["slug"], "code_file": f"{name}.ipynb",
        "language": "python", "kernel_type": "notebook", "is_private": True,
        "enable_gpu": True, "enable_internet": True,
        "dataset_sources": [f"{user}/{d}" for d in [DATASET_SLUG, *nb.get("datasets", [])]], "competition_sources": [], "kernel_sources": [],
    }, indent=2), encoding="utf-8")
    # Pas de type de GPU imposé : imposer la T4 a laissé un carnet plus d'une heure en file d'attente,
    # alors que Kaggle démarre aussitôt sur le premier GPU libre. KAGGLE_ACCELERATOR pour en forcer un.
    accel = os.environ.get("KAGGLE_ACCELERATOR")
    print(kaggle("kernels", "push", "-p", str(folder), *(["--accelerator", accel] if accel else [])))
    print(f"suivi : https://www.kaggle.com/code/{user}/{nb['slug']}")


def cmd_status(name: str) -> None:
    print(kaggle("kernels", "status", f"{username()}/{NOTEBOOKS[name]['slug']}", check=False).strip())


def cmd_output(name: str) -> None:
    user = username()
    dest = OUTPUTS / name
    dest.mkdir(parents=True, exist_ok=True)
    for pattern in NOTEBOOKS[name]["outputs"]:
        print(kaggle("kernels", "output", f"{user}/{NOTEBOOKS[name]['slug']}", "-p", str(dest), "-o",
                     "--file-pattern", pattern.replace("*", ".*"), check=False))
    print(f"sorties dans {dest} :", [p.name for p in dest.iterdir()])


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "whoami":
        print(username())
    elif cmd == "stage":
        stage()
    elif cmd == "dataset":
        cmd_dataset()
    elif cmd == "adapter":
        cmd_adapter()
    elif cmd in ("push", "status", "output"):
        if not args or args[0] not in NOTEBOOKS:
            raise SystemExit(f"carnet attendu parmi : {', '.join(NOTEBOOKS)}")
        {"push": cmd_push, "status": cmd_status, "output": cmd_output}[cmd](args[0])
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
