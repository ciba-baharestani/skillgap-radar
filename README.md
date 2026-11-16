# SkillGap Radar

**Live app:** https://skillgap-radar-kxypbiclo76hxz6rmnnkgj.streamlit.app/

A tool that analyzes the US ed-tech/learning job market and shows educators
which skills to learn next, and which training programs teach them.

Status: complete. Data collection, cleaning, validation, a clustering experiment and the Streamlit app are done.

## Data sources
- **Adzuna Job Search API** (REST): US job postings for four role families
- **O*NET Web Services** (REST): 7 occupations (245 skill rows, 557 tool rows), used as a reference layer
- **University program pages** (requests + BeautifulSoup): 13 programs, saved as raw HTML, plus one manually downloaded PDF (Winona State)
- - **Skill taxonomy**: 73 skills: 57 AI-assisted draft reviewed by me (teaching, ed-tech and MBA knowledge), 13 added after reviewing O*NET technology data, 3 added after validation. 71 are shown in the app (two MBA-flavored rows are hidden).

## Pipeline (scripts in src/, run in this order)
1. collect_adzuna.py: call-capped collector, raw JSON saved to disk
2. search_onet.py, pull_onet_skills.py, flatten_onet.py: O*NET occupations, skills and tools
3. download_programs.py, preview_programs.py, build_program_table.py: program pages
4. flatten_adzuna.py, apply_relevance.py, dedupe_adzuna.py: cleaning
5. extract_skills.py, distinctive_terms.py, plot_skills.py: first analysis
6. make_validation_sample.py, compare_validation.py, tally_notes.py: validation on 30 postings read in full
7. cluster_postings.py: clustering experiment
8. build_app_data.py, build_fulltext_counts.py, build_program_skills.py: count files for the app
Helper checks: check_robots.py, check_adzuna.py, check_salary.py, check_duplicates.py, check_remote.py, probe_text.py

## App

A Streamlit app with two pages:

- **Market view:** the most visible skills per role family, with one shared scale so families can be compared.
- **Skill gap:** tick the skills you already have, pick a target role family, and see which of the most requested skills you are missing, plus programs whose public pages mention them.

Run it locally:

    py -m pip install streamlit
    py -m streamlit run app.py

The app reads only small count files in `data/app/` (no posting text). They are built by
`src/build_app_data.py`, `src/build_fulltext_counts.py` and `src/build_program_skills.py`.


## Results so far
- 709 unique Adzuna postings collected, 388 listings kept after relevance filtering (one Humana role with 37 copies was excluded after a manual check), 266 distinct postings after deduplication
- Distinct postings per family: Instructional Design 106, Corporate L&D 89, Learning Analytics 45, Ed-Tech Product 26
- 90 of 266 distinct postings (34%) contain at least one taxonomy skill in the 500-character snippet; 39 of 73 skills never matched. The chart below was made before the three validation skills were added, so its footnote still says 72 of 266 (27%).
- Chart: figures/top_skills_by_family.png


## Validation

I tested the skill matcher on a stratified random sample of 30 postings (quotas 8/8/7/7 across the four role families, seed 7). I read each posting in full via its Adzuna link and listed its skills. Labels: V01–V06 by me alone; V07–V11 by me and an LLM, with me resolving the disagreements; V12–V30 by an LLM (with evidence phrases), then checked and confirmed by me. There was no second human annotator, so all numbers are rough estimates (n = 30).

- **Calibration:** on the 5 postings labeled by both of us (V07–V11), the LLM found 86% of my labels and I found 75% of its.
- **Relevance filter:** 29 of 30 sampled postings were relevant (the one false positive was an ESOL classroom teacher). This checks only the postings I kept; my manual review of dropped postings partly covers the other direction.
- **Precision:** at least 11 of the 14 matcher matches (79%) were confirmed by the full-text labels. The other 3 are not checked yet.
- **Recall: about 4%** (11 of 313 labeled skills, 3.5%). The full text mentions 10.4 taxonomy skills per posting on average; the matcher finds 0.5 in the 500-character snippet. This mixes two problems (the cut text and the matcher itself); I did not measure the matcher on the snippet alone.
- **The rankings differ:** in the full text, curriculum development (22 of 30), LMS (18), facilitation (18) and cross-functional collaboration (17) lead; SME collaboration, the top snippet skill, is not in the top 10. Percentages describe a stratified sample, not the market.
- **Decision:** the snippet counts are shown only as a "visible skills" view. The skill-gap page uses the 29 relevant postings read in full (8 Instructional Design, 6 Ed-Tech Product, 8 Corporate L&D, 7 Learning Analytics).
- **Taxonomy gaps:** I added three skills the validation showed were missing (instructional design, multimedia creation tools, AI tools). Most other gaps were employer-specific domain knowledge.
- **MBA-flavored rows:** strategic planning (0 of 30) and budget management (1 of 30) are hidden in the app; data-driven decision making (4 of 30) stays.
- LLM assistance is disclosed here and in the presentation.


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

- The skill-gap numbers rest on 29 hand-read postings (6 to 8 per family). They are rough indications, not market statistics.
- Role families (Instructional Design, Learning Analytics, Ed-Tech Product, Corporate L&D) are a hypothesis based on search phrases. A clustering experiment did not confirm them (see below).
- Program pages are short overviews, so "mentions a skill" does not mean "teaches it", and a missing skill may still be taught. Program names inflate "Instructional design".
- Skill labels were made partly with LLM assistance. Code was written with AI assistance (Claude).


## Data ethics and licensing
- robots.txt was checked for every program site. Sites that disallow automated access (Iowa State, Drexel Online, Central Michigan, Michigan Tech, NC State) were excluded. Purdue was checked by hand, and UW-Green Bay and Kennesaw State could not be checked and were skipped. Scraping used a few pages, a pause between requests and raw HTML saved once. LinkedIn and Indeed were avoided because they prohibit scraping.
- Adzuna: free trial of 25 API calls in total (about 17 used). The paid plan (not used) offers 5,000 calls a month and 500 a day. Attribution ("Job market data from Adzuna (adzuna.com)") is shown in the app and in this README.

- Adzuna's API terms (developer.adzuna.com/docs/terms_of_service) permit personal and academic research and require attribution. They do not address storing posting text, so this repository and the app contain only aggregate counts, no posting text. This is a non-commercial academic project. Job market data from Adzuna (adzuna.com). Skill profile data: O*NET Web Services, U.S. Department of Labor, Employment and Training Administration, licensed CC BY 4.0.

- O*NET data is licensed CC BY 4.0. Credit: O*NET Web Services, U.S. Department of Labor, Employment and Training Administration. O*NET account registered under my bootcamp (personal use is not allowed).
- Raw Adzuna data, program page copies and posting-level tables are not committed to GitHub; run the pipeline with your own API keys to regenerate them. API keys are kept in .env and never committed.


## Clustering experiment (negative result)

To test whether my four role families appear in the data, I clustered the 266 posting descriptions (title excluded, to avoid circularity) with TF-IDF and k-means, written with numpy because Windows blocked scikit-learn on Python 3.15 (`src/cluster_postings.py`).

- Silhouette scores were 0.03 to 0.04 for k = 2 to 8, so there is no clear cluster structure.
- At k = 4 the clusters match my families no better than chance (adjusted Rand index 0.03; shuffled labels: -0.01; purity 0.41, equal to the 40% baseline of labeling everything Instructional Design).
- The clusters reflect writing style (startup language, apparent military postings), not role. The descriptions are cut at 500 characters, which is mostly the employer's introduction.

Conclusion: the snippet text cannot confirm or reject the role families. They remain a hypothesis from search phrases, used as target categories in the app. Testing them properly would need full job descriptions.