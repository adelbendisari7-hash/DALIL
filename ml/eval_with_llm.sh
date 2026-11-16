#!/usr/bin/env bash
# Sert un modèle GGUF avec llama.cpp, mesure la chaîne complète avec ml/evaluate.py, puis arrête le serveur.
#
#   bash ml/eval_with_llm.sh <fichier.gguf> <étiquette> [modes] [options evaluate.py...]
#   bash ml/eval_with_llm.sh ml/artifacts/dalil-qwen3-4b-instruct-2507-q8_0.gguf lora-q8 full
#
# Variables : DALIL_RETRIEVAL_MODE=hybrid pour mesurer avec la recherche hybride ; PORT (8081 par défaut).
set -u
cd "$(dirname "$0")/.."
GGUF="$1"; TAG="$2"; MODES="${3:-full}"; shift 3 2>/dev/null || shift $#
PORT="${PORT:-8081}"
LOGD="${LOCALAPPDATA:-/tmp}/dalil-kaggle"; mkdir -p "$LOGD"

tools/llama.cpp/llama-server.exe -m "$GGUF" --port "$PORT" -c 4096 --alias dalil-lora --host 127.0.0.1 \
  > "$LOGD/llama-server-$TAG.log" 2>&1 &
SRV=$!
trap 'kill $SRV 2>/dev/null; taskkill //F //IM llama-server.exe >/dev/null 2>&1' EXIT
for _ in $(seq 1 90); do
  curl -s "http://127.0.0.1:$PORT/health" 2>/dev/null | grep -q ok && break
  sleep 2
done

DALIL_LLM_PROVIDER=openai_compat DALIL_LLM_BASE_URL="http://127.0.0.1:$PORT/v1" DALIL_LLM_MODEL=dalil-lora \
DALIL_LLM_TIMEOUT=900 PYTHONIOENCODING=utf-8 \
  backend/.venv/Scripts/python ml/evaluate.py --model A=ml/artifacts/baseline_tfidf_lr.joblib --modes "$MODES" --tag "$TAG" "$@" \
  2>&1 | tee "$LOGD/eval_$TAG.log"
