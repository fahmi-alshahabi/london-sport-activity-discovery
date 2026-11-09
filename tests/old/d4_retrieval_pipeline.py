"""
D4 retrieval/reranking pipeline — built against Michael's D4 input contract v0.1.

Structure follows the contract's "build rule for Wesley":
  R2 (BM25)  — text matching, built against §1 records directly. NO dependency.
  R3 (RRF)   — rank fusion, combines rankings. NO dependency.
  R1 (gate)  — evidence gate, built as a THREE-STRING INTERFACE STUB per §3.
               Michael's reducer_v0_1.py (due 3-4 Sep) drops in behind it
               WITHOUT changing this code.

Neuro-symbolic boundary (contract §2/§3, and the proposal): R2/R3 only RANK.
R1 alone decides eligibility, using Michael's evidence states. This code never
decides what is "true" about a session — it ranks candidates and calls the gate.
"""

import json
import re
import math
from pathlib import Path
from collections import defaultdict, Counter


# =====================================================================
#  ACTIVITY CARD — the retrieval document (source-swappable)
#  Built from an S1 record. Same builder works for the sample today and
#  the full 737k corpus later — nothing downstream changes.
# =====================================================================
def build_card(record):
    """Turn one S1 record (contract §1 shape) into a retrieval card."""
    f = record.get("fields", {}) or {}

    # --- searchable text: concatenate the human-meaningful fields ---
    name = f.get("name") or ""
    # category is often a list of {prefLabel} or strings
    cats = f.get("category") or []
    if isinstance(cats, dict):
        cats = [cats]
    cat_labels = [c.get("prefLabel", c) if isinstance(c, dict) else str(c) for c in cats] \
        if isinstance(cats, list) else [str(cats)]
    # location name adds retrievable venue text
    loc = f.get("location") or {}
    loc_name = loc.get("name", "") if isinstance(loc, dict) else ""
    instructions = f.get("attendeeInstructions") or ""

    text = " ".join(str(p) for p in [name, " ".join(map(str, cat_labels)), loc_name, instructions] if p).strip()

    # --- structured metadata for filtering / the gate ---
    # coordinates for distance work (from geo, or location.geo if present)
    geo = loc.get("geo", {}) if isinstance(loc, dict) else {}
    lat = geo.get("latitude")
    lng = geo.get("longitude")

    # price: three-state, never assumed (mirrors the gate discipline)
    offers = f.get("offers") or []
    if isinstance(offers, dict):
        offers = [offers]
    prices = [o.get("price") for o in offers if isinstance(o, dict) and o.get("price") is not None]
    is_free = None if not prices else all(float(p) == 0 for p in prices)

    return {
        "item_id": record["item_id"],
        "source_feed": record.get("provenance", {}).get("source_feed"),
        "text": text,
        "name": name,
        "location_name": loc_name,
        "lat": lat, "lng": lng,
        "start": f.get("startDate"),
        "is_free": is_free,
        "_record": record,          # keep the full record so the gate can read lineage
    }


def load_cards(path):
    cards = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            card = build_card(rec)
            if card["text"]:
                cards.append(card)
    return cards


# =====================================================================
#  R2 — BM25 lexical retrieval  (contract: build directly, no gate)
# =====================================================================
_TOKEN = re.compile(r"[a-z0-9]+")

def tokenize(s):
    return _TOKEN.findall(s.lower())


class BM25:
    """Standard BM25 over the cards' text. Pure Python, deterministic."""
    def __init__(self, cards, k1=1.5, b=0.75):
        self.cards = cards
        self.k1, self.b = k1, b
        self.docs = [tokenize(c["text"]) for c in cards]
        self.N = len(self.docs)
        self.avgdl = sum(len(d) for d in self.docs) / max(1, self.N)
        # document frequency per term
        df = Counter()
        for d in self.docs:
            for term in set(d):
                df[term] += 1
        self.idf = {t: math.log(1 + (self.N - n + 0.5) / (n + 0.5)) for t, n in df.items()}
        self.tf = [Counter(d) for d in self.docs]

    def search(self, query, top_k=100):
        q = tokenize(query)
        scores = []
        for i, tf in enumerate(self.tf):
            dl = len(self.docs[i])
            s = 0.0
            for term in q:
                if term not in tf:
                    continue
                idf = self.idf.get(term, 0.0)
                freq = tf[term]
                s += idf * (freq * (self.k1 + 1)) / (freq + self.k1 * (1 - self.b + self.b * dl / self.avgdl))
            if s > 0:
                scores.append((i, s))
        scores.sort(key=lambda x: x[1], reverse=True)
        return [(self.cards[i]["item_id"], sc) for i, sc in scores[:top_k]]


# =====================================================================
#  Dense retrieval (bi-encoder) — INTERFACE STUB for now
#  Swap in sentence-transformers later; RRF combines it with BM25.
#  Kept as a stub so R3 can be built and tested today.
# =====================================================================
def dense_search(query, cards, top_k=100):
    """Placeholder dense retriever. Returns [] until a bi-encoder is wired in.
       RRF handles an empty list gracefully, so R3 works with BM25 alone now."""
    return []   # TODO: embed cards + query with a bi-encoder, cosine top_k


# =====================================================================
#  R3 — Reciprocal Rank Fusion  (contract: combines rankings, no gate)
# =====================================================================
def rrf(rankings, k=60, top_k=100):
    """Fuse multiple ranked lists of item_ids by reciprocal rank.
       rankings: list of lists, each [(item_id, score), ...] in ranked order."""
    fused = defaultdict(float)
    for ranking in rankings:
        for rank, (item_id, _score) in enumerate(ranking):
            fused[item_id] += 1.0 / (k + rank + 1)
    out = sorted(fused.items(), key=lambda x: x[1], reverse=True)
    return out[:top_k]


# =====================================================================
#  R1 — EVIDENCE GATE  (contract §3: THREE-STRING INTERFACE STUB)
#  Michael's reducer_v0_1.py drops in here. Until then, a temporary
#  reducer that follows §2's mapping so the pipeline runs end-to-end.
# =====================================================================
# §2 lineage-class -> evidence-state mapping (FROZEN in the contract)
_LINEAGE_TO_STATE = {
    "ON_CHILD": "T", "CHILD_OVERRIDES": "T", "BOTH_EQUAL": "T", "INHERITED": "T",
    "SOURCE_ABSENT": "U", "UNRESOLVABLE_PARENT_UNAVAILABLE": "U",
}

def evidence_state(record, field):
    """Derive a field's evidence state (T/U) from its lineage class (§2)."""
    lineage = record.get("lineage", {}) or {}
    meta = lineage.get(field)
    if not isinstance(meta, dict):
        return "U"                      # child-only field with no lineage row -> U
    return _LINEAGE_TO_STATE.get(meta.get("class"), "U")


def r1_gate(query_constraints, card):
    """R1 gate INTERFACE. Returns one of the contract's three strings:
       'supported_match' | 'evidence_indeterminate' | 'bounded_non_match'.

       >>> THIS IS A STUB following §2/§3. Michael's reducer_v0_1.py (3-4 Sep)
       replaces the body; the SIGNATURE and RETURN VOCABULARY stay fixed, so
       R2/R3 code around it never changes. <<<

       query_constraints: dict of {field: predicate(value)->bool} for the
                          dimensions the query constrains.
    """
    record = card["_record"]
    any_indeterminate = False
    for field, satisfied in query_constraints.items():
        state = evidence_state(record, field)
        value = record.get("fields", {}).get(field)
        if state == "T":
            if not satisfied(value):
                return "bounded_non_match"      # T and unsatisfied
        else:  # U
            any_indeterminate = True            # constrained dim is unknown
    if any_indeterminate:
        return "evidence_indeterminate"
    return "supported_match"


# =====================================================================
#  D4 pipeline — wire R2 + R3 + R1 together
# =====================================================================
def d4_search(query_text, query_constraints, cards, bm25, top_k=20):
    """Full D4: retrieve (R2+dense) -> fuse (R3) -> gate (R1) -> return."""
    r2 = bm25.search(query_text, top_k=100)             # BM25 candidates
    rd = dense_search(query_text, cards, top_k=100)     # dense (stub -> [])
    fused = rrf([r2, rd], top_k=100)                    # R3 fusion

    by_id = {c["item_id"]: c for c in cards}
    results = []
    for item_id, fused_score in fused:
        card = by_id[item_id]
        gate = r1_gate(query_constraints, card)         # R1 eligibility
        results.append({"item_id": item_id, "name": card["name"],
                        "rank_score": round(fused_score, 4), "gate": gate})
    return results[:top_k]


# =====================================================================
#  DEMO
# =====================================================================
if __name__ == "__main__":
    cards = load_cards("sample_100_records.jsonl")
    print(f"loaded {len(cards)} cards")

    bm25 = BM25(cards)

    # example query: "gym induction", constrained to be free
    def is_free_pred(offers_value):
        # example predicate over the offers field
        if not offers_value:
            return False
        offers = offers_value if isinstance(offers_value, list) else [offers_value]
        prices = [o.get("price") for o in offers if isinstance(o, dict)]
        return any(p == 0 for p in prices if p is not None)

    results = d4_search(
        query_text="gym induction",
        query_constraints={"offers": is_free_pred},   # "free" constraint
        cards=cards, bm25=bm25, top_k=10,
    )
    print(f"\nquery: 'gym induction' (constrained: free)\n")
    for r in results:
        print(f"  {r['rank_score']:.4f}  [{r['gate']:22s}]  {r['name']}")
