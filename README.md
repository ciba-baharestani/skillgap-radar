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