"""
report.py
---------
Generate a text-based recommendation report and save it to outputs/.
"""

import os
from datetime import datetime

from src.data_store import DataStore
from src.recommender import RecommendationEngine


def _separator(char: str = "─", width: int = 72) -> str:
    return char * width


def _header(title: str, width: int = 72) -> str:
    pad   = (width - len(title) - 2) // 2
    return f"{'═' * pad} {title} {'═' * (width - pad - len(title) - 2)}"


def generate_report(store: DataStore, engine: RecommendationEngine,
                    user_id: str, output_dir: str = "outputs") -> str:
    """
    Build a full recommendation report for a given user.

    Returns the report as a string AND writes it to a .txt file.
    """
    os.makedirs(output_dir, exist_ok=True)
    now  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user = store.get_user(user_id)

    lines: list[str] = []

    # ── Title ─────────────────────────────────────────────────────────────────
    lines += [
        "",
        _header("E-COMMERCE PRODUCT RECOMMENDATION ENGINE"),
        f"  Generated   : {now}",
        f"  User ID     : {user_id}",
        _separator(),
        "",
    ]

    # ── User profile ──────────────────────────────────────────────────────────
    lines += [
        _header("USER PROFILE"),
        f"  Preferred categories : {', '.join(sorted(user.preferred_cats)) if user else 'N/A'}",
        f"  Purchases            : {len(user.purchase_hist) if user else 0}",
        f"  Views (search hist)  : {len(user.search_hist) if user else 0}",
        f"  Cart items           : {len(user.cart_items) if user else 0}",
        _separator(),
        "",
    ]

    # ── Personalised recommendations ─────────────────────────────────────────
    pers = engine.personalised(user_id, top_n=10)
    lines += [_header("TOP 10 PERSONALISED RECOMMENDATIONS"), ""]
    _append_table(lines, pers)
    lines.append("")

    # ── Category-wise ─────────────────────────────────────────────────────────
    lines += [_header("TOP PRODUCTS BY CATEGORY"), ""]
    for cat in store.all_categories():
        top_cat = engine.by_category(cat, top_n=3)
        lines.append(f"  {cat}:")
        for rank, item in enumerate(top_cat, 1):
            lines.append(
                f"    {rank}. [{item['item_id']}] {item['title']:<35} "
                f"₹{item['price']:>8.0f}  ★{item['rating']}"
            )
        lines.append("")

    # ── Cart cross-sell ───────────────────────────────────────────────────────
    crosssell = engine.cart_crosssell(user_id, top_n=5)
    lines += [_header("CART CROSS-SELL"), ""]
    if crosssell:
        _append_table(lines, crosssell)
    else:
        lines.append("  (No cart items to base cross-sell on.)")
    lines.append("")

    # ── Popular products ──────────────────────────────────────────────────────
    popular = engine.popular(top_n=5)
    lines += [_header("TRENDING / MOST POPULAR"), ""]
    _append_table(lines, popular)
    lines.append("")

    # ── Data-store summary ────────────────────────────────────────────────────
    summary = store.summary()
    lines += [
        _header("STORE SUMMARY"),
        f"  Total products : {summary['total_products']}",
        f"  Total users    : {summary['total_users']}",
        f"  Categories     : {summary['categories']}",
        f"  Brands         : {summary['brands']}",
        _separator("═"),
        "",
    ]

    report_text = "\n".join(lines)

    # Save to file
    fname = f"{output_dir}/report_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(report_text)

    print(f"\n  ✔  Report saved → {fname}")
    return report_text


def _append_table(lines: list[str], items: list[dict]) -> None:
    """Append a formatted product table to lines."""
    header = (f"  {'#':<3} {'Item ID':<8} {'Title':<35} "
              f"{'Category':<14} {'Brand':<12} {'Price':>8}  {'★':>4}  Score")
    lines.append(header)
    lines.append("  " + "─" * 100)
    for rank, item in enumerate(items, 1):
        lines.append(
            f"  {rank:<3} {item['item_id']:<8} {item['title'][:34]:<35} "
            f"{item['category']:<14} {item['brand']:<12} "
            f"₹{item['price']:>7.0f}  ★{item['rating']:<4}  {item.get('rec_score', '')}"
        )
