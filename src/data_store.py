"""
data_store.py
-------------
HashMap-based storage layer.

DSA concepts used
─────────────────
  HashMap / dict  – O(1) average-case insert & lookup
  List            – O(1) append when cataloguing items per category
  Set             – O(1) membership tests

Responsibilities
────────────────
  1. Load items.csv  → product_map   {item_id  → Product}
  2. Load events.csv → user_map      {user_id  → User}
  3. Build category_map              {category → [item_id, …]}
  4. Build brand_map                 {brand    → [item_id, …]}
"""

import csv
from collections import defaultdict

from src.models import Product, User


class DataStore:
    """Central in-memory store; all access is O(1) via hash maps."""

    def __init__(self):
        # Primary lookups
        self.product_map  : dict[str, Product]  = {}  # item_id  → Product
        self.user_map     : dict[str, User]      = {}  # user_id  → User

        # Inverted indexes (multi-value hash maps)
        self.category_map : dict[str, list[str]] = defaultdict(list)
        self.brand_map    : dict[str, list[str]] = defaultdict(list)

    # ── Loaders ───────────────────────────────────────────────────────────────

    def load_products(self, path: str = "data/items.csv") -> None:
        """
        Parse items.csv and populate product_map, category_map, brand_map.

        Time : O(N)   N = number of products
        Space: O(N)
        """
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                p = Product(
                    item_id  = row["item_id"],
                    title    = row["title"],
                    category = row["category"],
                    brand    = row["brand"],
                    price    = float(row["price"]),
                    rating   = float(row["rating"]),
                    tags     = row["tags"],
                )
                self.product_map[p.item_id]     = p
                self.category_map[p.category].append(p.item_id)
                self.brand_map[p.brand].append(p.item_id)

        print(f"  ✔  Loaded {len(self.product_map)} products "
              f"across {len(self.category_map)} categories.")

    def load_events(self, path: str = "data/events.csv") -> None:
        """
        Parse events.csv and reconstruct each User's history.

        Time : O(E)   E = number of events
        Space: O(U + E)
        """
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                uid  = row["user_id"]
                iid  = row["item_id"]
                evt  = row["event"]

                # Lazy-init user object
                if uid not in self.user_map:
                    self.user_map[uid] = User(uid)

                # Retrieve category from product_map (O(1))
                cat = self.product_map[iid].category if iid in self.product_map else ""
                self.user_map[uid].add_event(iid, evt, cat)

        print(f"  ✔  Loaded events for {len(self.user_map)} users.")

    # ── Convenience accessors ─────────────────────────────────────────────────

    def get_product(self, item_id: str) -> Product | None:
        """O(1) product lookup."""
        return self.product_map.get(item_id)

    def get_user(self, user_id: str) -> User | None:
        """O(1) user lookup."""
        return self.user_map.get(user_id)

    def items_in_category(self, category: str) -> list[str]:
        """Return all item_ids in a category — O(1) lookup (case-insensitive)."""
        # Try exact match first, then title-case, then scan
        if category in self.category_map:
            return self.category_map[category]
        title = category.strip().title()
        if title in self.category_map:
            return self.category_map[title]
        # full case-insensitive scan
        low = category.strip().lower()
        for k, v in self.category_map.items():
            if k.lower() == low:
                return v
        return []

    def all_categories(self) -> list[str]:
        return list(self.category_map.keys())

    def summary(self) -> dict:
        return {
            "total_products": len(self.product_map),
            "total_users":    len(self.user_map),
            "categories":     len(self.category_map),
            "brands":         len(self.brand_map),
        }
