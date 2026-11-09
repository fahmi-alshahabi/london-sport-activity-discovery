# ============================================================
#  D4 ABLATION — BM25 vs Dense vs Hybrid (RRF)
#  Add as a new cell AFTER your pipeline cell (reuses cards/bm25/dense).
#  No ground truth needed — compares the three retrieval variants to each
#  other, quantifying what fusion adds. Justifies the hybrid design.
# ============================================================
from collections import Counter

def ablation(queries, cards, bm25, dense, top_k=10):
    by_id = {c["item_id"]: c for c in cards}

    for qt in queries:
        r2 = [iid for iid,_ in bm25.search(qt, top_k)]        # BM25 top-k
        rd = [iid for iid,_ in dense.search(qt, top_k)]       # Dense top-k
        # hybrid via RRF over the two full ranked lists
        r2_full = bm25.search(qt, 100); rd_full = dense.search(qt, 100)
        fused = rrf([r2_full, rd_full], top_k=top_k)
        rh = [iid for iid,_ in fused]

        set2, setd, seth = set(r2), set(rd), set(rh)

        print(f"\n{'='*66}\nQUERY: '{qt}'")
        print(f"  BM25 top{top_k}:   {len(set2)} results")
        print(f"  Dense top{top_k}:  {len(setd)} results")
        print(f"  Hybrid top{top_k}: {len(seth)} results")

        # overlap: what the two methods agree/disagree on
        both = set2 & setd
        only_bm25 = set2 - setd
        only_dense = setd - set2
        print(f"\n  Overlap BM25 & Dense: {len(both)}/{top_k} "
              f"({len(both)/top_k:.0%} agreement)")
        print(f"  BM25-only (dense missed):  {len(only_bm25)}")
        print(f"  Dense-only (BM25 missed):  {len(only_dense)}")

        # THE KEY EVIDENCE: unique names each method surfaces that the other doesn't
        if only_dense:
            print(f"  --> Dense surfaced (BM25 missed): "
                  f"{sorted({by_id[i]['name'] for i in only_dense})[:5]}")
        if only_bm25:
            print(f"  --> BM25 surfaced (dense missed): "
                  f"{sorted({by_id[i]['name'] for i in only_bm25})[:5]}")

        # what hybrid pulls in that a single method's top-k didn't have
        hybrid_new = seth - (set2 | setd)
        print(f"  Hybrid promoted into top{top_k} from deeper ranks: {len(hybrid_new)}")


if __name__ == "__main__":
    # Queries chosen to expose lexical-vs-semantic differences:
    #  - literal terms (BM25 should do well)
    #  - semantic/paraphrase terms NOT in the data verbatim (dense should win)
    ablation_queries = [
        "swimming",                     # literal, common
        "lane swim",                    # literal exact phrase
        "beginner fitness class",       # semantic — words likely NOT in the data
        "water aerobics for seniors",   # semantic paraphrase
        "kids activities",              # semantic — 'kids' vs 'junior'/'child'
        "gentle exercise",              # semantic — no literal match likely
    ]
    ablation(ablation_queries, cards, bm25, dense, top_k=10)
