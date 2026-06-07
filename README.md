# 🛒 E-Commerce Product Recommendation Engine

> **A DSA-focused, production-inspired recommender system built in pure Python.**  
> Demonstrates HashMap, Priority Queue, Sorting, Similarity Scoring, and Heap-based ranking.

---

## 📌 Project Overview

This project simulates the recommendation pipeline used by platforms like Amazon, Flipkart, and Myntra. It ingests user interaction logs (views, cart additions, purchases), calculates product similarity using multiple DSA-backed algorithms, and surfaces personalised product recommendations via an interactive CLI.

**Built for:** Software Developer · DSA · Backend Developer · E-Commerce Developer · Coding Interview roles.

---

## ❓ Problem Statement

Online shoppers face **information overload** — thousands of products, limited time. A recommendation engine solves this by:

- Surfacing *relevant* products based on a user's history
- Cross-selling complementary items at checkout
- Ranking trending items on the home feed
- Helping new users discover popular products (cold-start)

---

## 🧠 DSA Concepts Used

| Concept | Where Applied | Complexity |
|---|---|---|
| **HashMap / dict** | Product store, user store, co-occurrence matrix | O(1) lookup |
| **Priority Queue / Heap** | Top-N personalised recs, popular items | O(N log K) |
| **Sorting** | Category-wise ranking by rating & price | O(M log M) |
| **Set** | Exclude interacted items, Jaccard similarity | O(1) membership |
| **Co-occurrence Matrix** | Item-item session-based similarity | O(U × S²) build |
| **Weighted Scoring** | Composite similarity function | O(1) per pair |

---

## ⚙️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA INGESTION LAYER                         │
│   items.csv (product catalog)  +  events.csv (user logs)       │
└────────────────────┬────────────────────────────────────────────┘
                     │ load
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                  HASHMAP DATA STORE                             │
│  product_map {item_id → Product}                               │
│  user_map    {user_id → User}                                  │
│  category_map {category → [item_ids]}                          │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              SIMILARITY ENGINE                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Tag-Jaccard  │  │ Price Score  │  │ Co-occurrence Matrix │  │
│  │ (Set ops)    │  │ (exp decay)  │  │ (HashMap of counts)  │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│           │               │                     │               │
│           └───────────────┴─────────────────────┘              │
│                         Composite Score (0–1)                  │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│             RECOMMENDATION ENGINE                               │
│  ┌────────────────┐  ┌────────────────┐  ┌───────────────────┐ │
│  │ Personalised   │  │ Category-wise  │  │ Cart Cross-Sell   │ │
│  │ (heap top-N)   │  │ (sorted list)  │  │ (co-occ lookup)   │ │
│  └────────────────┘  └────────────────┘  └───────────────────┘ │
│  ┌────────────────┐  ┌────────────────┐                        │
│  │ Similar Items  │  │ Popular/Trending│                        │
│  │ (heap top-K)   │  │ (Counter heap) │                        │
│  └────────────────┘  └────────────────┘                        │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│          OUTPUT LAYER                                           │
│     CLI Menu  +  Text Report (outputs/)                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

- 🔍 **Personalised Recommendations** — blends cart, purchase, and view signals
- 🔗 **Similar Products** — Jaccard + price proximity + co-occurrence
- 📂 **Category-wise Top Products** — sorted by rating and value
- 🔥 **Trending / Popular** — implicit-signal weighted counter
- 🛒 **Cart Cross-Sell** — co-occurrence based suggestions
- ❄️ **Cold-Start Fallback** — popularity ranking for new users
- 📄 **Report Generation** — saves full analysis to `outputs/`
- 🖥️ **Interactive CLI** — colour-coded menu, no dependencies

---

## 📁 Folder Structure

```
E-Commerce-Product-Recommendation-Engine/
│
├── data/
│   ├── generate_data.py    ← Synthetic dataset generator
│   ├── items.csv           ← 100 products (auto-generated)
│   └── events.csv          ← 1,200 user events (auto-generated)
│
├── src/
│   ├── models.py           ← Product & User classes
│   ├── data_store.py       ← HashMap-based storage layer
│   ├── similarity.py       ← Composite similarity engine
│   └── recommender.py      ← All recommendation strategies
│
├── outputs/                ← Generated reports saved here
├── images/                 ← Screenshots for GitHub
├── docs/                   ← Extra documentation
│
├── main.py                 ← CLI entry point (run this!)
├── requirements.txt        ← No external deps needed
├── .gitignore
└── README.md
```

---

## 🚀 How to Run

### Requirements
- Python 3.10 or higher (uses standard library only)

### Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/E-Commerce-Product-Recommendation-Engine.git
cd E-Commerce-Product-Recommendation-Engine

# Run the project
python main.py
```

Data files are **auto-generated on first run** if missing.

### Generate data manually (optional)
```bash
python data/generate_data.py
```

---

## 🖥️ Sample Output

```
  ╔══════════════════════════════════════════════════════════════════╗
  ║       E-COMMERCE PRODUCT RECOMMENDATION ENGINE                  ║
  ║       DSA Project  |  Python  |  HashMap + Heap + Sorting       ║
  ╚══════════════════════════════════════════════════════════════════╝

  Loading data …
  ✔  Loaded 100 products across 5 categories.
  ✔  Loaded events for 30 users.

  TOP 10 PERSONALISED RECOMMENDATIONS for U015
  #   Item ID  Title                               Category          Price  ★   Score
  1   P0031    UCB T-Shirt                         Clothing          36063  4.2  0.7308
  2   P0015    Boat Laptop                         Electronics       13970  4.1  0.7249
  3   P0014    Sony Earbuds                        Electronics       49262  4.6  0.7224
  ...
```

---

## 📚 Algorithm Explanation

### Composite Similarity Score

```
score = 0.35 × Jaccard(tags)
      + 0.25 × CategoryMatch
      + 0.15 × PriceProximity
      + 0.10 × RatingBoost
      + 0.15 × CoOccurrence
```

### Priority Queue (Heap) Usage

Instead of sorting all N products (`O(N log N)`), we use Python's `heapq.nlargest`:

```python
top = heapq.nlargest(k, scored, key=lambda x: x[1])  # O(N log K)
```

This is significantly faster when `K << N`.

---

## 🎯 Learning Outcomes

After studying this project you will be able to:

- Implement a HashMap-based data store with O(1) access
- Build a co-occurrence matrix from user session logs
- Apply Jaccard similarity for text-based product matching
- Use Python `heapq` for efficient top-K extraction
- Design a multi-strategy recommendation pipeline
- Explain real-world relevance to interviewers

---

## 💼 Interview Q&A (Top 10)

**Q1: Explain your project.**  
This is an end-to-end E-Commerce Product Recommendation Engine. It uses HashMaps for O(1) data storage, Priority Queues for top-N extraction, Sorting for category rankings, and a composite similarity function combining Jaccard tag overlap, price proximity, and session co-occurrence to generate personalised, category-wise, and cross-sell recommendations.

**Q2: Why did you use a HashMap?**  
HashMaps give O(1) average-case lookup. I use `product_map[item_id]` and `user_map[user_id]` to retrieve objects instantly without iterating through lists.

**Q3: How does the similarity score work?**  
It's a weighted blend of five components: tag Jaccard, category match, normalised price gap, rating, and co-occurrence count. Each component is O(1) or O(|tags|).

**Q4: Why `heapq.nlargest` instead of `sorted()`?**  
`heapq.nlargest(K, list)` runs in O(N log K). `sorted()` runs in O(N log N). For N=100 products and K=10, this is 2× faster.

**Q5: What is the cold-start problem and how did you solve it?**  
New users have no history. I fall back to popularity ranking — items weighted by purchases (×5), cart adds (×3), and views (×1) — giving new users relevant results without personal data.

---

## 🏷️ GitHub Tags

`python` `dsa` `recommendation-system` `machine-learning` `ecommerce` `data-structures` `hashmap` `priority-queue` `portfolio-project` `placement-prep`

---

## 👨‍💻 Author

**Khadergouse Savanur**  
Computer Science Student | GM University  
[LinkedIn](https://linkedin.com/in/khadergousesavanur) · #KhadergouseSavanur

> Mentored by **Umesh Yadav Sir** | Indian Institute of Placement (EDC, IIT Delhi)
