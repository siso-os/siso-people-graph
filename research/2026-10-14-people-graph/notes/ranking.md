# Ranking notes (slice: ranking, 2026-10-14)

Rows: `rows/ranking.jsonl` (24 rows). All `verified` fields are null.

## Recommendation: composite rank_score

Rank within cohorts, not globally. Cohort = occupation family x birth-century band x (optionally) country. Global lists are dominated by Western, English-edition, recent figures (Pantheon, Eom, Skiena and Ward all show this).

Inputs we can get without new licences:

| Input | Source | Notes |
|---|---|---|
| Language-edition count (sitelinks) | Wikidata dump | Breadth, not depth. Counts only editions that have an article. |
| Aggregated pageviews | QRank weekly CSV (Wikidata-keyed) | Use 12-month mean of log views. Recency and US/English skew. |
| Link-graph PageRank per edition | Wikipedia dumps (our compute) | Eom 2015 method. Rewards canon and list articles. |
| Scholar impact | OpenAlex `cited_by_count`, `summary_stats` | Only for people with an ORCID or name match. Use a weighted citation count, not raw h-index. |
| Repo-owner impact | GitHub API: stars received, followers, commit counts | Only for people with GitHub accounts. |
| Age, gender, region | Wikidata P569, P21, P27 | Gender is self-declared or recorded, never inferred from names. |

Proposed formula (version it as `rank_score_v1`):

    cohort_pct(x) = percentile of x within the person's cohort
    base  = 0.40 * cohort_pct(log(1 + sitelinks))
          + 0.30 * cohort_pct(log(1 + qrank_12mo_mean))
          + 0.20 * cohort_pct(pagerank_wp_edition_mean)
    works = domain signal (OpenAlex weighted citations or GitHub stars), percentile within domain; if missing, 0.5
    rank_score = 0.8 * base + 0.2 * works
    if inputs_present < 2 or sitelinks < 3: show "insufficient evidence", no rank

Why these weights: sitelinks is the most stable and least recency-biased input; QRank adds current attention; PageRank is the one that does not depend on pageviews at all. Weights are a starting guess, to be fitted against the validation below. Store the four components and `inputs_present` alongside `rank_score` so the page can show them.

## Validation plan (what would make the score "validated")

1. Gold sets: Time 100 membership by year, Nobel laureates by category, Pantheon top-N as a weak label. Report Spearman and top-N overlap per cohort.
2. Pairwise human judgments: about 300 pairs stratified by rank gap, both orders shown, fit Bradley-Terry (or TrueSkill with variance). Compare each input and the composite to human preference.
3. LLM judge as a second rater only after position-swap consistency is measured (arXiv 2406.07791, 2502.14074). Use it as an axis, not as the score.
4. Bias audit on every release: rank distribution by gender, region, article language, birth century; report the share of women in top-N against the cohort base rate (about 18.5% of English biographies per arXiv 2411.04340).
5. Stability: correlation of ranks across two months of QRank to show recency sensitivity.

## Falsifier status

We found no validated ranking that beats Pantheon HPI on bias. HPI's own paper admits English, Western, male and recency bias qualitatively, and no gender audit of HPI was found. The bar for "beats HPI on bias" is: same or better accuracy on the gold sets, and a smaller gender and region gap in top-N at matched cohort base rates. We have not met that bar and cannot claim it yet.

## Biases, and how to show them on the page

| Bias | Where it comes from | Show it as |
|---|---|---|
| Gender | Editor gatekeeping (AfD, arXiv 2411.04340), pageview priority (32% women in top 50k, arXiv 2208.08426) | Cohort baseline share next to every top-N list; gender-stratified tab |
| Language / Western | English and Western editors and readers; sitelinks breadth | Per-edition toggle; region column; "measured in N editions" |
| Recency | Pageviews and news spikes | 12-month window; "recent spike" flag; separate all-time view |
| Platform | GitHub-only, Wikipedia-only, LLM training data | "Signals used" list on every profile; never imply a platform-neutral score |
| Canon | Link graph and textbook lists (Linnaeus, Greek philosophers) | Warning panel showing share of top-N from one era or region |
| Fame vs. impact | All popularity inputs measure attention | Label the score "notability/attention", not "importance" |
| Gaming | Votes, boosts, follower counts (Famous Birthdays, Klout, GitHub) | Show raw counts and their date; flag accounts with sudden spikes |

Page rules:
- Show the four components as bars, not one number.
- Show `inputs_present` as a confidence badge; below 2 inputs, do not rank.
- Show PageRank and pageview ranks side by side where they disagree (Eom: Linnaeus vs. Hitler under 2DRank).
- Show LLM-recognition (NameRank) as a second axis, not blended into the score.
- Put the method and version on the leaderboard footer, with a link to this note.

## Gaps (not covered in this slice)

- Pantheon 2.0 not found; Schich's book and its Pantheon claim not found.
- Pantheon HPI formula weights not published on the pages we read; the 2015 Sci Data paper or PMC full text is needed.
- committers.top and gitstar-ranking formulas not read; OSS Insight developer formula not found.
- Peoplepill, Ranker, Social Blade, Pew 2025 monthly chart: not checked.
- Kred shutdown: not confirmed. Klout shutdown is confirmed (2018-05-25).
- Eom PLoS ONE full text, the Huq and Ciampaglia PDF text, and the Pantheon 1.0 HPI weights were not parsed (PDF fetch returned binary).
- The Phabricator URL for the sitelinks claim (T174981) was surfaced by search; its content should be checked before citing.
