"""
recommender.py
--------------
Main recommendation logic.

DSA concepts
─────────────
  Priority Queue (Max-Heap via heapq)
      – extract top-N recommendations in O(N log K)
  HashMap (dict)
      – O(1) user/product access from DataStore
  Sorting
      – rank candidates by composite relevance score
  Set
      – exclude already-interacted items in O(1) per check

Recommendation strategies
──────────────────────────
  1. Personalised (user history + similarity)
  2. Category-wise (top products in a given category)
  3. Similar products (seed item → nearest neighbours)
  4. Cold-start (new user / no history → popularity-based)
"""

import heapq
from collections import Counter

from src.data_store import DataStore
from src.similarity import SimilarityEngine


class RecommendationEngine:
    """Orchestrates all recommendation strategies."""

    def __init__(self, store: DataStore):
        self.store  = store
        self.engine = SimilarityEngine(store)

    # ── Helper: score a product for a user ────────────────────────────────────

    def _relevance_score(self, item_id: str, user_id: str) -> float:
        """
        Compute a personalised relevance score for (user, item).

        Factors
        -------
        • Average similarity to the user's purchased/carted items  (main signal)
        • Category preference boost                                 (+0.30)
        • Rating bonus                                              (+0.10)
        • Recency: items in cart > viewed > purchased

        Returns float in [0, ~2.0]
        """
        user    = self.store.get_user(user_id)
        product = self.store.get_product(item_id)
        if user is None or product is None:
            return 0.0

        # ── Seed items: cart carries more weight than views ──────────────────
        seed_items = (
            [(iid, 1.5) for iid in user.cart_items]       # weight 1.5
            + [(iid, 1.2) for iid in user.purchase_hist]  # weight 1.2
            + [(iid, 0.8) for iid in user.search_hist[-10:]]  # last 10 views
        )

        if seed_items:
            total_w = sum(w for _, w in seed_items)
            sim_sum = sum(
                w * self.engine.composite_score(seed_id, item_id)
                for seed_id, w in seed_items
            )
            sim_score = sim_sum / total_w
        else:
            sim_score = 0.0

        # ── Category preference boost ─────────────────────────────────────────
        cat_boost = 0.30 if product.category in user.preferred_cats else 0.0

        # ── Rating bonus ──────────────────────────────────────────────────────
        rating_bonus = (product.rating - 1.0) / 4.0 * 0.10

        return round(sim_score + cat_boost + rating_bonus, 4)

    # ── Strategy 1: Personalised recommendations ─────────────────────────────

    def personalised(self, user_id: str, top_n: int = 10) -> list[dict]:
        """
        Top-N personalised products for a user, excluding already-interacted items.

        Uses a max-heap of size top_n → O(N log top_n)
        """
        user = self.store.get_user(user_id)
        if user is None:
            return self.popular(top_n=top_n)   # cold-start fallback

        exclude = user.interacted_items

        # Score every non-interacted product
        scored = [
            (item_id, self._relevance_score(item_id, user_id))
            for item_id in self.store.product_map
            if item_id not in exclude
        ]

        # Max-heap: heapq.nlargest is O(N log K)
        top = heapq.nlargest(top_n, scored, key=lambda x: x[1])
        return self._format(top)

    # ── Strategy 2: Category-wise top products ───────────────────────────────

    def by_category(self, category: str, top_n: int = 5) -> list[dict]:
        """
        Top-N products in a category, ranked by rating then price competitiveness.

        Sorting: O(M log M) where M = items in category
        """
        items_in_cat = self.store.items_in_category(category)
        products = [
            self.store.get_product(iid)
            for iid in items_in_cat
            if self.store.get_product(iid) is not None
        ]
        # Sort: primary ↓ rating, secondary ↑ price (value for money)
        products.sort(key=lambda p: (-p.rating, p.price))
        top = [(p.item_id, p.rating) for p in products[:top_n]]
        return self._format(top)

    # ── Strategy 3: Similar items (PDP widget) ────────────────────────────────

    def similar_to(self, item_id: str, top_n: int = 6,
                   exclude: set[str] | None = None) -> list[dict]:
        """
        Products similar to a given seed item.
        Delegates to SimilarityEngine.top_similar().
        """
        results = self.engine.top_similar(item_id, k=top_n, exclude=exclude)
        return self._format(results)

    # ── Strategy 4: Cold-start / popularity fallback ─────────────────────────

    def popular(self, top_n: int = 10, category: str | None = None) -> list[dict]:
        """
        Popularity ranking using a weighted purchase/cart/view counter.

        Priority queue (Counter + nlargest) → O(N log K)
        """
        event_weights = {"purchase": 5, "cart": 3, "view": 1}
        score_counter: Counter = Counter()

        for user in self.store.user_map.values():
            for iid in user.purchase_hist:
                score_counter[iid] += event_weights["purchase"]
            for iid in user.cart_items:
                score_counter[iid] += event_weights["cart"]
            for iid in user.search_hist:
                score_counter[iid] += event_weights["view"]

        if category:
            cat_items = set(self.store.items_in_category(category))
            top = heapq.nlargest(
                top_n,
                [(iid, s) for iid, s in score_counter.items() if iid in cat_items],
                key=lambda x: x[1],
            )
        else:
            top = score_counter.most_common(top_n)

        return self._format(top)

    # ── Strategy 5: Cart cross-sell ───────────────────────────────────────────

    def cart_crosssell(self, user_id: str, top_n: int = 5) -> list[dict]:
        """
        Recommend items that co-occur with items in the user's cart.
        Uses co-occurrence map built inside SimilarityEngine.
        """
        user = self.store.get_user(user_id)
        if user is None or not user.cart_items:
            return []

        exclude  = user.interacted_items
        scores   : dict[str, float] = {}

        for seed in user.cart_items:
            co_map = self.engine._cooccur.get(seed, {})
            for iid, cnt in co_map.items():
                if iid not in exclude:
                    scores[iid] = scores.get(iid, 0.0) + cnt

        top = heapq.nlargest(top_n, scores.items(), key=lambda x: x[1])
        return self._format(top)

    # ── Formatter ─────────────────────────────────────────────────────────────

    def _format(self, items: list[tuple[str, float]]) -> list[dict]:
        """
        Enrich (item_id, score) tuples with full product info.

        Returns list of dicts ready for display / JSON serialisation.
        """
        results = []
        for item_id, score in items:
            p = self.store.get_product(item_id)
            if p:
                row = p.to_dict()
                row["rec_score"] = round(float(score), 4)
                results.append(row)
        return results
