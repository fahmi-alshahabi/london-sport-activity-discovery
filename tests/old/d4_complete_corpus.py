"""
D4 COMPLETE — full recommender pipeline, now with a CORPUS-AWARE loader.

Reads across all 66 per-provider s1_records.jsonl files, with safety caps so the
1.9GB Better file / 750MB Everyone_Active file can't exhaust memory. Loads a
representative multi-provider slice (fixes the single-provider Hartlepool sample).

  query -> retrieve (BM25 + dense) -> fuse (RRF) -> gate (Michael's reducer) -> preference-rank

Needs in same folder: reducer_v0_1_1.py, d5_preference_model.py
Point CORPUS_DIR at the unzipped corpus (folder of per-provider directories).
"""
import json, re, math, random
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np

from reducer_v0_1_1 import reduce_decision, match_text, match_date_window
from d5_preference_model import PreferenceBelief, preference_score

# ============ CONFIG — tune these to control memory/time ============
CORPUS_DIR = "S1_CORPUS_V2026-08-27"          # folder containing per-provider directories
PER_PROVIDER_CAP = 2000            # max records per provider (caps the giant files)
SKIP_GIANTS_OVER_MB = 200          # skip provider files bigger than this (Better/Everyone Active)
TOTAL_CAP = None                   # optional overall ceiling (None = no limit)


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
    return {"item_id": record["item_id"], "text": text, "name": name,
            "provider": record.get("provenance", {}).get("source_feed", ""),
            "facets": card_facets(f), "_record": record}

def card_facets(f):
    import datetime
    cats = f.get("category") or []
    if isinstance(cats, dict): cats = [cats]
    labels = " ".join(c.get("prefLabel","") if isinstance(c,dict) else str(c) for c in cats).lower()
    if "swim" in labels: cat = "swim"
    elif "fitness" in labels or "gym" in labels: cat = "fitness suite"
    elif "junior" in labels: cat = "junior"
    elif "group" in labels: cat = "group exercise"
    elif "pool" in labels: cat = "leisure pool"
    else: cat = None
    day_t, time_t = None, None
    sd = f.get("startDate")
    if sd:
        try:
            d = datetime.datetime.fromisoformat(sd)
            day_t = "weekend" if d.weekday() >= 5 else "weekday"
            h = d.hour
            time_t = "morning" if 5<=h<12 else "afternoon" if 12<=h<17 else "evening"
        except (ValueError, TypeError): pass
    facets = {}
    if cat: facets["category"] = cat
    if day_t: facets["day_type"] = day_t
    if time_t: facets["time"] = time_t
    return facets


# ---------- CORPUS-AWARE LOADER ----------
def load_corpus_cards(corpus_dir=CORPUS_DIR, per_provider_cap=PER_PROVIDER_CAP,
                      total_cap=TOTAL_CAP, skip_giants_over_mb=SKIP_GIANTS_OVER_MB):
    """Load cards across every provider's s1_records.jsonl, with caps for safety."""
    files = sorted(Path(corpus_dir).glob("*/s1_records.jsonl"))
    cards, report = [], {}
    for rf in files:
        provider = rf.parent.name
        size_mb = rf.stat().st_size / 1048576
        if rf.stat().st_size == 0:
            report[provider] = 0; continue
        if skip_giants_over_mb and size_mb > skip_giants_over_mb:
            report[provider] = f"SKIPPED({size_mb:.0f}MB)"; continue
        n = 0
        with open(rf, encoding="utf-8") as f:
            for line in f:
                if per_provider_cap and n >= per_provider_cap: break
                if total_cap and len(cards) >= total_cap: break
                try: rec = json.loads(line)
                except json.JSONDecodeError: continue
                c = build_card(rec)
                if c["text"]: cards.append(c); n += 1
        report[provider] = n
        if total_cap and len(cards) >= total_cap: break
    return cards, report


# ---------- query -> constraints (Michael's matchers) ----------
def price_max_matcher(limit):
    def pred(offers):
        offers = offers if isinstance(offers, list) else [offers]
        prices = [o.get("price") for o in offers if isinstance(o, dict) and o.get("price") is not None]
        return bool(prices) and min(prices) <= limit
    return pred
def price_free_matcher(offers):
    offers = offers if isinstance(offers, list) else [offers]
    return any(o.get("price") == 0 for o in offers if isinstance(o, dict) and o.get("price") is not None)
def build_constraints(query):
    cons = []
    if query.get("activity"): cons.append(("category", match_text(query["activity"])))
    if query.get("region"):   cons.append(("location", match_text(query["region"])))
    if query.get("free"):     cons.append(("offers", price_free_matcher))
    elif query.get("max_price") is not None: cons.append(("offers", price_max_matcher(query["max_price"])))
    if query.get("date_from") and query.get("date_to"):
        cons.append(("startDate", match_date_window(query["date_from"], query["date_to"])))
    return cons


# ---------- R2: BM25 ----------
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


# ---------- Dense ----------
class DenseRetriever:
    def __init__(self, cards, model_name="all-MiniLM-L6-v2", cache_dir="embeddings"):
        from sentence_transformers import SentenceTransformer
        self.cards = cards; self.ids=[c["item_id"] for c in cards]
        self.model = SentenceTransformer(model_name)
        Path(cache_dir).mkdir(exist_ok=True)
        cache = Path(cache_dir)/f"corpus_{len(cards)}.npy"
        if cache.exists() and np.load(cache).shape[0]==len(cards):
            self.emb = np.load(cache)
        else:
            print(f"  embedding {len(cards):,} records (one-time, then cached)...")
            emb = self.model.encode([c["text"] for c in cards], normalize_embeddings=True,
                                    batch_size=64, show_progress_bar=True)
            self.emb = np.asarray(emb, dtype=np.float32); np.save(cache, self.emb)
    def search(self, query, top_k=100):
        q = np.asarray(self.model.encode([query], normalize_embeddings=True), dtype=np.float32)[0]
        sims = self.emb @ q; k=min(top_k,len(sims))
        idx = np.argpartition(-sims,k-1)[:k]; idx=idx[np.argsort(-sims[idx])]
        return [(self.ids[i], float(sims[i])) for i in idx]


# ---------- R3: RRF ----------
def rrf(rankings, k=60, top_k=100):
    fused=defaultdict(float)
    for ranking in rankings:
        for rank,(iid,_) in enumerate(ranking): fused[iid]+=1.0/(k+rank+1)
    return sorted(fused.items(), key=lambda x:x[1], reverse=True)[:top_k]


# ---------- pipeline ----------
def recommend(query, cards, bm25, dense, belief=None, top_k=10):
    qt = query.get("activity") or query.get("text") or ""
    cons = build_constraints(query)
    belief = belief or PreferenceBelief()
    r2 = bm25.search(qt, 100)
    rd = dense.search(qt, 100) if dense else []
    fused = rrf([r2, rd], top_k=100)
    by_id = {c["item_id"]: c for c in cards}
    results = []
    for iid, rs in fused:
        card = by_id[iid]
        decision, _ = reduce_decision(card["_record"], cons)
        results.append({"item_id": iid, "name": card["name"], "gate": decision,
                        "preference": round(preference_score(card["facets"], belief),3),
                        "retrieval": round(rs,4)})
    order = {"supported_match":0, "evidence_indeterminate":1, "bounded_non_match":2}
    results.sort(key=lambda r: (order.get(r["gate"],3), -r["preference"], -r["retrieval"]))
    return results[:top_k]


if __name__ == "__main__":
    print("Loading corpus (representative slice, giants skipped)...")
    cards, report = load_corpus_cards()
    n_prov = sum(1 for v in report.values() if isinstance(v,int) and v>0)
    skipped = [k for k,v in report.items() if isinstance(v,str)]
    print(f"  {len(cards):,} cards from {n_prov} providers "
          f"({sum(1 for v in report.values() if v==0)} empty, {len(skipped)} giants skipped)")
    print(f"  giants skipped: {skipped}")

    print("Building BM25...")
    bm25 = BM25(cards)
    print("Building dense embeddings...")
    dense = DenseRetriever(cards)

    belief = PreferenceBelief(); belief.update("category","swim")
    query = {"activity":"swimming", "date_from":"2026-08-01", "date_to":"2026-09-30"}
    print(f"\nQuery: swimming | user prefers swim\n")
    print(f"  {'gate':22s} {'pref':>5s} {'retr':>7s}  name")
    print("  " + "-"*60)
    for r in recommend(query, cards, bm25, dense, belief, top_k=12):
        print(f"  {r['gate']:22s} {r['preference']:>5.2f} {r['retrieval']:>7.4f}  {r['name']}")
