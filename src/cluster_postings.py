import csv
import re
from collections import Counter

import numpy as np

STOP = set("""a about above after all also an and any are as at be been being both but by can
could do does each for from had has have he her his how if in into is it its more most my no
not of on or our out over own she should so some such than that the their them then there
these they this those through to too under up us very was we were what when where which
while who will with you your would per etc""".split())

with open("data/processed/adzuna_dedup.csv", newline="", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

if "description" not in rows[0]:
    print("No 'description' column. Columns are:", list(rows[0].keys()))
    raise SystemExit

families = [r["family"] for r in rows]
docs = []
for r in rows:
    tokens = re.findall(r"[a-z][a-z+#]+", r["description"].lower())
    docs.append([t for t in tokens if len(t) >= 3 and t not in STOP])

n = len(docs)
df = Counter(t for d in docs for t in set(d))
vocab = sorted(t for t, c in df.items() if 3 <= c <= 0.5 * n)
index = {t: i for i, t in enumerate(vocab)}

# TF-IDF with sublinear term frequency, rows scaled to length 1
X = np.zeros((n, len(vocab)))
for i, d in enumerate(docs):
    for t, c in Counter(d).items():
        if t in index:
            X[i, index[t]] = 1 + np.log(c)
idf = np.log((1 + n) / (1 + np.array([df[t] for t in vocab]))) + 1
X *= idf
norms = np.linalg.norm(X, axis=1)
norms[norms == 0] = 1
X /= norms[:, None]

rng = np.random.default_rng(7)


def kmeans(X, k, n_init=20, iters=100):
    best = None
    for _ in range(n_init):
        centers = X[rng.choice(len(X), k, replace=False)].copy()
        labels = None
        for _ in range(iters):
            new = (X @ centers.T).argmax(axis=1)
            if labels is not None and (new == labels).all():
                break
            labels = new
            for j in range(k):
                members = X[labels == j]
                if len(members) == 0:
                    centers[j] = X[rng.integers(len(X))]
                else:
                    c = members.mean(axis=0)
                    length = np.linalg.norm(c)
                    centers[j] = c / length if length > 0 else c
        score = (X @ centers.T).max(axis=1).sum()
        if best is None or score > best[0]:
            best = (score, labels.copy())
    return best[1]


def silhouette(X, labels):
    D = 1 - X @ X.T
    ks = sorted(set(labels))
    scores = []
    for i in range(len(X)):
        own = labels == labels[i]
        if own.sum() <= 1:
            scores.append(0.0)
            continue
        a = D[i, own].sum() / (own.sum() - 1)
        b = min(D[i, labels == k].mean() for k in ks if k != labels[i])
        scores.append((b - a) / max(a, b))
    return float(np.mean(scores))


def comb2(x):
    return x * (x - 1) / 2


def adjusted_rand(a, b):
    a_vals, b_vals = sorted(set(a)), sorted(set(b))
    table = np.array([[sum(1 for x, y in zip(a, b) if x == i and y == j) for j in b_vals] for i in a_vals])
    sum_cells = comb2(table).sum()
    sum_rows = comb2(table.sum(axis=1)).sum()
    sum_cols = comb2(table.sum(axis=0)).sum()
    expected = sum_rows * sum_cols / comb2(len(a))
    maximum = 0.5 * (sum_rows + sum_cols)
    return (sum_cells - expected) / (maximum - expected)


print(f"{n} postings, {len(vocab)} words after filtering\n")
print("Silhouette by number of clusters (higher = clearer structure):")
for k in range(2, 9):
    print(f"  k={k}: {silhouette(X, kmeans(X, k)):.3f}")

labels = kmeans(X, 4)
fam_list = sorted(set(families))
print("\nk=4 clusters (columns) vs. my role families (rows):")
print("%-22s" % "" + "".join("%6d" % j for j in range(4)))
for fam in fam_list:
    counts = [sum(1 for fm, lb in zip(families, labels) if fm == fam and lb == j) for j in range(4)]
    print("%-22s" % fam + "".join("%6d" % c for c in counts))

ari = adjusted_rand(families, list(labels))
shuffled = list(rng.permutation(families))
purity = sum(
    max(sum(1 for fm, lb in zip(families, labels) if lb == j and fm == fam) for fam in fam_list)
    for j in range(4)
) / n
print(f"\nAdjusted Rand index vs. families: {ari:.3f}  (0 = no better than chance, 1 = identical)")
print(f"Same index with shuffled family labels: {adjusted_rand(shuffled, list(labels)):.3f}")
print(f"Purity: {purity:.2f}  (share of postings in the most common family of their cluster)")

mean_all = X.mean(axis=0)
print("\nTop words per cluster:")
for j in range(4):
    diff = X[labels == j].mean(axis=0) - mean_all
    top = [vocab[i] for i in np.argsort(-diff)[:8]]
    print(f"  cluster {j} ({(labels == j).sum()} postings): {', '.join(top)}")