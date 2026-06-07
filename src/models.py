"""
models.py
---------
Data model classes: Product and User.

DSA concepts:
  - Class-based encapsulation of data
  - Dictionary (HashMap) for O(1) attribute access
  - List for ordered event history
"""


class Product:
    """
    Represents a single product in the catalog.

    Attributes
    ----------
    item_id   : str   – unique identifier (e.g. "P0001")
    title     : str   – display name
    category  : str   – top-level category (Electronics, Books …)
    brand     : str   – brand name
    price     : float – price in ₹
    rating    : float – average star rating (2.5 – 5.0)
    tags      : str   – space-separated keywords for text similarity
    """

    def __init__(self, item_id: str, title: str, category: str,
                 brand: str, price: float, rating: float, tags: str):
        self.item_id  = item_id
        self.title    = title
        self.category = category
        self.brand    = brand
        self.price    = float(price)
        self.rating   = float(rating)
        self.tags     = tags

    # ── Comparison support for sorting / priority-queue ──────────────────────
    def __lt__(self, other):
        """Enables min-heap comparison by rating (higher is better)."""
        return self.rating < other.rating

    def __repr__(self):
        return (f"Product({self.item_id!r}, {self.title!r}, "
                f"₹{self.price:.0f}, ★{self.rating})")

    def to_dict(self) -> dict:
        return {
            "item_id":  self.item_id,
            "title":    self.title,
            "category": self.category,
            "brand":    self.brand,
            "price":    self.price,
            "rating":   self.rating,
            "tags":     self.tags,
        }


# ─────────────────────────────────────────────────────────────────────────────

class User:
    """
    Represents a platform user with interaction history.

    Attributes
    ----------
    user_id        : str        – unique identifier (e.g. "U001")
    purchase_hist  : list[str]  – item_ids the user has purchased
    search_hist    : list[str]  – item_ids the user has viewed
    cart_items     : list[str]  – item_ids currently in cart
    preferred_cats : set[str]   – inferred from interaction history

    DSA notes:
      - List  → O(1) append for event logging
      - Set   → O(1) membership test (avoid re-recommending purchased items)
    """

    def __init__(self, user_id: str):
        self.user_id       = user_id
        self.purchase_hist : list[str] = []
        self.search_hist   : list[str] = []   # "view" events
        self.cart_items    : list[str] = []
        self.preferred_cats: set[str]  = set()

    # ── Helper: add a single event ────────────────────────────────────────────
    def add_event(self, item_id: str, event: str, category: str = "") -> None:
        """
        Record a user–item interaction.

        Parameters
        ----------
        item_id  : product identifier
        event    : one of {'view', 'cart', 'purchase'}
        category : product's category (used to infer preferences)
        """
        if event == "view":
            if item_id not in self.search_hist:
                self.search_hist.append(item_id)
        elif event == "cart":
            if item_id not in self.cart_items:
                self.cart_items.append(item_id)
        elif event == "purchase":
            if item_id not in self.purchase_hist:
                self.purchase_hist.append(item_id)

        if category:
            self.preferred_cats.add(category)

    # ── All interacted items (for exclusion during recommendation) ────────────
    @property
    def interacted_items(self) -> set[str]:
        """Return the set of all item_ids the user has ever interacted with."""
        return set(self.purchase_hist) | set(self.search_hist) | set(self.cart_items)

    def __repr__(self):
        return (f"User({self.user_id!r}, "
                f"purchases={len(self.purchase_hist)}, "
                f"views={len(self.search_hist)}, "
                f"cart={len(self.cart_items)})")
