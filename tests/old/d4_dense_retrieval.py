"""
D4 — dense retrieval (bi-encoder), replacing the dense_search stub.

Drops into d4_retrieval_pipeline.py: replace the stub `dense_search` with the
`DenseRetriever` class here, and update `d4_search` to use it (shown at bottom).

Model: a small, fast, CPU-friendly sentence-transformer. all-MiniLM-L6-v2 is the
standard default — 384-dim, ~80MB, good quality/speed for this scale.

Why a bi-encoder here (contract-aligned): it embeds each card's text and the query
INDEPENDENTLY into vectors, then ranks by cosine similarity. This catches semantic
matches BM25 misses ("beginner fitness" -> "gym induction"). It only affects
RECALL/ORDERING — it never decides eligibility (that stays R1's job).

Install once:  pip install sentence-transformers   (add --break-system-packages if needed)
"""

import numpy as np
from pathlib import Path


class DenseRetriever:
    """Bi-encoder dense retrieval over the cards' text.
       Embeds once, caches to disk, then serves cosine-similarity search."""

    def __init__(self, cards, model_name="all-MiniLM-L6-v2", cache_dir="embeddings"):
        from sentence_transformers import SentenceTransformer   # imported lazily
        self.cards = cards
        self.ids = [c["item_id"] for c in cards]
        self.model = SentenceTransformer(model_name)

        Path(cache_dir).mkdir(exist_ok=True)
        cache = Path(cache_dir) / f"cards_{model_name.replace('/', '_')}_{len(cards)}.npy"

        if cache.exists():
            self.emb = np.load(cache)
            # guard: cache must match current card count
            if self.emb.shape[0] != len(cards):
                self.emb = self._embed_and_cache(cache)
        else:
            self.emb = self._embed_and_cache(cache)

    def _embed_and_cache(self, cache_path):
        texts = [c["text"] for c in self.cards]
        emb = self.model.encode(texts, normalize_embeddings=True,   # normalize -> cosine = dot
                                show_progress_bar=True, batch_size=64)
        emb = np.asarray(emb, dtype=np.float32)
        np.save(cache_path, emb)
        return emb

    def search(self, query, top_k=100):
        q = self.model.encode([query], normalize_embeddings=True)
        q = np.asarray(q, dtype=np.float32)[0]
        sims = self.emb @ q                       # cosine (both normalized) -> [N]
        # top_k by similarity
        k = min(top_k, len(sims))
        idx = np.argpartition(-sims, k - 1)[:k]
        idx = idx[np.argsort(-sims[idx])]
        return [(self.ids[i], float(sims[i])) for i in idx]


# =====================================================================
#  HOW TO WIRE IT INTO d4_retrieval_pipeline.py
# =====================================================================
#
#  1. Delete the stub `def dense_search(...)` and paste this DenseRetriever class.
#
#  2. Build the retriever ONCE (alongside `bm25 = BM25(cards)`):
#
#         bm25  = BM25(cards)
#         dense = DenseRetriever(cards)          # embeds + caches on first run
#
#  3. Change d4_search to accept and use it:
#
#         def d4_search(query_text, query_constraints, cards, bm25, dense, top_k=20):
#             r2    = bm25.search(query_text, top_k=100)     # lexical
#             rd    = dense.search(query_text, top_k=100)    # semantic (REAL now)
#             fused = rrf([r2, rd], top_k=100)               # R3 fuses both
#             ...                                            # rest unchanged
#
#  RRF already handles both lists — nothing else in the pipeline changes.
#
# =====================================================================
#  QUICK TEST once wired (shows dense catching what BM25 misses):
#
#     bm25, dense = BM25(cards), DenseRetriever(cards)
#     q = "beginner fitness class"                 # NOTE: not the literal words
#     print("BM25 top 3:")
#     for iid, s in bm25.search(q, 3):  print("  ", s, next(c["name"] for c in cards if c["item_id"]==iid))
#     print("Dense top 3:")
#     for iid, s in dense.search(q, 3): print("  ", s, next(c["name"] for c in cards if c["item_id"]==iid))
#
#  Expect: dense surfaces "Gym Induction" for "beginner fitness class" even though
#  those exact words aren't in the text; BM25 may miss it. That gap IS the value.
