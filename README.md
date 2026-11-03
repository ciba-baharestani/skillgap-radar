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