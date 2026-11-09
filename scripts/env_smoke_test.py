#!/usr/bin/env python
"""Environment smoke test. Per-check status: PASS / WARN / FAIL / SKIP. Writes results/env_smoke/*.json.
Numbers printed here are plumbing checks on a tiny sample, NOT experimental results."""
import argparse, json, os, platform, random, re, shutil, subprocess, sys, time, traceback
from collections import Counter
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from scifact_verif.seed import set_seed

SEED, N_SMOKE, TOP_K = 42, 20, 5
RESULTS, STATE = [], {}

def record(name, status, detail=""):
    RESULTS.append({"check": name, "status": status, "detail": detail})
    print(f"[{status:4}] {name}" + (f" :: {detail}" if detail else ""), flush=True)

def check(name):
    def deco(fn):
        def run(*a, **k):
            try:
                out = fn(*a, **k)
                status, detail = out if isinstance(out, tuple) else ("PASS", out or "")
            except Exception as e:
                status, detail = "FAIL", f"{type(e).__name__}: {e}"
                traceback.print_exc(limit=4)
            record(name, status, detail)
        return run
    return deco

def ver(pkg):
    try: return metadata.version(pkg)
    except metadata.PackageNotFoundError: return None

def jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]

def toks(text):  # smoke-only tokenizer; the frozen BM25 tokenizer is decided at the freeze gate
    return re.findall(r"\w+", text.lower())

def top_k(scores, doc_ids, k=TOP_K):  # tie-break: ascending doc_id (Prompt07 §4A)
    order = sorted(range(len(doc_ids)), key=lambda i: (-float(scores[i]), doc_ids[i]))[:k]
    return [(doc_ids[i], float(scores[i])) for i in order]

# ---------------------------------------------------------------- 1. versions / system
@check("packages")
def c_packages():
    core = ["numpy", "scipy", "scikit-learn", "rank-bm25", "pyyaml"]
    opt = ["pandas", "psutil", "torch", "transformers", "sentencepiece", "tqdm", "matplotlib"]
    v = {p: ver(p) for p in core + opt}
    STATE["versions"] = v
    print("   " + ", ".join(f"{p}={x or 'MISSING'}" for p, x in v.items()))
    miss = [p for p in core if not v[p]]
    if miss: return "FAIL", f"missing core packages: {miss}"
    miss_o = [p for p in ["torch", "transformers", "sentencepiece"] if not v[p]]
    return ("WARN", f"NLI deps missing: {miss_o}") if miss_o else "all present"

@check("system")
def c_system():
    ram = None
    try:
        import psutil; ram = round(psutil.virtual_memory().total / 2**30, 1)
    except ImportError: pass
    info = {"python": sys.version.split()[0], "platform": platform.platform(), "cpus": os.cpu_count(),
            "ram_gb": ram, "disk_free_gb": round(shutil.disk_usage(ROOT).free / 2**30, 1),
            "colab": "google.colab" in sys.modules or bool(os.environ.get("COLAB_RELEASE_TAG"))}
    STATE["system"] = info
    return json.dumps(info)

@check("gpu")
def c_gpu():
    smi = shutil.which("nvidia-smi")
    if smi:
        out = subprocess.run([smi, "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"],
                             capture_output=True, text=True).stdout.strip()
        print("   nvidia-smi:", out)
    import torch
    info = {"torch": torch.__version__, "torch_cuda_build": torch.version.cuda,
            "cuda_available": torch.cuda.is_available(), "cudnn": torch.backends.cudnn.version()}
    if torch.cuda.is_available():
        info.update(device=torch.cuda.get_device_name(0), capability=torch.cuda.get_device_capability(0),
                    vram_gb=round(torch.cuda.get_device_properties(0).total_memory / 2**30, 1))
        x = torch.randn(256, 256, device="cuda"); y = (x @ x).sum().item()  # real kernel launch
        info["matmul_ok"] = bool(y == y)
    STATE["gpu"] = info
    if not info["cuda_available"]:
        return "WARN", "CUDA unavailable -> NLI runs on CPU (slow); " + json.dumps(info)
    return json.dumps(info)

# ---------------------------------------------------------------- 2. seeds
@check("seed_reproducibility")
def c_seed():
    import numpy as np
    from sklearn.datasets import make_classification
    from sklearn.linear_model import LogisticRegression
    def draw():
        s = set_seed(SEED)
        d = [random.random(), np.random.rand(3).tolist()]
        try:
            import torch
            d.append(torch.rand(3).tolist())
            if torch.cuda.is_available(): d.append(torch.rand(3, device="cuda").cpu().tolist())
        except ImportError: pass
        X, y = make_classification(n_samples=200, n_features=10, random_state=SEED)
        d.append(LogisticRegression(max_iter=500, random_state=SEED).fit(X, y).coef_.round(10).tolist())
        return d, s
    a, info = draw(); b, _ = draw()
    STATE["seed_info"] = info
    return ("PASS", json.dumps(info)) if a == b else ("FAIL", "two seeded runs differ")

# ---------------------------------------------------------------- 3. data audit
@check("data_audit")
def c_data(data_dir):
    root = Path(data_dir)
    corp = next(root.rglob("corpus.jsonl"), None)
    if corp is None: return "SKIP", f"no corpus.jsonl under {root}; run scripts/01_download_data.sh"
    d = corp.parent
    corpus = jsonl(corp)
    splits = {s: jsonl(d / f"claims_{s}.jsonl") for s in ["train", "dev", "test"] if (d / f"claims_{s}.jsonl").exists()}
    if "train" not in splits or "dev" not in splits: return "FAIL", f"claims_train/dev missing in {d}"
    ck = Counter(k for c in corpus for k in c)
    print(f"   corpus: n={len(corpus)} keys={dict(ck)} doc_id type={type(corpus[0]['doc_id']).__name__} "
          f"dup_ids={len(corpus) - len({c['doc_id'] for c in corpus})}")
    by_id = {str(c["doc_id"]): c for c in corpus}
    def label(c):  # smoke-only gold-label rule; the audited label map is frozen later
        L = {e["label"] for items in (c.get("evidence") or {}).values() for e in items}
        return "NOT_ENOUGH_INFO" if not L else (next(iter(L)) if len(L) == 1 else "MIXED")
    miss_ref = 0
    for s, cl in splits.items():
        keys = Counter(k for c in cl for k in c)
        ids = [c["id"] for c in cl]
        line = f"   {s}: n={len(cl)} keys={dict(keys)} id type={type(ids[0]).__name__} dup_ids={len(ids)-len(set(ids))}"
        if s != "test":
            labs = Counter(label(c) for c in cl)
            n_ev = sum(1 for c in cl if c.get("evidence"))
            line += f" labels={dict(labs)} with_nonempty_evidence={n_ev}"
            miss_ref += sum(1 for c in cl for k in (c.get("evidence") or {}) if k not in by_id)
        print(line)
    print(f"   evidence doc ids absent from corpus: {miss_ref}")
    rnd = random.Random(SEED)
    for s in ["dev"]:
        for c in rnd.sample(splits[s], 2): print(f"   sample {s}:", json.dumps(c)[:300])
    print("   sample corpus:", json.dumps(rnd.choice(corpus))[:300])
    STATE.update(corpus=corpus, by_id=by_id, splits=splits, label=label)
    return ("WARN", f"{miss_ref} evidence docs missing from corpus") if miss_ref else f"data dir {d}"

def gold_text(c):
    out = []
    for did, items in (c.get("evidence") or {}).items():
        sents = STATE["by_id"][did]["abstract"]
        for e in items:
            for i in e["sentences"]: out.append(sents[i])
    return " ".join(out)

def smoke_claims():
    dev = [c for c in STATE["splits"]["dev"] if STATE["label"](c) != "MIXED"]
    return random.Random(SEED).sample(dev, min(N_SMOKE, len(dev)))

# ---------------------------------------------------------------- 4. methods
@check("tfidf_logreg")
def c_lr():
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    tr = [c for c in STATE["splits"]["train"] if STATE["label"](c) != "MIXED"]
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=100000)  # fit on TRAIN claims only
    Xtr = vec.fit_transform([c["claim"] for c in tr])
    clf = LogisticRegression(max_iter=2000, random_state=SEED).fit(Xtr, [STATE["label"](c) for c in tr])
    sm = smoke_claims()
    P = clf.predict_proba(vec.transform([c["claim"] for c in sm]))
    print(f"   train n={len(tr)} X.shape={Xtr.shape} class order={list(clf.classes_)} proba.shape={P.shape}")
    for c, p in list(zip(sm, P))[:5]:
        print(f"   claim {c['id']}: gold={STATE['label'](c)} pred={clf.classes_[p.argmax()]} p={p.round(3).tolist()}")
    assert P.shape == (len(sm), len(clf.classes_)) and abs(P.sum(1) - 1).max() < 1e-6
    return f"{len(sm)} smoke claims scored (plumbing only)"

@check("condition_inputs_ABC_and_bm25")
def c_bm25():
    from rank_bm25 import BM25Okapi
    corpus = STATE["corpus"]
    ids = [str(c["doc_id"]) for c in corpus]
    text = {str(c["doc_id"]): c["title"] + " " + " ".join(c["abstract"]) for c in corpus}
    t0 = time.perf_counter(); bm = BM25Okapi([toks(text[i]) for i in ids]); t_idx = time.perf_counter() - t0
    sm = smoke_claims(); t0 = time.perf_counter()
    run = {c["id"]: top_k(bm.get_scores(toks(c["claim"])), ids) for c in sm}   # query = claim text ONLY
    t_ret = time.perf_counter() - t0
    bad = [d for r in run.values() for d, _ in r if d not in STATE["by_id"]]
    withgold = [c for c in sm if c.get("evidence")]
    hits = sum(any(d in c["evidence"] for d, _ in run[c["id"]]) for c in withgold)
    c0 = withgold[0] if withgold else sm[0]
    B = f"CLAIM: {c0['claim']}\nEVIDENCE: {gold_text(c0)}"
    C = f"CLAIM: {c0['claim']}\nEVIDENCE: " + " || ".join(text[d][:150] for d, _ in run[c0['id']])
    print(f"   index {t_idx:.1f}s, retrieval {t_ret:.2f}s for {len(sm)} claims; invalid ids={len(bad)}")
    print(f"   example top5 claim {c0['id']}: {[(d, round(s, 2)) for d, s in run[c0['id']]]}")
    print(f"   input B (gold) preview: {B[:200]!r}\n   input C (retrieved) preview: {C[:200]!r}")
    print(f"   smoke sample hit@5 plumbing: {hits}/{len(withgold)} claims with gold evidence (NOT a result)")
    STATE["text"], STATE["ids"] = text, ids
    if bad: return "FAIL", f"{len(bad)} retrieved ids not in corpus"
    if len(withgold) >= 5 and hits == 0: return "WARN", "0 hits on >=5 gold claims: suspect doc-id type mismatch (str vs int)"
    return "PASS", f"top-{TOP_K} ids valid; B/C inputs constructed"

@check("tfidf_retrieval")
def c_tfidf_ret():
    from sklearn.feature_extraction.text import TfidfVectorizer
    ids, text = STATE["ids"], STATE["text"]
    vec = TfidfVectorizer(ngram_range=(1, 2), norm="l2")                      # fit on corpus text ONLY
    t0 = time.perf_counter(); M = vec.fit_transform([text[i] for i in ids]); t_fit = time.perf_counter() - t0
    sm = smoke_claims(); Q = vec.transform([c["claim"] for c in sm])
    S = (Q @ M.T).toarray()                                                    # cosine (both L2-normalised)
    runs = [top_k(S[i], ids) for i in range(len(sm))]
    print(f"   fit {t_fit:.1f}s, matrix {M.shape}, example top5 claim {sm[0]['id']}: {[(d, round(s, 3)) for d, s in runs[0]]}")
    assert all(d in STATE["by_id"] for r in runs for d, _ in r)
    return "top-5 ids valid"

# ---------------------------------------------------------------- 5. NLI (secondary)
@check("nli_deberta")
def c_nli(model_name="cross-encoder/nli-deberta-v3-base"):
    try:
        import torch, transformers
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
    except ImportError as e:
        return "SKIP", f"missing dependency: {e}"
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    set_seed(SEED)
    t0 = time.perf_counter()
    tok = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name).to(dev).eval()
    t_load = time.perf_counter() - t0
    id2label = {int(k): v for k, v in model.config.id2label.items()}
    print(f"   revision={getattr(model.config, '_commit_hash', None)} id2label={id2label} load={t_load:.1f}s device={dev}")
    low = {v.lower() for v in id2label.values()}
    if not {"entailment", "contradiction", "neutral"} <= low:
        return "FAIL", f"unexpected label names {id2label}; do not apply the Prompt07 mapping"
    pairs = [("Aspirin reduces the risk of heart attack in adults.", "Aspirin lowers heart attack risk."),
             ("Aspirin reduces the risk of heart attack in adults.", "Aspirin increases heart attack risk."),
             ("The study enrolled 200 patients in Denmark.", "Chocolate improves memory."),
             ("Vitamin D supplementation had no effect on fracture rates.", "Vitamin D prevents fractures.")]
    enc = tok([p for p, _ in pairs], [h for _, h in pairs], truncation=True, max_length=256,
              padding=True, return_tensors="pt").to(dev)                       # premise = evidence, hypothesis = claim
    full = tok([p for p, _ in pairs], [h for _, h in pairs])["input_ids"]
    trunc = [len(x) > 256 for x in full]
    if dev == "cuda": torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
    t0 = time.perf_counter()
    with torch.no_grad(): probs = torch.softmax(model(**enc).logits, -1).cpu()
    if dev == "cuda": torch.cuda.synchronize()
    t_inf = time.perf_counter() - t0
    peak = round(torch.cuda.max_memory_allocated() / 2**20, 1) if dev == "cuda" else None
    print(f"   logits/probs shape={tuple(probs.shape)} batch=4 max_len=256 inference={t_inf*1000:.0f}ms peak_vram_mb={peak} truncated={trunc}")
    for (p, h), pr in zip(pairs, probs):
        print(f"   {h!r}: " + ", ".join(f"{id2label[i]}={pr[i]:.3f}" for i in range(len(id2label))))
    assert probs.shape == (4, len(id2label)) and (probs.sum(1) - 1).abs().max() < 1e-4
    return "PASS", f"model loads, labels read from config, forward pass ok on {dev}"

# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default=str(ROOT / "data/raw/scifact"))
    ap.add_argument("--skip-nli", action="store_true")
    a = ap.parse_args()
    print(f"=== env smoke test {datetime.now(timezone.utc).isoformat()} root={ROOT} ===")
    c_packages(); c_system(); c_gpu(); c_seed(); c_data(a.data_dir)
    if "corpus" in STATE: c_lr(); c_bm25(); c_tfidf_ret()
    else:
        for n in ["tfidf_logreg", "condition_inputs_ABC_and_bm25", "tfidf_retrieval"]: record(n, "SKIP", "no data")
    c_nli() if not a.skip_nli else record("nli_deberta", "SKIP", "--skip-nli")
    out = ROOT / "results/env_smoke"; out.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    (out / f"env_report_{ts}.json").write_text(json.dumps(
        {"timestamp_utc": ts, "seed": SEED, "versions": STATE.get("versions"), "system": STATE.get("system"),
         "gpu": STATE.get("gpu"), "results": RESULTS}, indent=2, default=str))
    (out / f"pip_freeze_{ts}.txt").write_text(subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True).stdout)
    print("\n=== SUMMARY ==="); [print(f"{r['status']:5} {r['check']}") for r in RESULTS]
    n_fail = sum(r["status"] == "FAIL" for r in RESULTS)
    print(f"OVERALL: {'FAIL (' + str(n_fail) + ')' if n_fail else 'NO FAILURES (review WARN/SKIP manually)'}  report={out}/env_report_{ts}.json")
    sys.exit(1 if n_fail else 0)

if __name__ == "__main__":
    main()