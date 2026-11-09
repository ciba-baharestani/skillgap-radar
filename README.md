# SkillGap Radar

A tool that analyzes the US ed-tech/learning job market and shows educators
which skills to learn next, and which training programs teach them.

Status: data collection, cleaning and first skill extraction are done.
In progress: validation on a hand-labeled sample, clustering, skill-gap scoring and a Streamlit app.

## Data sources
- **Adzuna Job Search API** (REST): US job postings for four role families
- **O*NET Web Services** (REST): 7 occupations (245 skill rows, 557 tool rows), used as a reference layer
- **University program pages** (requests + BeautifulSoup): 13 programs, saved as raw HTML, plus one manually downloaded PDF (Winona State)
- **Skill taxonomy**: 70 skills, hand-built (teaching, ed-tech and MBA knowledge), extended after reviewing O*NET technology data

## Pipeline (scripts in src/, run in this order)
1. collect_adzuna.py: call-capped collector, raw JSON saved to disk
2. search_onet.py, pull_onet_skills.py, flatten_onet.py: O*NET occupations, skills and tools
3. download_programs.py, preview_programs.py, build_program_table.py: program pages
4. flatten_adzuna.py, apply_relevance.py, dedupe_adzuna.py: cleaning
5. extract_skills.py, distinctive_terms.py, plot_skills.py: first analysis
Helper checks: check_robots.py, check_adzuna.py, check_salary.py, check_duplicates.py, check_remote.py, probe_text.py

## Results so far
- 709 unique Adzuna postings collected, 388 listings kept after relevance filtering (one Humana role with 37 copies was excluded after a manual check), 266 distinct postings after deduplication
- Distinct postings per family: Instructional Design 106, Corporate L&D 89, Learning Analytics 45, Ed-Tech Product 26
- Only 72 of 266 distinct postings (27%) contain any taxonomy skill; 38 of 70 skills never matched
- Chart: figures/top_skills_by_family.png

## Key decisions
- US market, because O*NET is a US taxonomy
- Role families (Instructional Design, Learning Analytics, Ed-Tech Product, Corporate L&D) are a hypothesis based on search phrases, to be tested by clustering
- O*NET has no "instructional designer", "learning analyst" or "ed-tech product manager" occupation, so 7 occupations were chosen by hand and some serve as proxies (data scientist and BI analyst for Learning Analytics, project management occupations for Ed-Tech Product)
- O*NET's 35 generic skills are kept as a separate profile layer, not used for text matching, because they would match almost every posting
- Relevance: a title-keyword filter, then manual review of dropped postings. Rule: keep a posting if the employer's work involves learning or education and the role involves training, learning design, learning data or ed-tech. Machine-learning and "in training" (trainee) titles are excluded. One Humana posting was checked by hand and excluded.
- Borderline rescues (education-sector data analysts) are flagged low_confidence, so results can be checked with and without them
- Deduplication: 168 of 413 listings at that stage were exact copies (same title, company and text) posted under many locations. The analysis uses one row per distinct posting; n_listings and n_locations keep the copy counts. Whether copies are one opening or several is unknown, since the snippets rarely say (all 39 Norstella copies say "remote").

## Known limitations
- Adzuna descriptions are cut at 500 characters, so requirements (tools such as Python, Canvas, Storyline) are mostly invisible. Probe: those tools appear in 0-1 of 266 postings.
- The sample is the top relevance-ranked results of 16 API calls (12 first pages plus 4 second pages), not the whole market. Page 2 added many off-topic postings.
- Ed-Tech Product (26) and Learning Analytics (45) are small, so results for them are tentative.
- 70% of salaries in the raw data are Adzuna predictions (salary_is_predicted = 1); only stated salaries are used, 95 distinct postings.
- Family labels come from search phrases, and the distinctive-terms view is partly circular (job-title words dominate, even in a descriptions-only rerun; Ed-Tech Product terms are mostly employer mission language).
- Program pages differ in detail (Winona's page lists only competency areas), so low coverage can mean a thin web page, not a weaker curriculum. The price, credits and duration columns in programs.csv are unverified regex hints.
- The three MBA-flavored taxonomy rows (strategic planning, budget management, data-driven decision making) matched 0-2 postings each; to be kept or dropped after validation.

## Data ethics and licensing
- robots.txt was checked for every program site. Sites that disallow automated access (Iowa State, Drexel Online, Central Michigan, Michigan Tech, NC State) were excluded. Purdue was checked by hand, and UW-Green Bay and Kennesaw State could not be checked and were skipped. Scraping used a few pages, a pause between requests and raw HTML saved once. LinkedIn and Indeed were avoided because they prohibit scraping.
- Adzuna: free trial of 25 API calls in total (about 17 used). The paid plan (not used) offers 5,000 calls a month and 500 a day. Attribution ("Jobs by Adzuna") is shown as a precaution. [Still to check in Adzuna's terms: whether storing and displaying posting text is allowed. Until then, results show only aggregate counts, and posting-level tables are kept local.]
- O*NET data is licensed CC BY 4.0. Credit: O*NET Web Services, U.S. Department of Labor, Employment and Training Administration. O*NET account registered under my bootcamp (personal use is not allowed).
- Raw Adzuna data, program page copies and posting-level tables are not committed to GitHub; run the pipeline with your own API keys to regenerate them. API keys are kept in .env and never committed.