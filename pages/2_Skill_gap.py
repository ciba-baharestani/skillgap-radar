import csv
from pathlib import Path

import streamlit as st

# My guess at a typical teacher profile. Edit these names to match you.
TEACHER_PRESET = {
    "Curriculum development",
    "Assessment design",
    "Formative assessment",
    "Differentiated instruction",
    "Backward design",
    "Bloom's taxonomy",
    "Learner engagement",
    "Facilitation",
    "Presentation skills",
    "Written communication",
}


@st.cache_data
def load_rows():
    path = Path(__file__).parent.parent / "data" / "app" / "fulltext_counts.csv"
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["postings"] = int(r["postings"])
        r["family_labeled"] = int(r["family_labeled"])
        r["share"] = float(r["share"])
    return rows


rows = load_rows()
families = sorted({r["family"] for r in rows})

by_category = {}
seen = set()
for r in rows:
    if r["skill"] not in seen:
        seen.add(r["skill"])
        by_category.setdefault(r["category"], []).append(r["skill"])

st.title("My skill gap")
st.write(
    "Tick the skills you already have, pick a target role family, "
    "and see what the market asks for that you don't have yet."
)

with st.expander("How does this work?"):
    st.markdown(
        "- **Your skills** start from a typical teacher profile that you can change.\n"
        "- **The market** is 29 job postings I read in full by hand (6 to 8 per role family).\n"
        "- **Skills to build** are the 12 most requested skills for the family that you did not tick.\n"
        "- **Programs** are 13 US certificate programs whose public pages mention those skills."
    )

st.subheader("1. Your skills")
use_preset = st.checkbox("Start from a typical teacher profile", value=True)
my_skills = set()
for category in sorted(by_category):
    names = sorted(by_category[category])
    default = [n for n in names if use_preset and n in TEACHER_PRESET]
    with st.expander(category):
        chosen = st.multiselect(
            f"Skills in {category}", names, default=default, key=f"{category}-{use_preset}"
        )
        my_skills.update(chosen)

st.subheader("2. Target role")
family = st.selectbox("Role family", families)

wanted = [r for r in rows if r["family"] == family and r["postings"] > 0]
wanted.sort(key=lambda r: (-r["postings"], r["skill"]))
top = wanted[:12]
n_read = top[0]["family_labeled"]

have = [r for r in top if r["skill"] in my_skills]
missing = [r for r in top if r["skill"] not in my_skills]

st.subheader("3. Your gap")
st.write(f"You have **{len(have)} of the {len(top)}** most requested skills for {family}.")

col_missing, col_have = st.columns(2)
with col_missing:
    st.markdown("**Skills to build**")
    if not missing:
        st.write("None of the top skills are missing.")
    for r in missing:
        st.markdown(f"- {r['skill']}: in {r['postings']} of {n_read} postings")
with col_have:
    st.markdown("**Skills you already have**")
    if not have:
        st.write("None of the top skills yet.")
    for r in have:
        st.markdown(f"- {r['skill']}: in {r['postings']} of {n_read} postings")


st.subheader("4. Programs that mention these skills")
base = Path(__file__).parent.parent / "data" / "app"
with open(base / "program_info.csv", newline="", encoding="utf-8") as f:
    info = {r["slug"]: r for r in csv.DictReader(f)}
program_skills = {}
with open(base / "program_skills.csv", newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        program_skills.setdefault(r["slug"], set()).add(r["skill"])

missing_names = {r["skill"] for r in missing}
ranked = []
for slug, names in program_skills.items():
    hit = sorted(names & missing_names)
    if hit:
        ranked.append((len(hit), info[slug], hit))
ranked.sort(key=lambda x: (-x[0], x[1]["program"]))

if not ranked:
    st.write("No program in our list mentions the skills you are missing.")
for count, p, hit in ranked[:5]:
    st.markdown(f"**[{p['program']}]({p['url']})** covers {count} of your gaps: {', '.join(hit)}")
st.caption(
    "A program 'mentions' a skill when its public web page does. "
    "The pages are short overviews, so a skill missing here may still be taught."
)

st.caption(
    f"Based on {n_read} {family} postings read in full by hand. "
    "It is a small random sample, so treat the numbers as rough. "
    "Job market data from Adzuna (adzuna.com)."
)