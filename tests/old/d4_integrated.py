"""
D4 pipeline with Michael's REAL reducer (reducer_v0_1_1.py) wired in,
replacing the stub gate. Retrieval (BM25+dense+RRF) unchanged.

Needs in the same folder: sample_100_records.jsonl, reducer_v0_1_1.py
"""
import json, re, math
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np

# >>> Michael's real reducer — the R1 gate <<<
from reducer_v0_1_1 import reduce_decision, match_text, match_date_window


# ---------- ACTIVITY CARD (unchanged) ----------
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
    return {"item_id": record["item_id"], "text": text, "name": name, "_record": record}

def load_cards(path):
    cards = []
    for line in open(path, encoding="utf-8"):
        c = build_card(json.loads(line))
        if c["text"]: cards.append(c)
    return cards


# ---------- R2: BM25 (unchanged) ----------
_TOKEN = re.compile(r"[a-z0-9]+")
def tokenize(s): return _TOKEN.findall(s.lower())
class BM25:
    def __init__(self, cards, k1=1.5, b=0.75):
        self.cards, self.k1, self.b = cards, k1, b
        self.docs = [tokenize(c["text"]) for c in cards]
        self.N = len(self.docs); self.avgdl = sum(len(d) for d in self.docs)/max(1,self.N)
        df = Counter()
        for d in self.docs:
            for t in set(d): df[t]+=1
        self.idf = {t: math.log(1+(self.N-n+0.5)/(n+0.5)) for t,n in df.items()}
        self.tf = [Counter(d) for d in self.docs]
    def search(self, query, top_k=100):
        q = tokenize(query); out=[]
        for i,tf in enumerate(self.tf):
            dl=len(self.docs[i]); s=0.0
            for term in q:
                if term not in tf: continue
                f=tf[term]; s+=self.idf.get(term,0.0)*(f*(self.k1+1))/(f+self.k1*(1-self.b+self.b*dl/self.avgdl))
            if s>0: out.append((i,s))
        out.sort(key=lambda x:x[1], reverse=True)
        return [(self.cards[i]["item_id"], sc) for i,sc in out[:top_k]]


# ---------- Dense (unchanged) ----------
class DenseRetriever:
    def __init__(self, cards, model_name="all-MiniLM-L6-v2", cache_dir="embeddings"):
        from sentence_transformers import SentenceTransformer
        self.cards = cards; self.ids=[c["item_id"] for c in cards]
        self.model = SentenceTransformer(model_name)
        Path(cache_dir).mkdir(exist_ok=True)
        cache = Path(cache_dir)/f"cards_{model_name.replace('/','_')}_{len(cards)}.npy"
        if cache.exists() and np.load(cache).shape[0]==len(cards):
            self.emb = np.load(cache)
        else:
            emb = self.model.encode([c["text"] for c in cards], normalize_embeddings=True, batch_size=64)
            self.emb = np.asarray(emb, dtype=np.float32); np.save(cache, self.emb)
    def search(self, query, top_k=100):
        q = np.asarray(self.model.encode([query], normalize_embeddings=True), dtype=np.float32)[0]
        sims = self.emb @ q; k=min(top_k,len(sims))
        idx = np.argpartition(-sims,k-1)[:k]; idx=idx[np.argsort(-sims[idx])]
        return [(self.ids[i], float(sims[i])) for i in idx]


# ---------- R3: RRF (unchanged) ----------
def rrf(rankings, k=60, top_k=100):
    fused=defaultdict(float)
    for ranking in rankings:
        for rank,(iid,_) in enumerate(ranking): fused[iid]+=1.0/(k+rank+1)
    return sorted(fused.items(), key=lambda x:x[1], reverse=True)[:top_k]


# ---------- D4 pipeline: now calls Michael's reduce_decision ----------
def d4_search(query_text, constraints, cards, bm25, dense, top_k=20):
    """constraints: list of (field, predicate) tuples — Michael's reducer format."""
    r2 = bm25.search(query_text, 100)
    rd = dense.search(query_text, 100) if dense else []
    fused = rrf([r2, rd], top_k=100)
    by_id = {c["item_id"]: c for c in cards}
    out = []
    for iid, sc in fused[:top_k]:
        card = by_id[iid]
        decision, detail = reduce_decision(card["_record"], constraints)   # <-- REAL gate
        out.append({"item_id": iid, "name": card["name"],
                    "rank_score": round(sc,4), "gate": decision})
    return out


if __name__ == "__main__":
    cards = load_cards("sample_100_records.jsonl")
    print(f"loaded {len(cards)} cards, using Michael's reduce_decision as R1\n")
    bm25 = BM25(cards)

    # query: swim sessions in July 2026, using HIS matchers
    constraints = [
        ("location", match_text("mill house")),
        ("startDate", match_date_window("2026-07-01", "2026-07-31")),
    ]
    # BM25 only (skip dense here so it runs without the model download in this demo)
    class NoDense:
        def search(self, q, top_k=100): return []
    for r in d4_search("swim", constraints, cards, bm25, NoDense(), top_k=10):
        print(f"  {r['rank_score']:.4f}  [{r['gate']:22s}]  {r['name']}")
