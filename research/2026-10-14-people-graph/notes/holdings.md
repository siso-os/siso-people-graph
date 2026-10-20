# What we already hold (Opus, count-only queries, 14 Oct 2026)

DB: `~/SISO_Workspace/_data/foundry/foundry-scratch/graph/work.sqlite`, 1,113,350,144 bytes (matches README release size).
Opened read-only; COUNT/LIMIT queries only.

| measure | count |
|---|---|
| person rows | 339,217 (human 37,647; organisation 7,329; unknown 294,241) |
| state | linked 280,595; tracked 58,622 |
| organisation table | 1,131 |
| external ids by source | github_identity 244,874; crates_io 175,527; crates_io_dump 9,815; github_api 8,522; **wikidata_sparql 3,342**; v1_migration 419 |
| person_content by domain | github 463,230; crates 337,038; book 101,124; youtube_video 97; youtube_channel 35 |
| birth year known | 27,583; BCE 53; born before 1500: 342 |
| rank_score set | 280,571 (method undocumented) |

Spot checks: Elon Musk (human, linked, no birth year, no rank); Socrates appears TWICE (human/tracked and
unknown/tracked: a live duplicate); Plato -428, Aristotle -385; Theo Browne tracked (no works); Andrej Karpathy
rank 76.62; Convex present as organisation; "groq" as unknown; David Andre absent.

**Read:** the graph is a GitHub + crates + Gutenberg graph. 87% of rows are kind=unknown (mostly GitHub/crates
logins). Only 3,342 rows carry a Wikidata QID, so the "all humans of all time" skeleton is missing, not the scraping.
YouTube is 132 edges. X is zero. Elon's 92k posts and 1,981 quotes live in a separate DB
(`knowledge/pipelines/people/corpus/elon-musk/extraction/elon_extraction.sqlite`), not joined to the graph.
Other assets: `_data/foundry/foundry-scratch/wikidata/` (31 MB: advisors.csv, gh_orcid.csv, gh_social.csv);
`knowledge/pipelines/youtube/people_video_queue.sqlite`; book library `works/siso-book-library` is on GitHub only
(not checked out on this laptop; `estate restore` would fetch it).
