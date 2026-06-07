"""
similarity.py
-------------
Product–product similarity scoring.

DSA concepts
─────────────
  HashMap   – co-occurrence counting, tag-to-item inverted index
  Set       – Jaccard intersection / union in O(|A|+|B|)
  Sorting   – rank by score descending
  Heap      – top-K extraction in O(N log K) via heapq.nlargest

Similarity methods implemented
───────────────────────────────
  1. Tag-Jaccard          – textual overlap of tag tokens
  2. Category match       – binary boost when categories align
  3. Price proximity      – normalised inverse price gap
  4. Rating boost         – prefer higher-rated products
  5. Co-occurrence        – items appearing together in user sessions
  6. Composite score      – weighted blend of all the above
"""

import heapq
from collections import defaultdict
from math import exp

from src.data_store import DataStore


# ── Weight constants (tunable) ────────────────────────────────────────────────
W_TAG      = 0.35
W_CATEGORY = 0.25
W_PRICE    = 0.15
W_RATING   = 0.10
W_COOCCUR  = 0.15

MAX_PRICE  = 50_000.0   # normalisation ceiling


class SimilarityEngine:
    """Computes composite similarity scores between products."""

    def __init__(self, store: DataStore):
        self.store    = store
        self._cooccur : dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self._build_cooccurrence()

    # ── Private: build co-occurrence matrix from user sessions ───────────────

    def _build_cooccurrence(self) -> None:
        """
        For every user, treat all interacted items as a session.
        Increment co[A][B] for every ordered pair (A, B) in that session.

        Time : O(U × S²)  where S = avg session size
        Space: O(I²) worst-case, sparse in practice
        """
        for user in self.store.user_map.values():
            session = list(set(
                user.search_hist + user.cart_items + user.purchase_hist
            ))
            for i in range(len(session)):
                for j in range(i + 1, len(session)):
                    a, b = session[i], session[j]
                    self._cooccur[a][b] += 1
                    self._cooccur[b][a] += 1

    # ── Individual score components ───────────────────────────────────────────

    def _tag_jaccard(self, p1, p2) -> float:
        """
        Jaccard similarity on tag token sets.
        J(A,B) = |A ∩ B| / |A ∪ B|

        Time: O(|tags|)
        """
        t1 = set(p1.tags.lower().split())
        t2 = set(p2.tags.lower().split())
        if not t1 or not t2:
            return 0.0
        return len(t1 & t2) / len(t1 | t2)

    def _category_score(self, p1, p2) -> float:
        """1.0 if same category, 0.5 if different — quick category boost."""
        return 1.0 if p1.category == p2.category else 0.0

    def _price_score(self, p1, p2) -> float:
        """
        Normalised inverse price gap.
        score = exp( -|price_diff| / MAX_PRICE )
        Returns values in (0, 1]; closer prices → score → 1
        """
        gap = abs(p1.price - p2.price) / MAX_PRICE
        return exp(-gap * 3)          # decay factor 3 gives nice spread

    def _rating_score(self, p2) -> float:
        """Normalised rating of the candidate product: [0, 1]."""
        return (p2.rating - 1.0) / 4.0   # scale [1,5] → [0,1]

    def _cooccur_score(self, iid1: str, iid2: str) -> float:
        """
        Normalised co-occurrence score.
        Uses the raw count normalised by the maximum count for iid1.
        """
        counts = self._cooccur.get(iid1, {})
        if not counts:
            return 0.0
        max_count = max(counts.values())
        return counts.get(iid2, 0) / max_count if max_count else 0.0

    # ── Public: composite score ───────────────────────────────────────────────

    def composite_score(self, item_id_seed: str, item_id_candidate: str) -> float:
        """
        Weighted composite similarity: [0.0, 1.0].

        Returns 0.0 if either product is not found.
        """
        p1 = self.store.get_product(item_id_seed)
        p2 = self.store.get_product(item_id_candidate)
        if p1 is None or p2 is None:
            return 0.0

        score = (
            W_TAG      * self._tag_jaccard(p1, p2)
            + W_CATEGORY * self._category_score(p1, p2)
            + W_PRICE    * self._price_score(p1, p2)
            + W_RATING   * self._rating_score(p2)
            + W_COOCCUR  * self._cooccur_score(item_id_seed, item_id_candidate)
        )
        return round(score, 4)

    # ── Public: top-K similar items ───────────────────────────────────────────

    def top_similar(self, item_id: str, k: int = 10,
                    exclude: set[str] | None = None) -> list[tuple[str, float]]:
        """
        Return the top-K most similar products to `item_id`.

        Uses heapq.nlargest → O(N log K) instead of full O(N log N) sort.

        Parameters
        ----------
        item_id : seed product
        k       : how many results to return
        exclude : set of item_ids to skip (e.g. already purchased)

        Returns
        -------
        List of (item_id, score) tuples, sorted descending by score.
        """
        if exclude is None:
            exclude = set()
        exclude.add(item_id)   # never include the seed itself

        scored = [
            (iid, self.composite_score(item_id, iid))
            for iid in self.store.product_map
            if iid not in exclude
        ]
        # heapq.nlargest is O(N log K) — more efficient than sort for large N
        return heapq.nlargest(k, scored, key=lambda x: x[1])
