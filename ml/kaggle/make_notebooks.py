"""Génère les carnets Kaggle de l'étape 7 (format .ipynb) à partir des cellules ci-dessous.

    python ml/kaggle/make_notebooks.py

Les carnets supposent un jeu de données Kaggle privé « dalil-pipeline » contenant le dépôt
(backend/, data/pipeline/, data/seed/, data/test/, data/processed/) ; voir ml/kaggle/README.md.
"""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

HERE = Path(__file__).parent

SETUP = '''import glob, json, os, random, shutil, time
from collections import Counter
# Le jeu de données « dalil-pipeline » est monté sous /kaggle/input (chemin variable selon Kaggle) :
# on cherche le dossier qui contient backend/ et data/.
INPUT = next(root for root, dirs, _ in os.walk("/kaggle/input") if "backend" in dirs and "data" in dirs)
REPO = "/kaggle/working/dalil"
if not os.path.exists(REPO):
    shutil.copytree(INPUT, REPO)
os.chdir(REPO)
print(sorted(os.listdir(REPO)))'''

NB_TRANSLATE = [
    ("md", "# DALIL : traduction des corpus (étape 6)\n\nParamètres Kaggle : **GPU T4**, **Internet activé**. "
           "Le cache de traduction est écrit au fil de l'eau : si la session s'arrête, relancer la dernière cellule reprend "
           "là où elle s'était arrêtée. À la fin, télécharger `data/processed/` depuis l'onglet *Output*."),
    ("code", SETUP),
    ("code", "!pip install -q sentencepiece sacremoses py7zr pydantic-settings"),
    ("code", "!python data/pipeline/run.py translate --sources nhtsa_complaints,nhtsa_recalls,stackexchange_mechanics,cvffad --redo-uppercase --review 200"),
    ("code", "!python data/pipeline/run.py report && cat data/processed/report.md\n"
             "!cd data && zip -qr /kaggle/working/dalil_processed.zip processed -x 'processed/llm/*'\n"
             "!du -sh /kaggle/working/dalil_processed.zip"),
]

NB_ENCODER = [
    ("md", "# DALIL : classifieur de famille de pièce par encodeur multilingue affiné (variante B)\n\n"
           "Paramètres Kaggle : **GPU T4**, **Internet activé**. Sortie : dossier ONNX à copier dans `ml/artifacts/` "
           "puis à évaluer avec `python ml/evaluate.py --model B=ml/artifacts/<dossier>`.\n\n"
           "Deux configurations à comparer (section 6.3) : `fr` (textes traduits en français) et `en+fr` "
           "(textes anglais d'origine + français : transfert multilingue sans traduction)."),
    ("code", SETUP),
    ("code", '!pip install -q -U "transformers>=4.48" accelerate onnx onnxruntime onnxscript'),
    ("code", '''MODEL_ID = "jhu-clsp/mmBERT-base"   # à comparer : "FacebookAI/xlm-roberta-base", "alger-ia/dziribert"
CONFIG = "__CONFIG__"                 # "fr" (textes traduits) ou "en+fr" (transfert depuis l'anglais)
MAX_LEN, EPOCHS, LR, BATCH, SEED, MIN_PER_CLASS = 256, 3, 3e-5, 32, 13, 5
NAME = f"{MODEL_ID.split('/')[-1]}_{CONFIG.replace('+', '-')}"
OUT = f"/kaggle/working/{NAME}"
os.makedirs(OUT, exist_ok=True)'''),
    ("code", '''def load_jsonl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]

faults = json.load(open("data/seed/faults.json", encoding="utf-8"))["faults"]
f2p = {f["slug"]: max(f["parts"].items(), key=lambda x: x[1])[0] for f in faults}
examples = [{"text": r["text"], "label": f2p[r["fault"]], "src": "seed"} for r in load_jsonl("data/seed/diagnosis_examples_fr.jsonl")]
for p in sorted(glob.glob("data/processed/train/*.jsonl")):
    for r in load_jsonl(p):
        label = r.get("category") or r.get("family")
        if not label:
            continue
        if CONFIG == "fr":
            text = r["text"] if r["lang"] == "fr" else r.get("text_fr")
        else:
            text = r["text"] if r["lang"] in ("en", "fr") else r.get("text_fr")
        if text:
            examples.append({"text": text[:2000], "label": label, "src": r["source"]})
counts = Counter(e["label"] for e in examples)
examples = [e for e in examples if counts[e["label"]] >= MIN_PER_CLASS]
labels = sorted({e["label"] for e in examples})
lid = {l: i for i, l in enumerate(labels)}
random.Random(SEED).shuffle(examples)
n_val = max(50, len(examples) // 10)
val, train = examples[:n_val], examples[n_val:]
dev = [d for d in load_jsonl("data/test/dev_fr_synthetique.jsonl") if d.get("text") and d.get("expect")]
print(f"{len(train)} entraînement, {len(val)} validation, {len(dev)} dev FR, {len(labels)} classes")
print(Counter(e["src"] for e in examples))'''),
    ("code", '''import torch
from torch.utils.data import DataLoader
from transformers import AutoModelForSequenceClassification, AutoTokenizer, get_linear_schedule_with_warmup

torch.manual_seed(SEED)
tok = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_ID, num_labels=len(labels), id2label=dict(enumerate(labels)), label2id=lid).to("cuda")

def collate(batch):
    enc = tok([b["text"] for b in batch], truncation=True, max_length=MAX_LEN, padding=True, return_tensors="pt")
    enc["labels"] = torch.tensor([lid[b["label"]] for b in batch])
    return enc

@torch.no_grad()
def predict(texts, bs=64):
    model.eval()
    out = []
    for i in range(0, len(texts), bs):
        enc = tok(texts[i:i + bs], truncation=True, max_length=MAX_LEN, padding=True, return_tensors="pt").to("cuda")
        with torch.autocast("cuda", dtype=torch.float16):
            out.append(model(**enc).logits.float().softmax(-1).cpu())
    model.train()
    return torch.cat(out)

def topk(probs, gold_sets, k):
    idx = probs.topk(k, dim=-1).indices.tolist()
    return round(sum(any(labels[j] in g for j in row) for row, g in zip(idx, gold_sets)) / len(gold_sets), 3)

def evaluate():
    pv = predict([e["text"] for e in val])
    pd = predict([d["text"] for d in dev])
    gv, gd = [{e["label"]} for e in val], [set(d["expect"]) for d in dev]
    return {"val_top1": topk(pv, gv, 1), "val_top3": topk(pv, gv, 3), "dev_top1": topk(pd, gd, 1), "dev_top3": topk(pd, gd, 3)}

dl = DataLoader(train, batch_size=BATCH, shuffle=True, collate_fn=collate)
opt = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=0.01)
sched = get_linear_schedule_with_warmup(opt, int(0.06 * len(dl) * EPOCHS), len(dl) * EPOCHS)
scaler = torch.amp.GradScaler("cuda")
ckpt, start, history = f"{OUT}/checkpoint.pt", 0, []
if os.path.exists(ckpt):   # reprise après une session Kaggle interrompue (sauvegarde à chaque époque)
    state = torch.load(ckpt, weights_only=False)
    model.load_state_dict(state["model"]); opt.load_state_dict(state["opt"]); sched.load_state_dict(state["sched"])
    start, history = state["epoch"] + 1, state["history"]
for epoch in range(start, EPOCHS):
    t0 = time.time()
    for step, batch in enumerate(dl):
        batch = {k: v.to("cuda") for k, v in batch.items()}
        with torch.autocast("cuda", dtype=torch.float16):
            loss = model(**batch).loss
        scaler.scale(loss).backward()
        scaler.unscale_(opt)
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        scaler.step(opt); scaler.update(); opt.zero_grad(); sched.step()
        if step % 100 == 0:
            print(f"époque {epoch} pas {step}/{len(dl)} perte {loss.item():.3f}")
    history.append({"epoch": epoch, **evaluate(), "minutes": round((time.time() - t0) / 60, 1)})
    print(history[-1])
    torch.save({"model": model.state_dict(), "opt": opt.state_dict(), "sched": sched.state_dict(),
                "epoch": epoch, "history": history}, ckpt)'''),
    ("code", '''# Export ONNX : le portable l'exécute avec onnxruntime, sans PyTorch
model.save_pretrained(f"{OUT}/hf"); tok.save_pretrained(f"{OUT}/hf")
export = AutoModelForSequenceClassification.from_pretrained(f"{OUT}/hf", attn_implementation="eager").eval()

class Logits(torch.nn.Module):
    def __init__(self, m):
        super().__init__(); self.m = m
    def forward(self, input_ids, attention_mask):
        return self.m(input_ids=input_ids, attention_mask=attention_mask).logits

onnx_dir = f"{OUT}/onnx"
os.makedirs(onnx_dir, exist_ok=True)
sample = tok(["le volant tremble quand je freine"], return_tensors="pt")
torch.onnx.export(Logits(export), (sample["input_ids"], sample["attention_mask"]), f"{onnx_dir}/model.onnx",
                  input_names=["input_ids", "attention_mask"], output_names=["logits"],
                  dynamic_axes={"input_ids": {0: "b", 1: "t"}, "attention_mask": {0: "b", 1: "t"}, "logits": {0: "b"}},
                  opset_version=17, dynamo=False)   # exportateur classique : axes dynamiques fiables
tok.save_pretrained(onnx_dir)   # écrit tokenizer.json
json.dump({"target": "part", "labels": labels, "version": f"{NAME}-{time.strftime('%Y%m%d')}", "max_length": MAX_LEN,
           "history": history, "model_id": MODEL_ID, "config": CONFIG},
          open(f"{onnx_dir}/labels.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# Vérification : mêmes sorties en ONNX et en PyTorch
import numpy as np, onnxruntime as ort
sess = ort.InferenceSession(f"{onnx_dir}/model.onnx", providers=["CPUExecutionProvider"])
o = sess.run(None, {"input_ids": sample["input_ids"].numpy(), "attention_mask": sample["attention_mask"].numpy()})[0]
with torch.no_grad():
    t = export(**sample).logits.numpy()
print("écart max ONNX / PyTorch :", float(np.abs(o - t).max()))

# Quantification int8 : modèle ~4 fois plus léger et plus rapide sur le processeur du portable.
# On ne la garde que si la précision sur le jeu dev ne baisse pas de plus d'un point.
from onnxruntime.quantization import QuantType, quantize_dynamic
quantize_dynamic(f"{onnx_dir}/model.onnx", f"{OUT}/model.int8.onnx", weight_type=QuantType.QInt8)

def ort_dev_scores(path):
    sess = ort.InferenceSession(path, providers=["CPUExecutionProvider"])
    rows = []
    for d in dev:
        enc = tok([d["text"]], truncation=True, max_length=MAX_LEN, return_tensors="np")
        logits = sess.run(None, {"input_ids": enc["input_ids"].astype(np.int64), "attention_mask": enc["attention_mask"].astype(np.int64)})[0][0]
        rows.append(torch.tensor(logits).softmax(-1))
    probs = torch.stack(rows)
    gd = [set(d["expect"]) for d in dev]
    return {"dev_top1": topk(probs, gd, 1), "dev_top3": topk(probs, gd, 3)}

fp32, int8 = ort_dev_scores(f"{onnx_dir}/model.onnx"), ort_dev_scores(f"{OUT}/model.int8.onnx")
print("fp32", fp32, "int8", int8)
meta = json.load(open(f"{onnx_dir}/labels.json", encoding="utf-8"))
meta.update({"onnx_fp32": fp32, "onnx_int8": int8})
if int8["dev_top1"] >= fp32["dev_top1"] - 0.01:
    shutil.move(f"{OUT}/model.int8.onnx", f"{onnx_dir}/model.onnx")
    meta["quantization"] = "int8 dynamique"
json.dump(meta, open(f"{onnx_dir}/labels.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("taille du modèle :", round(os.path.getsize(f"{onnx_dir}/model.onnx") / 1e6), "Mo", meta.get("quantization", "fp32"))
shutil.make_archive(f"/kaggle/working/{NAME}_onnx", "zip", onnx_dir)
print(history)'''),
]

# --- Cellules communes aux carnets 03 (entraînement) et 04 (reprise d'un adaptateur déjà entraîné) ---

# torchao 0.10 préinstallé sur Kaggle : peft refuse alors de charger un adaptateur (ImportError).
PIP_LLM = '!pip install -q -U "transformers>=4.51" peft trl bitsandbytes accelerate datasets\n!pip uninstall -y -q torchao'

EVAL_CELL = r'''# Évaluation sur la validation : JSON valide, panne correcte en tête, aucune panne hors des candidats
import re
def generate(messages, max_new_tokens=512):
    prompt = tok.apply_chat_template(messages[:2], tokenize=False, add_generation_prompt=True)
    ids = tok(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        out = model.generate(**ids, max_new_tokens=max_new_tokens, do_sample=False, use_cache=True)
    return tok.decode(out[0][ids["input_ids"].shape[1]:], skip_special_tokens=True)

ok_json = ok_top1 = ok_cands = 0
samples = []
t_eval = time.time()
val = data["val"].select(range(min(N_EVAL, len(data["val"]))))
for i, ex in enumerate(val):
    gold = json.loads(ex["messages"][2]["content"])["ranking"][0]["fault"]
    cands = {c["slug"] for c in json.loads(ex["messages"][1]["content"])["candidats"]}
    text = generate(ex["messages"])
    if i < 3:
        print(f"--- réponse {i} (attendu : {gold}) ---\n{text[:800]}", flush=True)
    m = re.search(r"\{.*\}", text, re.S)
    try:
        ranking = json.loads(m.group(0))["ranking"]
        ok_json += 1
        ok_top1 += ranking[0]["fault"] == gold
        ok_cands += all(r["fault"] in cands for r in ranking)
    except Exception:
        pass
    samples.append({"gold": gold, "output": text})
    if time.time() - t_eval > MAX_EVAL_MIN * 60:
        print(f"Budget d'évaluation atteint après {i + 1} exemples", flush=True)
        val = val.select(range(i + 1))
        break
    if i % 10 == 0:
        print(f"évaluation {i}/{len(val)} ({time.time() - t_eval:.0f} s)", flush=True)
n = len(val)
result = {"n": n, "json_valide": ok_json, "top1": ok_top1, "candidats_respectes": ok_cands}
print(f"JSON valide {ok_json}/{n}, panne correcte en tête {ok_top1}/{n}, candidats respectés {ok_cands}/{n}")
with open(f"/kaggle/working/{NAME}-evaluation.json", "w", encoding="utf-8") as fh:
    json.dump({"resultat": result, "reponses": samples}, fh, ensure_ascii=False, indent=1)'''

MERGE_CELL = '''# Fusion de l'adaptateur dans le modèle de base (float16, sur processeur)
from peft import PeftModel
base = AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype=torch.float16, device_map="cpu")
merged = PeftModel.from_pretrained(base, ADAPTER).merge_and_unload()
merged.save_pretrained(f"/tmp/merged", safe_serialization=True)
del base, merged
# Fichiers du tokenizer d'origine : ceux réécrits par transformers 5 font échouer convert_hf_to_gguf
# (« 'list' object has no attribute 'keys' »).
from huggingface_hub import snapshot_download
src = snapshot_download(MODEL_ID, allow_patterns=["tokenizer*", "vocab.json", "merges.txt", "special_tokens_map.json",
                                                  "generation_config.json"])
for f in os.listdir(src):
    if os.path.isfile(os.path.join(src, f)):
        shutil.copy(os.path.join(src, f), f"/tmp/merged/{f}")
print(sorted(os.listdir(f"/tmp/merged")))'''

GGUF_CELL = '''# Conversion en GGUF pour llama.cpp (processeur du portable)
!git clone -q --depth 1 https://github.com/ggml-org/llama.cpp /kaggle/working/llama.cpp
!pip install -q -r /kaggle/working/llama.cpp/requirements/requirements-convert_hf_to_gguf.txt
!pip uninstall -y -q torchao
!python /kaggle/working/llama.cpp/convert_hf_to_gguf.py /tmp/merged --outfile /tmp/{NAME}-f16.gguf --outtype f16
!rm -rf /tmp/merged && df -h /tmp /kaggle/working
# llama-quantize refuse de recompresser un fichier déjà en q8_0 : on part du f16. Modèle fusionné et f16 (8 Go
# chacun) dans /tmp : /kaggle/working est limité à ~20 Go (« Not enough free space »).
!cd /kaggle/working/llama.cpp && cmake -B build -DGGML_CUDA=OFF -DLLAMA_CURL=OFF > /dev/null && cmake --build build --target llama-quantize -j 4 > /dev/null
!/kaggle/working/llama.cpp/build/bin/llama-quantize /tmp/{NAME}-f16.gguf /kaggle/working/{NAME}-q4_k_m.gguf Q4_K_M
!/kaggle/working/llama.cpp/build/bin/llama-quantize /tmp/{NAME}-f16.gguf /kaggle/working/{NAME}-q8_0.gguf Q8_0
!rm -f /tmp/{NAME}-f16.gguf
!rm -rf /kaggle/working/llama.cpp && ls -lh /kaggle/working/*.gguf'''


NB_LLM = [
    ("md", "# DALIL : modèle de langage affiné par LoRA (variante D, section 6.6)\n\n"
           "Paramètres Kaggle : **GPU T4** (ou P100), **Internet activé**. Entrée : `data/processed/llm/` produit par "
           "`python ml/build_llm_dataset.py` (relancer ce script après la traduction pour profiter du corpus). "
           "Sortie : fichier GGUF servi sur le portable par llama.cpp (`ml/kaggle/README.md`).\n\n"
           "Gemma 3 demande d'accepter sa licence sur Hugging Face et un jeton `HF_TOKEN` dans les secrets Kaggle."),
    ("code", SETUP),
    ("code", PIP_LLM),
    ("code", '''MODEL_ID = "Qwen/Qwen3-4B-Instruct-2507"   # à comparer : "google/gemma-3-4b-it", "Qwen/Qwen3-8B" (variante plus lourde)
NAME = "dalil-" + MODEL_ID.split("/")[-1].lower()
OUT = f"/kaggle/working/{NAME}"
ADAPTER = f"{OUT}/adapter"
EPOCHS, LR, MAX_LEN = 1, 2e-4, 2048
N_EVAL = 100   # exemples de validation générés à la fin (la génération est lente)
MAX_TRAIN_H, MAX_EVAL_MIN = 3.5, 30   # garde-fous : la session Kaggle s'arrête à 12 h, on garde de la marge'''),
    ("code", '''# Un seul GPU visible, avant le premier import de torch : SFTTrainer refuse nn.DataParallel (T4 x2).
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
import torch
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainerCallback
from trl import SFTConfig, SFTTrainer

data = load_dataset("json", data_files={"train": "data/processed/llm/train.jsonl", "val": "data/processed/llm/val.jsonl"})
tok = AutoTokenizer.from_pretrained(MODEL_ID)
bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.float16,
                         bnb_4bit_use_double_quant=True)
model = AutoModelForCausalLM.from_pretrained(MODEL_ID, quantization_config=bnb, device_map={"": 0}, dtype=torch.float16)
lora = LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, task_type="CAUSAL_LM",
                  target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"])
# Les GPU T4 et P100 ne gèrent pas le bfloat16. TRL active bf16 par défaut : on le coupe explicitement et on
# entraîne en précision mixte float16, adaptateurs LoRA en float32 (sinon le GradScaler échoue).
# Un seul GPU (device_map {"": 0}) : réparti sur deux T4, le modèle passe son temps à attendre l'autre carte.
# Pas de prepare_model_for_kbit_training : il passe embeddings et tête de sortie en float32, ce qui divise
# la vitesse par plusieurs fois sur T4.
model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
model.enable_input_require_grads()
model = get_peft_model(model, lora)
for param in model.parameters():
    if param.requires_grad:
        param.data = param.data.float()
model.print_trainable_parameters()
cfg = SFTConfig(output_dir=OUT, num_train_epochs=EPOCHS, learning_rate=LR, per_device_train_batch_size=2,
                gradient_accumulation_steps=8, gradient_checkpointing=True,
                gradient_checkpointing_kwargs={"use_reentrant": False}, fp16=True, bf16=False,
                logging_steps=5, logging_first_step=True, disable_tqdm=True,   # journal lisible en direct sur Kaggle
                save_strategy="steps", save_steps=40, save_total_limit=1, eval_strategy="no",
                max_length=MAX_LEN, report_to="none")
class TimeBudget(TrainerCallback):
    """Arrête proprement l'entraînement après MAX_TRAIN_H heures : l'adaptateur est sauvegardé, puis
    l'évaluation et la conversion GGUF tournent quand même. Évite une nuit perdue si le GPU est lent."""
    def on_train_begin(self, args, state, control, **kw):
        self.t0 = time.time()
    def on_step_end(self, args, state, control, **kw):
        if time.time() - self.t0 > MAX_TRAIN_H * 3600:
            print(f"Budget de temps atteint à l'étape {state.global_step}/{state.max_steps} : arrêt de l'entraînement", flush=True)
            control.should_training_stop = True
        return control

trainer = SFTTrainer(model=model, args=cfg, train_dataset=data["train"], eval_dataset=data["val"],
                     processing_class=tok, callbacks=[TimeBudget()])
# SFTTrainer repasse les adaptateurs d'un modèle quantifié en bfloat16 : le GradScaler float16 échoue alors
# (« _amp_foreach_non_finite_check_and_unscale_cuda not implemented for BFloat16 »). On les remet en float32
# après sa construction ; l'optimiseur n'est créé qu'au lancement de train().
for param in trainer.model.parameters():
    if param.requires_grad and param.dtype != torch.float32:
        param.data = param.data.float()
print("types des paramètres entraînés :", Counter(str(p.dtype) for p in trainer.model.parameters() if p.requires_grad))
resume = bool(glob.glob(f"{OUT}/checkpoint-*"))   # reprise après une session interrompue
trainer.train(resume_from_checkpoint=resume)
trainer.save_model(f"{OUT}/adapter")'''),
    ("code", """# Passage en mode génération : sans cela le gradient checkpointing laisse le cache désactivé
# (~50 s par réponse) et le dropout LoRA reste actif.
model.gradient_checkpointing_disable(); model.config.use_cache = True; model.eval()"""),
    ("code", EVAL_CELL),
    ("code", "del model, trainer; torch.cuda.empty_cache()"),
    ("code", MERGE_CELL),
    ("code", GGUF_CELL),
]

NB_FUSION = [
    ("md", "# DALIL : évaluation, fusion et GGUF d'un adaptateur LoRA déjà entraîné (variante D)\n\n"
           "Reprend l'adaptateur produit par le carnet 03 (jeu de données Kaggle `dalil-lora-adapter`, envoyé par "
           "`python ml/kaggle/kaggle_run.py adapter`) sans refaire les 3 h d'entraînement. GPU T4, Internet activé."),
    ("code", SETUP),
    ("code", PIP_LLM),
    ("code", '''MODEL_ID = "Qwen/Qwen3-4B-Instruct-2507"
NAME = "dalil-" + MODEL_ID.split("/")[-1].lower()
OUT = f"/kaggle/working/{NAME}"
N_EVAL, MAX_EVAL_MIN = 100, 40
RUN_EVAL = False   # déjà mesuré le 15/11/2026 : JSON valide 79/79, panne correcte en tête 50/79, candidats respectés 79/79
ADAPTER = next(root for root, _, files in os.walk("/kaggle/input") if "adapter_config.json" in files)
print("adaptateur :", ADAPTER)'''),
    ("code", '''os.environ["CUDA_VISIBLE_DEVICES"] = "0"
import torch
from datasets import load_dataset
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

data = load_dataset("json", data_files={"val": "data/processed/llm/val.jsonl"})
tok = AutoTokenizer.from_pretrained(MODEL_ID)
bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.float16,
                         bnb_4bit_use_double_quant=True)
if RUN_EVAL:
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, quantization_config=bnb, device_map={"": 0}, dtype=torch.float16)
    model = PeftModel.from_pretrained(model, ADAPTER).eval()'''),
    ("code", "if RUN_EVAL:\n" + textwrap.indent(EVAL_CELL, "    ") + "\n    del model; torch.cuda.empty_cache()"),
    ("code", MERGE_CELL),
    ("code", GGUF_CELL),
]

NB_VECTEURS = [
    ("md", "# DALIL : vecteurs de recherche et modèle de reclassement (étape 8, section 6.1)\n\n"
           "Paramètres Kaggle : **GPU T4**, **Internet activé**. Entrée : `data/processed/kb/chunks.jsonl` "
           "(`python ml/export_kb_chunks.py`). Calcule un vecteur Qwen3-Embedding-0.6B par passage de la base de "
           "connaissances, vérifie la recherche sur quelques requêtes, puis exporte les deux modèles "
           "(Qwen3-Embedding-0.6B et bge-reranker-v2-m3) pour les charger sur le portable.\n\n"
           "Sorties : `chunk_vectors.npy` (float16, normalisés), `chunk_ids.json`, `check_queries.json` (contrôle du "
           "portage), `qwen3-embedding-0.6b.zip`, `bge-reranker-v2-m3.zip`."),
    ("code", SETUP),
    ("code", '!pip install -q -U "transformers>=4.51"'),
    ("code", '''os.environ["CUDA_VISIBLE_DEVICES"] = "0"
import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModel, AutoModelForSequenceClassification, AutoTokenizer

EMB_ID, RERANK_ID = "Qwen/Qwen3-Embedding-0.6B", "BAAI/bge-reranker-v2-m3"
MAX_LEN, BATCH = 384, 32
# Instruction devant chaque requête (les passages n'en portent pas). Même chaîne côté portable :
# backend/app/services/diagnosis/embeddings.py
TASK = "Given a description of a car problem, retrieve passages describing the same fault"
rows = [json.loads(l) for l in open("data/processed/kb/chunks.jsonl", encoding="utf-8")]
print(len(rows), "passages")

tok = AutoTokenizer.from_pretrained(EMB_ID, padding_side="left")
model = AutoModel.from_pretrained(EMB_ID, dtype=torch.float16).cuda().eval()


def encode(texts, bs=BATCH, max_len=MAX_LEN):
    """Vecteur du dernier jeton (remplissage à gauche), normalisé : méthode de Qwen3-Embedding."""
    order = sorted(range(len(texts)), key=lambda i: -len(texts[i]))   # lots de longueurs voisines : plus rapide
    out = np.zeros((len(texts), model.config.hidden_size), dtype=np.float16)
    t0 = time.time()
    for s in range(0, len(order), bs):
        idx = order[s:s + bs]
        enc = tok([texts[i] for i in idx], padding=True, truncation=True, max_length=max_len, return_tensors="pt").to("cuda")
        with torch.no_grad():
            h = model(**enc).last_hidden_state[:, -1]
        out[idx] = F.normalize(h.float(), dim=-1).cpu().numpy().astype(np.float16)
        if (s // bs) % 50 == 0:
            print(f"{s}/{len(texts)} ({time.time() - t0:.0f} s)", flush=True)
    return out


def query_text(q):
    return f"Instruct: {TASK}\\nQuery:{q}"'''),
    ("code", '''vectors = encode([r["text"] for r in rows])
np.save("/kaggle/working/chunk_vectors.npy", vectors)
json.dump([r["id"] for r in rows], open("/kaggle/working/chunk_ids.json", "w"))
print(vectors.shape, vectors.dtype, "norme moyenne", float(np.linalg.norm(vectors.astype(np.float32), axis=1).mean()))'''),
    ("code", '''# Contrôle : quelques requêtes du jeu dev, passages les plus proches. Les vecteurs des requêtes sont aussi
# exportés : le portable doit retrouver les mêmes (cosinus ~ 1), sinon son portage de la méthode est faux.
dev = [json.loads(l) for l in open("data/test/dev_fr_synthetique.jsonl", encoding="utf-8")]
queries = [d["text"] for d in dev[:12]]
qv = encode([query_text(q) for q in queries])
sims = qv.astype(np.float32) @ vectors.astype(np.float32).T
for q, s in list(zip(queries, sims))[:4]:
    print("REQUÊTE :", q[:110])
    for j in np.argsort(-s)[:3]:
        print(f"   {s[j]:.3f} [{rows[j]['source']}] {rows[j]['text'][:110]}")
json.dump({"task": TASK, "texts": queries, "vectors": qv.astype(np.float32).tolist()},
          open("/kaggle/working/check_queries.json", "w"), ensure_ascii=False)'''),
    ("code", '''# Reclassement : bge-reranker-v2-m3 sur les 20 passages les plus proches de chaque requête de contrôle
del model; torch.cuda.empty_cache()
rtok = AutoTokenizer.from_pretrained(RERANK_ID)
rmodel = AutoModelForSequenceClassification.from_pretrained(RERANK_ID, dtype=torch.float16).cuda().eval()
for q, s in list(zip(queries, sims))[:3]:
    cand = list(np.argsort(-s)[:20])
    enc = rtok([q] * len(cand), [rows[j]["text"] for j in cand], padding=True, truncation=True, max_length=512,
               return_tensors="pt").to("cuda")
    with torch.no_grad():
        sc = torch.sigmoid(rmodel(**enc).logits.view(-1).float()).cpu().numpy()
    print("REQUÊTE :", q[:110])
    for k in np.argsort(-sc)[:3]:
        print(f"   rerank {sc[k]:.3f} (vecteur {s[cand[k]]:.3f}) [{rows[cand[k]]['source']}] {rows[cand[k]]['text'][:100]}")'''),
    ("code", '''# Export des deux modèles (float16) pour le portable
rmodel.save_pretrained("/kaggle/working/bge-reranker-v2-m3"); rtok.save_pretrained("/kaggle/working/bge-reranker-v2-m3")
emb = AutoModel.from_pretrained(EMB_ID, dtype=torch.float16)
emb.save_pretrained("/kaggle/working/qwen3-embedding-0.6b")
AutoTokenizer.from_pretrained(EMB_ID).save_pretrained("/kaggle/working/qwen3-embedding-0.6b")
for name in ("qwen3-embedding-0.6b", "bge-reranker-v2-m3"):
    shutil.make_archive(f"/kaggle/working/{name}", "zip", f"/kaggle/working/{name}")
    shutil.rmtree(f"/kaggle/working/{name}")
!rm -rf /kaggle/working/dalil && ls -lh /kaggle/working'''),
]


def encoder(config: str) -> list[tuple[str, str]]:
    return [(k, src.replace("__CONFIG__", config)) for k, src in NB_ENCODER]


NOTEBOOKS = {
    "01_traduction": NB_TRANSLATE,
    "02_encodeur_fr": encoder("fr"),          # variante B sur textes traduits (après le carnet 01)
    "02_encodeur_enfr": encoder("en+fr"),     # variante B par transfert multilingue (sans traduction)
    "03_lora_llm": NB_LLM,
    "04_fusion_gguf": NB_FUSION,   # reprise après le 03 : évaluation, fusion, GGUF
    "05_vecteurs": NB_VECTEURS,    # étape 8 : vecteurs de recherche + modèle de reclassement
}


def notebook(cells: list[tuple[str, str]]) -> dict:
    out = []
    for kind, src in cells:
        cell = {"cell_type": "markdown" if kind == "md" else "code", "metadata": {}, "source": src.splitlines(keepends=True)}
        if kind == "code":
            cell.update(execution_count=None, outputs=[])
        out.append(cell)
    return {"cells": out, "nbformat": 4, "nbformat_minor": 5,
            "metadata": {"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"},
                         "language_info": {"name": "python"}, "kaggle": {"accelerator": "gpu", "isInternetEnabled": True}}}


def main() -> None:
    for name, cells in NOTEBOOKS.items():
        path = HERE / f"{name}.ipynb"
        path.write_text(json.dumps(notebook(cells), ensure_ascii=False, indent=1), encoding="utf-8")
        print("écrit", path)


if __name__ == "__main__":
    main()
