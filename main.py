"""
main.py
-------
Entry point: interactive CLI menu for the
E-Commerce Product Recommendation Engine.

Run:
    python main.py
"""

import os
import sys

# ── Make sure src/ is on the path when run from project root ─────────────────
sys.path.insert(0, os.path.dirname(__file__))

from data.generate_data import generate_products, generate_events, write_csv
from src.data_store import DataStore
from src.recommender import RecommendationEngine
from src.report import generate_report


# ── ANSI colour helpers (work on Windows ≥ Win10 and all Unix terminals) ──────
class C:
    CYAN   = "\033[96m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    BOLD   = "\033[1m"
    RESET  = "\033[0m"


def clr(text: str, colour: str) -> str:
    return f"{colour}{text}{C.RESET}"


# ── Display helpers ───────────────────────────────────────────────────────────

def print_banner() -> None:
    banner = r"""
  ╔══════════════════════════════════════════════════════════════════╗
  ║       E-COMMERCE PRODUCT RECOMMENDATION ENGINE                  ║
  ║       DSA Project  |  Python  |  HashMap + Heap + Sorting       ║
  ╚══════════════════════════════════════════════════════════════════╝
    """
    print(clr(banner, C.CYAN))


def print_menu() -> None:
    menu = f"""
  {clr('─── MAIN MENU ───────────────────────────────────────────────────', C.YELLOW)}
   {clr('[1]', C.GREEN)} Personalised Recommendations (top-N for a user)
   {clr('[2]', C.GREEN)} Similar Products             (seed item → neighbours)
   {clr('[3]', C.GREEN)} Top Products by Category
   {clr('[4]', C.GREEN)} Trending / Most Popular Products
   {clr('[5]', C.GREEN)} Cart Cross-Sell Suggestions
   {clr('[6]', C.GREEN)} Generate Full Report (saves to outputs/)
   {clr('[7]', C.GREEN)} Show User Profile
   {clr('[8]', C.GREEN)} Show Product Details
   {clr('[9]', C.GREEN)} List all Users / All Categories
   {clr('[0]', C.RED )} Exit
  {clr('─'*66, C.YELLOW)}
"""
    print(menu)


def print_products(items: list[dict], title: str = "") -> None:
    if title:
        print(f"\n  {clr(title, C.CYAN)}")
    if not items:
        print(clr("  (no results)", C.RED))
        return
    print(f"  {'#':<3} {'Item':<8} {'Title':<35} {'Cat':<13} ₹{'Price':>7}  ★  Score")
    print("  " + "─" * 82)
    for i, p in enumerate(items, 1):
        score = p.get("rec_score", "")
        print(
            f"  {i:<3} {p['item_id']:<8} {p['title'][:34]:<35} "
            f"{p['category']:<13} {p['price']:>8.0f}  {p['rating']}  {score}"
        )


def ask(prompt: str, default: str = "") -> str:
    val = input(f"  {clr('▶', C.GREEN)} {prompt}: ").strip()
    return val if val else default


def norm_uid(val: str) -> str:
    """Accept '1', 'u1', 'U001' -> always returns 'U001' format."""
    v = val.strip().upper().lstrip("U")
    return f"U{int(v):03d}" if v.isdigit() else val.strip().upper()


def norm_iid(val: str) -> str:
    """Accept '6', 'p6', 'P0006' -> always returns 'P0006' format."""
    v = val.strip().upper().lstrip("P")
    return f"P{int(v):04d}" if v.isdigit() else val.strip().upper()

# ── Startup: ensure data files exist ─────────────────────────────────────────

def ensure_data() -> None:
    if not os.path.exists("data/items.csv") or not os.path.exists("data/events.csv"):
        print(clr("\n  Data files not found — generating now …\n", C.YELLOW))
        os.makedirs("data", exist_ok=True)
        products = generate_products(n_per_category=20)
        write_csv("data/items.csv", products,
                  ["item_id", "title", "category", "brand", "price", "rating", "tags"])
        events = generate_events(products)
        write_csv("data/events.csv", events,
                  ["user_id", "item_id", "event", "ts"])
        print()


# ── Main loop ─────────────────────────────────────────────────────────────────

def main() -> None:
    print_banner()

    # ── Load data ─────────────────────────────────────────────────────────────
    ensure_data()
    print(clr("\n  Loading data …", C.YELLOW))
    store = DataStore()
    store.load_products("data/items.csv")
    store.load_events("data/events.csv")

    engine = RecommendationEngine(store)
    print(clr("  Engine ready!\n", C.GREEN))

    # ── Defaults (shown as hints) ─────────────────────────────────────────────
    default_uid  = list(store.user_map.keys())[0]
    default_iid  = list(store.product_map.keys())[0]
    default_cat  = store.all_categories()[0]

    while True:
        print_menu()
        choice = ask("Choice", "0")

        # ── [1] Personalised ──────────────────────────────────────────────────
        if choice == "1":
            uid  = norm_uid(ask(f"User ID (e.g. {default_uid})", default_uid))
            topn = int(ask("How many recommendations?", "10"))
            recs = engine.personalised(uid, top_n=topn)
            print_products(recs, f"Personalised Recommendations for {uid}")

        # ── [2] Similar products ──────────────────────────────────────────────
        elif choice == "2":
            iid  = norm_iid(ask(f"Seed Item ID (e.g. {default_iid})", default_iid))
            topn = int(ask("How many similar products?", "6"))
            recs = engine.similar_to(iid, top_n=topn)
            seed = store.get_product(iid)
            if seed:
                print(f"\n  Seed: {clr(seed.title, C.BOLD)} [{iid}] ★{seed.rating}")
            print_products(recs, f"Products similar to {iid}")

        # ── [3] By category ───────────────────────────────────────────────────
        elif choice == "3":
            cats = store.all_categories()
            print(f"\n  Available categories: {clr(', '.join(cats), C.CYAN)}")
            cat  = ask(f"Category (e.g. {default_cat})", default_cat)
            topn = int(ask("How many?", "5"))
            recs = engine.by_category(cat, top_n=topn)
            print_products(recs, f"Top {topn} in {cat}")

        # ── [4] Popular ───────────────────────────────────────────────────────
        elif choice == "4":
            topn = int(ask("How many?", "10"))
            recs = engine.popular(top_n=topn)
            print_products(recs, f"Trending / Most Popular (Top {topn})")

        # ── [5] Cart cross-sell ───────────────────────────────────────────────
        elif choice == "5":
            uid  = norm_uid(ask(f"User ID (e.g. {default_uid})", default_uid))
            topn = int(ask("How many cross-sell suggestions?", "5"))
            recs = engine.cart_crosssell(uid, top_n=topn)
            print_products(recs, f"Cart Cross-Sell for {uid}")

        # ── [6] Report ────────────────────────────────────────────────────────
        elif choice == "6":
            uid = norm_uid(ask(f"User ID for report (e.g. {default_uid})", default_uid))
            report = generate_report(store, engine, uid)
            print(clr("\n" + report, C.CYAN))

        # ── [7] User profile ──────────────────────────────────────────────────
        elif choice == "7":
            uid  = norm_uid(ask(f"User ID (e.g. {default_uid})", default_uid))
            user = store.get_user(uid)
            if user is None:
                print(clr(f"  User {uid} not found.", C.RED))
            else:
                print(f"\n  {clr('USER PROFILE', C.CYAN)} — {uid}")
                print(f"  Preferred categories : {', '.join(sorted(user.preferred_cats))}")
                print(f"  Purchases  ({len(user.purchase_hist)}): {user.purchase_hist[:5]} …")
                print(f"  Views      ({len(user.search_hist)}): {user.search_hist[:5]} …")
                print(f"  Cart       ({len(user.cart_items)}): {user.cart_items[:5]}")

        # ── [8] Product details ───────────────────────────────────────────────
        elif choice == "8":
            iid = norm_iid(ask(f"Item ID (e.g. {default_iid})", default_iid))
            p   = store.get_product(iid)
            if p is None:
                print(clr(f"  Product {iid} not found.", C.RED))
            else:
                print(f"\n  {clr(p.title, C.BOLD)} [{p.item_id}]")
                print(f"  Category : {p.category}")
                print(f"  Brand    : {p.brand}")
                print(f"  Price    : ₹{p.price:.2f}")
                print(f"  Rating   : ★{p.rating}")
                print(f"  Tags     : {p.tags}")

        # ── [9] List users / categories ───────────────────────────────────────
        elif choice == "9":
            sub = ask("Show [U]sers or [C]ategories?", "U").upper()
            if sub == "C":
                for cat in store.all_categories():
                    n = len(store.items_in_category(cat))
                    print(f"  {cat:<16} ({n} products)")
            else:
                uids = list(store.user_map.keys())
                print(f"\n  {len(uids)} users: {', '.join(uids[:20])} …")

        # ── [0] Exit ──────────────────────────────────────────────────────────
        elif choice == "0":
            print(clr("\n  Thank you for using the Recommendation Engine! 👋\n", C.GREEN))
            break

        else:
            print(clr("  Invalid choice. Please enter 0–9.", C.RED))


if __name__ == "__main__":
    main()
