import csv
import html
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="SkillGap Radar", layout="wide")


@st.cache_data
def load_counts():
    path = Path(__file__).parent / "data" / "app" / "skill_counts.csv"
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["postings"] = int(r["postings"])
        r["family_postings"] = int(r["family_postings"])
        r["share"] = float(r["share"])
    return rows


def bar_row(skill, n, total, biggest):
    width = n / biggest * 100
    pct = round(n / total * 100)
    return (
        '<div style="margin:10px 0">'
        '<div style="display:flex;justify-content:space-between;font-size:0.95rem">'
        f"<span>{html.escape(skill)}</span>"
        f"<span>{n} of {total} postings ({pct}%)</span></div>"
        '<div style="background:rgba(128,128,128,0.25);border-radius:4px;height:10px">'
        f'<div style="width:{width}%;background:#2a9d8f;height:10px;border-radius:4px"></div>'
        "</div></div>"
    )


rows = load_counts()
families = sorted({r["family"] for r in rows})

st.title("SkillGap Radar")
st.write("Which skills show up in US learning and ed-tech job postings?")

family = st.selectbox("Role family", families)
selected = [r for r in rows if r["family"] == family][:10]
total = selected[0]["family_postings"]
biggest = selected[0]["postings"]

st.subheader(f"Most visible skills: {family}")
st.markdown(
    "".join(bar_row(r["skill"], r["postings"], total, biggest) for r in selected),
    unsafe_allow_html=True,
)

st.caption(
    "Counts come from the first 500 characters of each job description, "
    "so they show skills that are visible in the snippet, not full requirements. "
    "Job market data from Adzuna (adzuna.com)."
)