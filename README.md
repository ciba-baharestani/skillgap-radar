# SkillGap Radar

A tool that analyzes the US ed-tech/learning job market and shows educators
which skills to learn next, and which training programs teach them.

## Data sources
- Adzuna Job Search API (job postings)
- O*NET Web Services (skills taxonomy)
- Public bootcamp/university program pages (web scraping)

## Notes to expand later
- US market chosen because O*NET is a US taxonomy
- Adzuna limits: [write the real numbers from their Terms]; "Jobs by Adzuna" attribution required
- Adzuna descriptions are truncated snippets (~500 characters), so tools mentioned later in a posting are missed
- O*NET account registered under the bootcamp (personal use not allowed); attribution required
- O*NET has no "instructional designer" title; mapped to closest occupations (25-9031.00, 13-1151.00)
- Scraping ethics: checked robots.txt and terms, polite delays, avoided LinkedIn and Indeed
- Raw data saved to disk so analysis never depends on live sites
- Role families are a hypothesis; compare with clustering results
- Salary data is often missing; report coverage honestly
- API keys kept in .env, never committed

Delaware: robots.txt allows all; terms of use checked, no scraping restriction found.
Iowa State: Checked robots.txt for each site and excluded programs that disallow automated access.

- Adzuna free trial gave 25 test calls; first test returned 18,703 postings for "instructional designer"
- Program pages shortlisted (Instructional Design family): Delaware, SWU, Drexel, WKU, Oregon State, Georgetown. 
- Purdue: robots.txt checked manually (the script hit a local SSL certificate error); program page path is not disallowed, so it is included
- robots.txt checked for every program site with a Python script (check_robots.py); Iowa State disallows automated access, so it was excluded
- Delaware: robots.txt allows all; terms of use checked, no scraping restriction found
- Scraping approach: few pages (8-15), a pause between requests, raw HTML saved once, content used for analysis only
- Georgetown: the shortlisted URL was a faculty subpage; the curriculum page will be used for scraping

Few programs target ed-tech product roles directly, so I used ed-tech leadership and general product management programs as proxies.

- Final program list: 13 programs in 4 role families, saved in data/program_urls.csv
- Excluded after robots.txt check: Iowa State, Drexel Online, Central Michigan, Michigan Tech, NC State (all disallow automated access). Drexel shows that rules differ by subdomain: drexel.edu allowed, online.drexel.edu blocked
- UW-Green Bay and Kennesaw State could not be checked by script (local SSL error) and were skipped
- Few US programs target ed-tech product roles directly, so ed-tech leadership programs are used as proxies
- Skill taxonomy: draft of 57 skills built by hand (data/taxonomy_draft.csv), including skills from my teaching and MBA background; to be extended with O*NET skills

- Adzuna collection: 12 search phrases x 1 page x 50 results = 551 postings (549 unique), collected with a call-capped script (src/collect_adzuna.py) on the free trial (25 calls total)
- Sample comes from relevance-ranked top results, so it is not representative of the whole market
- "edtech product manager" has only 6 matches in all of Adzuna, so the Ed-Tech Product family is thin
- Adzuna descriptions are cut at 500 characters (average length is exactly 500)
- Salary: 70% of postings (386 of 551) have predicted salaries (salary_is_predicted = 1); only the 165 stated salaries are used for salary analysis
- Broad searches (e.g. "training manager", "learning analytics") return some irrelevant jobs; a relevance filter is needed in cleaning

- O*NET occupation mapping: keyword search is literal (e.g. "product manager" returned biodiesel managers), so 7 occupations were chosen by hand and saved in data/onet_occupations.csv
- O*NET has no "learning analyst" or "ed-tech product manager" occupation; Learning Analytics uses data scientist and BI analyst as proxies, and Ed-Tech Product uses project management occupations as loose proxies
- O*NET data is licensed CC BY 4.0, so the README must credit "O*NET Web Services, U.S. Department of Labor, Employment and Training Administration"

- Skill taxonomy: 70 skills = 57 hand-built (teaching/MBA/ed-tech knowledge) + 13 added after reviewing O*NET technology data. O*NET covered only 11 of the first 57 (19%), so the hand-built list is the core
- O*NET's 35 generic skills (e.g. Active Listening, Instructing) are kept as a separate profile layer, not used for text matching, because they would match almost every posting

Taxonomy rows from MBA background to be kept or dropped based on validation results

- Winona State: the page lists only competency areas, so the program's requirements PDF was downloaded manually and its course text copied into data/processed/program_text/winona_state_pdf.txt (manual supplement; not scraped)
- Program pages differ in detail: programs with brief pages may show lower skill coverage because of thin web content, not a weaker curriculum

- Program table (data/processed/programs.csv): price, credits and duration columns are regex "hints" (first match on each page) and are unreliable; they were not verified. The page text itself is used for skill coverage.
- 13 program pages downloaded with requests, parsed with BeautifulSoup (strict cleanup, with a lighter fallback for pages like Drexel's that wrap content in tags the strict cleanup removes). Winona's course list came from a manually downloaded PDF.