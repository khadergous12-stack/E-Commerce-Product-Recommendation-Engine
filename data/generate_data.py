"""
generate_data.py
----------------
Generates synthetic product catalog (items.csv) and user event logs (events.csv).
Run once to produce the data files used by all other modules.
"""

import csv
import random
from datetime import datetime, timedelta

random.seed(42)

# ─── Product Catalog ────────────────────────────────────────────────────────

CATEGORIES = {
    "Electronics":  ["Smartphone", "Laptop", "Tablet", "Earbuds", "Smartwatch",
                     "Camera", "Monitor", "Keyboard", "Mouse", "Speaker"],
    "Clothing":     ["T-Shirt", "Jeans", "Sneakers", "Jacket", "Kurta",
                     "Saree", "Hoodie", "Formal Shirt", "Shorts", "Sandals"],
    "Books":        ["Python Programming", "Data Structures", "Clean Code",
                     "System Design", "Machine Learning", "Deep Learning",
                     "The Pragmatic Programmer", "DBMS Fundamentals",
                     "Operating Systems", "Computer Networks"],
    "Home":         ["Mixer Grinder", "Air Purifier", "LED Bulb", "Water Bottle",
                     "Pressure Cooker", "Curtains", "Pillow", "Bedsheet",
                     "Table Lamp", "Wall Clock"],
    "Sports":       ["Cricket Bat", "Football", "Yoga Mat", "Dumbbell",
                     "Running Shoes", "Badminton Racket", "Cycle Helmet",
                     "Resistance Band", "Jump Rope", "Water Sipper"],
}

BRANDS = {
    "Electronics": ["Samsung", "Apple", "Sony", "Boat", "Realme", "OnePlus"],
    "Clothing":    ["Zara", "H&M", "Nike", "Adidas", "Fabindia", "UCB"],
    "Books":       ["O'Reilly", "Pearson", "Packt", "Wiley", "Apress", "Manning"],
    "Home":        ["Prestige", "Philips", "Havells", "Milton", "Nilkamal", "IKEA"],
    "Sports":      ["Cosco", "Nivia", "Decathlon", "Adidas", "Yonex", "Boldfit"],
}

def generate_products(n_per_category: int = 20) -> list[dict]:
    """Create a list of product dicts."""
    products = []
    pid = 1
    for cat, names in CATEGORIES.items():
        for _ in range(n_per_category):
            name = random.choice(names)
            brand = random.choice(BRANDS[cat])
            price = round(random.uniform(99, 49999), 2)
            rating = round(random.uniform(2.5, 5.0), 1)
            tags = f"{cat.lower()} {name.lower()} {brand.lower()}"
            products.append({
                "item_id":  f"P{pid:04d}",
                "title":    f"{brand} {name}",
                "category": cat,
                "brand":    brand,
                "price":    price,
                "rating":   rating,
                "tags":     tags,
            })
            pid += 1
    return products


# ─── User Event Logs ─────────────────────────────────────────────────────────

EVENTS   = ["view", "cart", "purchase"]
WEIGHTS  = [0.65, 0.25, 0.10]          # views are most common


def generate_events(products: list[dict], n_users: int = 30,
                    events_per_user: int = 40) -> list[dict]:
    """Simulate user click/purchase logs."""
    base_ts = datetime(2024, 1, 1)
    events  = []
    item_ids = [p["item_id"] for p in products]

    for u in range(1, n_users + 1):
        uid = f"U{u:03d}"
        # Each user has 2–3 preferred categories
        fav_cats = random.sample(list(CATEGORIES.keys()), k=random.randint(2, 3))
        fav_items = [p["item_id"] for p in products if p["category"] in fav_cats]

        for _ in range(events_per_user):
            # 70 % chance to interact with a favourite-category item
            if random.random() < 0.70 and fav_items:
                iid = random.choice(fav_items)
            else:
                iid = random.choice(item_ids)

            event = random.choices(EVENTS, WEIGHTS)[0]
            ts    = base_ts + timedelta(
                days=random.randint(0, 89),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )
            events.append({
                "user_id": uid,
                "item_id": iid,
                "event":   event,
                "ts":      ts.strftime("%Y-%m-%d %H:%M:%S"),
            })

    # Sort chronologically
    events.sort(key=lambda x: x["ts"])
    return events


# ─── Write CSV files ──────────────────────────────────────────────────────────

def write_csv(path: str, rows: list[dict], fieldnames: list[str]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  ✔  Written {len(rows)} rows → {path}")


if __name__ == "__main__":
    import os
    os.makedirs("data", exist_ok=True)

    print("\n[1/2] Generating product catalog …")
    products = generate_products(n_per_category=20)
    write_csv(
        "data/items.csv", products,
        ["item_id", "title", "category", "brand", "price", "rating", "tags"],
    )

    print("\n[2/2] Generating user event logs …")
    events = generate_events(products)
    write_csv(
        "data/events.csv", events,
        ["user_id", "item_id", "event", "ts"],
    )

    print("\n✅  Data generation complete!")
    print(f"   Products : {len(products)}")
    print(f"   Events   : {len(events)}")
