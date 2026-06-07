# Architecture & Design Decisions

## Data Flow

```
items.csv + events.csv
        │
        ▼
   DataStore (HashMaps)
        │
        ▼
 SimilarityEngine (Co-occurrence + Jaccard + Price + Rating)
        │
        ▼
 RecommendationEngine
 ├── personalised()    → max-heap top-N
 ├── by_category()     → sorted list
 ├── similar_to()      → SimilarityEngine.top_similar()
 ├── popular()         → Counter + heap
 └── cart_crosssell()  → co-occurrence lookup
        │
        ▼
   CLI Menu + Report
```

## DSA Complexity Summary

| Operation | Data Structure | Time Complexity |
|---|---|---|
| Load N products | dict | O(N) |
| Lookup product by ID | dict | O(1) avg |
| Build co-occurrence | nested dict | O(U × S²) |
| Composite similarity | arithmetic | O(\|tags\|) |
| Top-K recs (personalized) | heapq.nlargest | O(N log K) |
| Category sort | list.sort | O(M log M) |
| Cart cross-sell | dict lookup | O(C × max_co) |

## Why No External Libraries?

The core engine uses only Python's standard library:
- `heapq` for min/max heap operations
- `collections.defaultdict` and `Counter`
- `csv` for data loading
- `math.exp` for price decay

This makes the project **dependency-free** and easy to run anywhere.

## Extension Points

1. **Better embeddings**: Replace tag-Jaccard with TF-IDF + cosine or sentence-transformers
2. **ANN index**: Add FAISS for sub-linear similarity search at scale
3. **Ranker model**: Train LightGBM LambdaMART on implicit feedback pairs (see project PDF)
4. **FastAPI server**: Wrap `RecommendationEngine` in a `/recommend` endpoint
5. **React UI**: Add a frontend grid (see Step 8 in the project spec)
