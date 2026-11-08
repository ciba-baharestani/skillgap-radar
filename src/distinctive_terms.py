import csv
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS

EXTRA_STOP = {
    "experience", "work", "working", "team", "teams", "role", "position", "job",
    "description", "responsibilities", "skills", "ability", "including", "years",
    "company", "new", "help", "will", "join", "looking", "seeking", "required",
    "preferred", "strong", "related", "opportunity", "full", "time", "part",
    "summary", "duties", "essential", "support", "business", "services",
    "employees", "provide", "able", "ensure", "knowledge", "management", "hard", "way", "space", "mission"
}

with open("data/processed/adzuna_dedup.csv", newline="", encoding="utf-8") as f:
    postings = list(csv.DictReader(f))

docs = [p["description"] for p in postings]
families = np.array([p["family"] for p in postings])

vec = TfidfVectorizer(
    stop_words=sorted(set(ENGLISH_STOP_WORDS) | EXTRA_STOP),
    ngram_range=(1, 2),
    min_df=4,
    max_df=0.5,
    token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z\-]+\b",
)
X = vec.fit_transform(docs)
terms = np.array(vec.get_feature_names_out())
print("Postings:", len(docs), "| terms kept:", len(terms))

rows = []
for fam in sorted(set(families)):
    inside = families == fam
    mean_in = np.asarray(X[inside].mean(axis=0)).ravel()
    mean_out = np.asarray(X[~inside].mean(axis=0)).ravel()
    diff = mean_in - mean_out
    top = np.argsort(diff)[::-1][:12]
    print(f"\n{fam} ({inside.sum()} postings):")
    print("   " + ", ".join(terms[top]))
    for rank, i in enumerate(top, 1):
        rows.append({"family": fam, "rank": rank, "term": terms[i], "score": round(float(diff[i]), 4)})

with open("data/processed/distinctive_terms.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["family", "rank", "term", "score"])
    writer.writeheader()
    writer.writerows(rows)
print("\nSaved data/processed/distinctive_terms.csv")