# Wireframes (low-fi, structure not style; 14 Oct 2026)

Built by 3 Haikus from SYSTEM.md, advisor-design.md, knowledge-packs.md and notes/person-ui.md. Checked headless
(camofox over a local http server); screenshots are in `shots/`. UI Hub styles them later from its kit. Every number is
a sample.

| File | Page | Borrows (best of person-ui.md) |
|---|---|---|
| `person.html` | header (tier T0-T3, identifiers, Watch) - rank as 4 component bars - knowledge-pack principles with quote chips - works tabs - what they said (topic, year, dated rows, contradiction pair) - advisor box (answer + refusal) - identities & merge history - related people + ego box | FamousBirthdays (facts grid, rank pill), Pantheon (attention sparkline), Semantic Scholar (TLDR + influence badge), Google Scholar (sortable works), Roll Call Factbase (dated said-rows), LittleSis (external-links panel) |
| `explore.html` | search across people and orgs incl. BCE - facet rail with live counts - Leaderboard / Map / Timeline tabs - bias panel (cohort base rate vs top-N) and canon warning - ego drawer (top 50, cap 300) - two-person path | Pantheon (cohort rank, facet pages), Wikidata (typeahead label + QID), Embedding Atlas (points map, lasso), Histropedia/Litmaps (lanes), sigma.js/Connected Papers (ego, path), ranking.md bias rules |
| `advisor.html` | disclosure "From X's public record. Not X." + consent chip + coverage strip - corpus filters - answers as verbatim quote blocks (date, medium, URL with &t=, attribution confidence) - contradiction pair - refusal with nearest topics - sources panel + report wrong attribution - ask() JSON contract + release metrics | Dexa (timestamped links), StoryFile (verbatim clips, consent), Perplexity (source cards), Sensay (AI marker / assumed-info flag), Factbase (dated rows) |

Fixed by the Opus: advisor.html overflowed to the right (grid min-content); now it is `minmax(0,1fr)`.
Still missing: an **org page** wireframe (LittleSis relationship groups are the base; Crunchbase was blocked).
