"""
D4 HYBRID retrieval pipeline — BM25 (R2) + dense bi-encoder + RRF (R3) + R1 gate stub.
Built against Michael's D4 input contract v0.1, over sample_100_records.jsonl.

Run:  python d4_hybrid_pipeline.py
(needs sample_100_records.jsonl in the same folder)
"""

import json, re, math
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np


# ---------- ACTIVITY CARD ----------
def build_card(record):
    f = record.get("fields", {}) or {}
    name = f.get("name") or ""
    cats = f.get("category") or []
    if isinstance(cats, dict): cats = [cats]
    cat_labels = [c.get("prefLabel", c) if isinstance(c, dict) else str(c) for c in cats] \
        if isinstance(cats, list) else [str(cats)]
    loc = f.get("location") or {}
    loc_name = loc.get("name", "") if isinstance(loc, dict) else ""
    instructions = f.get("attendeeInstructions") or ""
    text = " ".join(str(p) for p in [name, " ".join(map(str, cat_labels)), loc_name, instructions] if p).strip()
    geo = loc.get("geo", {}) if isinstance(loc, dict) else {}
    offers = f.get("offers") or []
    if isinstance(offers, dict): offers = [offers]
    prices = [o.get("price") for o in offers if isinstance(o, dict) and o.get("price") is not None]
    is_free = None if not prices else all(float(p) == 0 for p in prices)
    return {"item_id": record["item_id"],
            "source_feed": record.get("provenance", {}).get("source_feed"),
            "text": text, "name": name, "location_name": loc_name,
            "lat": geo.get("latitude"), "lng": geo.get("longitude"),
            "start": f.get("startDate"), "is_free": is_free, "_record": record}

def load_cards(path):
    cards = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            c = build_card(rec)
            if c["text"]: cards.append(c)
    return cards


# ---------- R2: BM25 ----------
_TOKEN = re.compile(r"[a-z0-9]+")
def tokenize(s): return _TOKEN.findall(s.lower())

class BM25:
    def __init__(self, cards, k1=1.5, b=0.75):
        self.cards, self.k1, self.b = cards, k1, b
        self.docs = [tokenize(c["text"]) for c in cards]
        self.N = len(self.docs)
        self.avgdl = sum(len(d) for d in self.docs) / max(1, self.N)
        df = Counter()
        for d in self.docs:
            for t in set(d): df[t] += 1
        self.idf = {t: math.log(1 + (self.N - n + 0.5)/(n + 0.5)) for t, n in df.items()}
        self.tf = [Counter(d) for d in self.docs]
    def search(self, query, top_k=100):
        q = tokenize(query); scores = []
        for i, tf in enumerate(self.tf):
            dl = len(self.docs[i]); s = 0.0
            for term in q:
                if term not in tf: continue
                f = tf[term]
                s += self.idf.get(term, 0.0) * (f*(self.k1+1)) / (f + self.k1*(1 - self.b + self.b*dl/self.avgdl))
            if s > 0: scores.append((i, s))
        scores.sort(key=lambda x: x[1], reverse=True)
        return [(self.cards[i]["item_id"], sc) for i, sc in scores[:top_k]]


# ---------- Dense bi-encoder ----------
class DenseRetriever:
    def __init__(self, cards, model_name="all-MiniLM-L6-v2", cache_dir="embeddings"):
        from sentence_transformers import SentenceTransformer
        self.cards = cards
        self.ids = [c["item_id"] for c in cards]
        self.model = SentenceTransformer(model_name)
        Path(cache_dir).mkdir(exist_ok=True)
        cache = Path(cache_dir) / f"cards_{model_name.replace('/', '_')}_{len(cards)}.npy"
        if cache.exists() and np.load(cache).shape[0] == len(cards):
            self.emb = np.load(cache)
        else:
            texts = [c["text"] for c in cards]
            emb = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=True, batch_size=64)
            self.emb = np.asarray(emb, dtype=np.float32)
            np.save(cache, self.emb)
    def search(self, query, top_k=100):
        q = np.asarray(self.model.encode([query], normalize_embeddings=True), dtype=np.float32)[0]
        sims = self.emb @ q
        k = min(top_k, len(sims))
        idx = np.argpartition(-sims, k-1)[:k]
        idx = idx[np.argsort(-sims[idx])]
        return [(self.ids[i], float(sims[i])) for i in idx]


# ---------- R3: RRF ----------
def rrf(rankings, k=60, top_k=100):
    fused = defaultdict(float)
    for ranking in rankings:
        for rank, (iid, _) in enumerate(ranking):
            fused[iid] += 1.0 / (k + rank + 1)
    return sorted(fused.items(), key=lambda x: x[1], reverse=True)[:top_k]


# ---------- R1 gate stub (Michael's reducer drops in here) ----------
_LINEAGE_TO_STATE = {"ON_CHILD":"T","CHILD_OVERRIDES":"T","BOTH_EQUAL":"T","INHERITED":"T",
                     "SOURCE_ABSENT":"U","UNRESOLVABLE_PARENT_UNAVAILABLE":"U"}
def evidence_state(record, field):
    meta = (record.get("lineage", {}) or {}).get(field)
    return _LINEAGE_TO_STATE.get(meta.get("class"), "U") if isinstance(meta, dict) else "U"

def r1_gate(query_constraints, card):
    record = card["_record"]; any_u = False
    for field, satisfied in query_constraints.items():
        st = evidence_state(record, field)
        val = record.get("fields", {}).get(field)
        if st == "T":
            if not satisfied(val): return "bounded_non_match"
        else:
            any_u = True
    return "evidence_indeterminate" if any_u else "supported_match"


# ---------- D4 pipeline ----------
def d4_search(query_text, query_constraints, cards, bm25, dense, top_k=20):
    r2 = bm25.search(query_text, 100)
    rd = dense.search(query_text, 100)
    fused = rrf([r2, rd], top_k=100)
    by_id = {c["item_id"]: c for c in cards}
    return [{"item_id": iid, "name": by_id[iid]["name"],
             "rank_score": round(sc, 4), "gate": r1_gate(query_constraints, by_id[iid])}
            for iid, sc in fused][:top_k]


if __name__ == "__main__":
    cards = load_cards("sample_100_records.jsonl")
    print(f"loaded {len(cards)} cards")
    bm25 = BM25(cards)
    print("building dense embeddings (first run downloads the model ~80MB)...")
    dense = DenseRetriever(cards)

    # THE KEY TEST: a query that does NOT use the literal words
    q = "beginner fitness class"
    print(f"\n=== '{q}' — semantic query, words NOT in the data ===\n")
    print("BM25 (keyword) top 5:")
    b = bm25.search(q, 5)
    for iid, s in b:
        print(f"  {s:.3f}  {next(c['name'] for c in cards if c['item_id']==iid)}")
    if not b: print("  (nothing — BM25 found no keyword match)")
    print("\nDense (semantic) top 5:")
    for iid, s in dense.search(q, 5):
        print(f"  {s:.3f}  {next(c['name'] for c in cards if c['item_id']==iid)}")

    print("\n=== full hybrid pipeline: 'swimming lessons' (no constraints) ===\n")
    for r in d4_search("swimming lessons", {}, cards, bm25, dense, top_k=8):
        print(f"  {r['rank_score']:.4f}  [{r['gate']:22s}]  {r['name']}")
