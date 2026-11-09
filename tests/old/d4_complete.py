"""
D4 COMPLETE — the full recommender pipeline, end to end.

  query (plain dict)
    -> retrieve   : BM25 + dense bi-encoder
    -> fuse       : RRF
    -> gate (R1)  : Michael's reduce_decision (evidence eligibility)
    -> rank       : D5 Bayesian preference_score (preference ordering)
    -> results

Combines: item 1 (query->constraints wired to Michael's matchers) and
          item 2 (D5 preference ranking wired into D4's final step).

Needs in same folder: sample_100_records.jsonl, reducer_v0_1_1.py, d5_preference_model.py
"""
import json, re, math
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np

from reducer_v0_1_1 import reduce_decision, match_text, match_date_window
from d5_preference_model import PreferenceBelief, preference_score


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
            "facets": card_facets(f), "_record": record}

def card_facets(f):
    """Extract the D5 preference facets from a record's fields (for preference_score)."""
    import datetime
    cats = f.get("category") or []
    if isinstance(cats, dict): cats = [cats]
    labels = " ".join(c.get("prefLabel","") if isinstance(c,dict) else str(c) for c in cats).lower()
    # map to D5 category vocabulary
    if "swim" in labels: cat = "swim"
    elif "fitness" in labels or "gym" in labels: cat = "fitness suite"
    elif "junior" in labels: cat = "junior"
    elif "group" in labels: cat = "group exercise"
    elif "pool" in labels: cat = "leisure pool"
    else: cat = None
    # day + time from startDate
    day_t, time_t = None, None
    sd = f.get("startDate")
    if sd:
        try:
            d = datetime.datetime.fromisoformat(sd)
            day_t = "weekend" if d.weekday() >= 5 else "weekday"
            h = d.hour
            time_t = "morning" if 5 <= h < 12 else "afternoon" if 12 <= h < 17 else "evening"
        except (ValueError, TypeError):
            pass
    facets = {}
    if cat: facets["category"] = cat
    if day_t: facets["day_type"] = day_t
    if time_t: facets["time"] = time_t
    return facets

def load_cards(path):
    cards = []
    for line in open(path, encoding="utf-8"):
        c = build_card(json.loads(line))
        if c["text"]: cards.append(c)
    return cards


# ---------- ITEM 1: query -> constraints (using Michael's matchers) ----------
def price_max_matcher(limit):
    """Numeric price predicate (Michael's match_text can't do '<= £6')."""
    def pred(offers_value):
        offers = offers_value if isinstance(offers_value, list) else [offers_value]
        prices = [o.get("price") for o in offers if isinstance(o, dict) and o.get("price") is not None]
        return bool(prices) and min(prices) <= limit
    return pred

def price_free_matcher(offers_value):
    offers = offers_value if isinstance(offers_value, list) else [offers_value]
    return any(o.get("price") == 0 for o in offers if isinstance(o, dict) and o.get("price") is not None)

def build_constraints(query):
    """Plain query dict -> [(field, predicate)] in Michael's reducer format.
       Text facets use HIS match_text; price uses our numeric predicate; dates use HIS window."""
    cons = []
    if query.get("activity"):
        cons.append(("category", match_text(query["activity"])))      # his matcher
    if query.get("region"):
        cons.append(("location", match_text(query["region"])))        # his matcher (deep)
    if query.get("free"):
        cons.append(("offers", price_free_matcher))
    elif query.get("max_price") is not None:
        cons.append(("offers", price_max_matcher(query["max_price"])))
    if query.get("date_from") and query.get("date_to"):
        cons.append(("startDate", match_date_window(query["date_from"], query["date_to"])))  # his matcher
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


# ---------- R3: RRF ----------
def rrf(rankings, k=60, top_k=100):
    fused=defaultdict(float)
    for ranking in rankings:
        for rank,(iid,_) in enumerate(ranking): fused[iid]+=1.0/(k+rank+1)
    return sorted(fused.items(), key=lambda x:x[1], reverse=True)[:top_k]


# ---------- THE COMPLETE PIPELINE ----------
def recommend(query, cards, bm25, dense, belief=None, top_k=10):
    """Full D4: retrieve -> fuse -> gate (Michael) -> preference-rank (D5)."""
    query_text = query.get("activity") or query.get("text") or ""
    constraints = build_constraints(query)                    # ITEM 1
    belief = belief or PreferenceBelief()

    # retrieve + fuse
    r2 = bm25.search(query_text, 100)
    rd = dense.search(query_text, 100) if dense else []
    fused = rrf([r2, rd], top_k=100)
    by_id = {c["item_id"]: c for c in cards}

    results = []
    for iid, retr_score in fused:
        card = by_id[iid]
        decision, detail = reduce_decision(card["_record"], constraints)   # Michael's gate
        pref = preference_score(card["facets"], belief)                    # ITEM 2: D5 preference
        results.append({"item_id": iid, "name": card["name"],
                        "gate": decision, "preference": round(pref, 3),
                        "retrieval": round(retr_score, 4)})

    # RANK: supported first, then by preference, then by retrieval
    order = {"supported_match": 0, "evidence_indeterminate": 1, "bounded_non_match": 2}
    results.sort(key=lambda r: (order.get(r["gate"], 3), -r["preference"], -r["retrieval"]))
    return results[:top_k]


if __name__ == "__main__":
    cards = load_cards("sample_100_records.jsonl")
    print(f"loaded {len(cards)} cards\n")
    bm25 = BM25(cards)
    dense = DenseRetriever(cards)          # real semantic retrieval (embeds + caches)

    # a user who wants swimming, on a weekend, in the morning
    belief = PreferenceBelief()
    belief.update("category", "swim")
    belief.update("day_type", "weekend")
    belief.update("time", "morning")

    query = {"activity": "swim", "date_from": "2026-08-01", "date_to": "2026-08-31"}
    print("Query: swimming in Aug 2026 | user prefers weekend mornings\n")
    print(f"  {'gate':22s} {'pref':>5s} {'retr':>7s}  name")
    print("  " + "-"*60)
    for r in recommend(query, cards, bm25, dense, belief, top_k=12):
        print(f"  {r['gate']:22s} {r['preference']:>5.2f} {r['retrieval']:>7.4f}  {r['name']}")
