# SYSTEM: the people and organisations graph (PEOPLE-GRAPH, 14 Oct 2026)

Shaan: "every single human that we know of, of all time ... people, organisation, whatever ... a map of all knowledge,
and this is just the people and orgs." Keep it cheap and continuous.

This is the design. Evidence is in `notes/` (one file per slice) and `INDEX.md`. What we hold today is in
`notes/holdings.md`.

## 0. The one idea

**We don't scrape the world into a graph. We attach to the graphs that already exist, and spend money only where
attention is.**

Wikidata already names 13.74M humans (live Q5 count, 14 Oct) and millions of organisations, CC0, with crosswalks to VIAF, ORCID, ISNI,
OpenAlex, GitHub, X and YouTube. OpenAlex names ~96.5M authors (live API, 14 Oct). These are our free skeleton. Our value is the layer
above: the works joined across domains, everything a person said (verbatim, dated, cited), a rank you can audit, and
knowledge packs. We pay for that layer only for people someone cares about.

Today's graph is the inverse. 87% of its 339k rows are `kind=unknown` GitHub and crates logins, only 3,342 carry a
Wikidata QID, Socrates exists twice, and Elon's 92k posts sit in a separate database. The fix is the skeleton, not
more scraping.

## 1. Tiers: cost follows attention

| Tier | Who | What we hold | How it updates | Cost |
|---|---|---|---|---|
| **T0 skeleton** | every human and org in Wikidata (13.74M humans, 4.99M organisation-class items; QLever, 14 Oct), plus Pantheon 2.0's 126,582 ranked people (`wd_id` join), GLEIF 3.46M LEIs, ROR 141k (CC0), OpenAlex authors on demand | name, aliases, dates (BCE negative), occupations, country, all external IDs, sitelinks count | weekly Wikidata diff | ~$0: a dump filter on the mini |
| **T1 linked** | anyone with works in our catalogues (books, repos, crates, papers, videos) | T0 + works edges + rank components | per-catalogue cursor (daily/weekly) | ~$0: APIs we already use |
| **T2 watched** | the watchlist, plus anyone promoted by rank or request | T1 + channel inventory (every video, post and repo, as metadata only) | polled (X since_id, YouTube RSS, GitHub events) | cents per person per month |
| **T3 deep** | people Shaan picks | T2 + transcripts and posts as **utterances**, claims, knowledge pack, advisor | on new item from T2; transcripts only for videos he picks or rules he signs | ~$150-700 back-fill for Elon-scale (extraction.md), then a few $/month |

Promotion is explicit (`tier` column plus a reason); demotion stops polling but keeps data. "All of history" lives in
T0 at near-zero cost; the money goes to T2 and T3.

## 2. Data model

Eight tables. Everything except `entity` is a **statement with a source**: the prosopography "factoid" model
(PBW/SNAP), Wikidata's statement+reference model, and OpenSanctions' statement store, combined. Nothing is asserted
without a source, and nothing is ever overwritten. A new run adds rows; views pick the current best.

```
entity        (entity_id, kind: person|org|group|pseudonym, label, tier, state: active|merged|disputed,
               merged_into, created_run)                      -- thin; facts live in statements
identifier    (entity_id, scheme: wikidata|viaf|orcid|isni|openalex|github|x|youtube|crates|gutenberg|lei|...,
               value, method: hard|matched|claimed, confidence, source_id)   -- the crosswalk
source        (source_id, url, kind: dump|api|page|video|post|book, publisher, fetched_at, published_at,
               content_hash, blob_path, licence, run_id)      -- every fetch; raw blob kept, immutable
statement     (stmt_id, subject_id, predicate, object_id | value, qualifiers_json (start, end, role, place),
               source_id, span (char/time offsets), method: dump|api|llm|human, confidence, rank:
               preferred|normal|deprecated, run_id)           -- facts AND edges: born, member_of, authored, topic
work          (work_id, kind: book|repo|video|post|paper|product|benchmark|talk, title, date, canonical_url,
               content_hash, popularity_json)                 -- authored-by is a statement
utterance     (utt_id, speaker_id, text (verbatim), said_at, source_id, span, context_before/after, medium:
               post|video|podcast|interview|essay|book, lang, dup_of, attribution: account|voiceprint|
               transcript_label|llm, attribution_conf, topics)  -- "what they said"; the advisor's only corpus
pack          (pack_id, entity_id, version, built_at, lines_json: [{text, kind: principle|method|work|belief,
               utt_ids[], verified}], coverage_json)          -- knowledge packs, every line cited
judgement     (left_ref, right_ref, verdict: same|different|unsure, by: rule|splink|haiku|human, score,
               reason, at)                                     -- identity as a judgement graph (nomenklatura)
```

`entity` is derived, not edited. It is the connected components of `same` judgements over source records (scheme +
value), recomputed after each run. Undoing a merge means flipping one judgement. The durable key is the
**source-record ID** (e.g. `wikidata:Q317521`, `github:theo`), because cluster IDs move (VIAF re-clusters monthly).
Our `entity_id` is minted once and kept stable by mapping a new component to the old ID with the largest overlap.

Org-specific spines sit beside Wikidata: GLEIF LEI (daily Golden Copy deltas), ROR (versioned research orgs),
OpenCorporates (220M companies, statement model; licence check before bulk) and GitHub orgs. Their facts go in the
same `statement` table.

Rules carried from the prior art (prior-art.md, people-dbs.md):
1. **Hard keys first.** Two different QIDs, ORCIDs or ISNIs never merge. Probabilistic matching (Splink) only for
   the remainder, with the reason stored.
2. **Merges are reversible.** A `different` judgement (the VIAF/ISNI marker pattern) stops a bad merge from coming
   back. Blocking + Splink (EM, ~1M records/min on a laptop) proposes; the judgement graph decides.
3. **Uncertain stays uncertain.** Unresolved logins stay their own entity (OpenAlex's NULL-author bucket) rather than
   being forced into a person.
4. **Edges carry citations** (the LittleSis pattern): `authored`, `member_of` and `said` are statements with a
   `source_id`.
5. **Dates are qualifiers, not facts about now.** An utterance is "said on DATE in SOURCE", never "believes".

## 3. Storage that scales to unlimited data cheaply

- **Raw blobs** (pages, JSON, transcripts, audio never kept after ASR): content-addressed (`sha256/ab/cd...`) on the
  Mac mini / HOLD, not the laptop (over 1 GB: `estate storage`). Immutable and deduped by hash.
- **Lake** (truth): `statement`, `utterance`, `identifier` and `source` as **Parquet partitioned by `run_id`**,
  queried with DuckDB. Appends only, so a run is cheap, rebuildable and diffable. A Wikidata humans+orgs extract is a
  few GB of Parquet, filtered in two streaming passes from `latest-truthy.nt.bz2` (43.5 GB, measured 14 Oct) on the
  mini, never the 103 GB JSON dump on the laptop (notes/gap-dbs-orgs.md, estimate 100-150 GB scratch, untimed).
- **Serving DB** (derived, rebuilt nightly): one SQLite per role, as today:
  - `graph.sqlite`: entities, current statements, FTS5 names
  - `said.sqlite`: utterances with FTS5 + vectors (sqlite-vec)
  - static JSON per T2/T3 person page
  It is a cache; delete it and rebuild from the lake.
- **Why not a graph DB:** every page needs 1-hop data plus precomputed neighbours. Recursive CTEs over SQLite cover
  depth 2. Freebase died of a closed, write-heavy central store (prior-art.md); a rebuildable lake avoids that.

Size check: T0 ~15M entities x ~20 statements = 300M rows, a few GB in Parquet on the mini. T3 for 100 people at
Elon scale (~100k posts + ~500 h audio, ~10M words each) is ~1B words, about 10 GB of text. Both fit one mini disk.

## 4. Continuous ingestion (adapters + cursors)

Every source is an **adapter**: `(source, cursor) -> new source rows + statements/utterances + next cursor`. It is
idempotent, keyed by content hash, and one job per adapter per cadence on the mini. A run never re-fetches what it
already holds.

| Adapter | Cursor | Cadence | Feeds |
|---|---|---|---|
| Wikidata humans+orgs | dump date, then RecentChanges | weekly | T0 entities, identifiers, dates, sitelinks |
| QRank / pageviews | week | weekly | rank components |
| OpenAlex authors+works | `updated_date` | weekly, filtered to T1+ | papers, citations |
| GitHub owners/repos | events ETag | daily, T1+ | repos, stars |
| Book catalogues (Gutenberg, our 79k library) | catalogue version | monthly | books, authors to QID |
| YouTube channel | RSS feed (free, 15 latest) + yt-dlp inventory once | hourly RSS for T2 | video metadata; captions only for T3-picked |
| X account | `since_id`, official pay-per-use ($0.005/read) | daily for T2 | posts as utterances (T3) or counts (T2) |
| Podcasts | Podcast Index feed | daily for T2 | episodes; transcripts if publisher ships them |

**Dedup** happens at three levels:
1. `source.content_hash` stops a fetch from being stored twice.
2. Utterances dedup by normalised exact hash, then MinHash (5-gram, Jaccard ~0.8) and SimHash for short posts. The
   earliest dated copy wins, and later copies point `dup_of` at it, so we keep every place it was said.
3. Entities dedup through the identity pass.

**Identity pass** runs after each ingest, on new identifiers only:
1. Hard-key join (QID, ORCID, ISNI, VIAF, and handles that Wikidata lists, e.g. P2002 X, P2397 YouTube, P2037
   GitHub).
2. Splink on name + dates + co-occurrence for the rest.
3. Above the threshold it auto-links; in the band it goes to a review queue (the Mix'n'match yes/no/unsure UI, which
   Haiku checkers can clear); below it, it stays separate.
4. Scored against S2AND-style B3 F1 before any bulk merge.

**Speaker attribution** for audio:
1. The channel owner is the default candidate.
2. pyannote turns, then a voiceprint enrolled from a known-solo clip, then a transcript label/LLM pass.
3. Each utterance stores its attribution method and confidence. Below 0.9, it does not reach advisors or packs.

## 5. Ranking (stored as components, shown as components)

`rank_score_v1 = 0.8 * base + 0.2 * works`, with
`base = 0.4 * pct(log sitelinks) + 0.3 * pct(log QRank 12mo) + 0.2 * pct(Wikipedia PageRank)`.
Percentiles are taken within a cohort (occupation family x birth century), so Socrates is not compared with a
YouTuber. Fewer than 2 inputs means "insufficient evidence", not a rank. The components and `inputs_present` are
stored as statements, the method version goes on the page, and a bias audit (gender, region, era) runs each release
(ranking.md). The 280,571 existing `rank_score` values have no documented method; they are kept as
`rank_score_v0` until v1 replaces them.

## 6. Serving the UI

| Page | Reads | Latency path |
|---|---|---|
| **Person / org** | precomputed JSON (T2/T3) or one SQL bundle (T0/T1): header, rank bars, identifiers, works by kind, "said" by topic and year, related people, pack summary, advisor box | static file or 1 query; pages render at 15M scale because T0 pages are generated on request from `graph.sqlite` |
| **Explore** | facets (occupation x era x country x topic) with live counts; leaderboard per cohort; overview map of precomputed UMAP coordinates (Embedding Atlas / deck.gl), ego view in sigma.js capped at 300 nodes | facets and coordinates are precomputed nightly; ego is a depth-1 CTE with LIMIT |
| **Advisor** | `said.sqlite` only: hybrid FTS + vector over utterances where attribution_conf >= 0.9; answer = selected verbatim spans with id, date and URL each; abstain under the relevance threshold | one retrieval; the LLM only selects and orders spans, it never writes claims (advisor-design.md) |
| **Agents (CLI/MCP)** | the same three queries as tools: `who(name)`, `said(person, topic, since)`, `ask(person, q)`, `pack(person)` | Agents Hub wraps them as skills |

## 7. Knowledge packs

A pack is a person's (or org's) distilled **principles, methods, works and positions over time**, where every line
cites utterance or work IDs. It is built only from T3 data.
1. Cluster utterances by topic.
2. An LLM proposes candidate lines, each with the utterance IDs behind it.
3. Haiku checkers confirm each cited span supports its line, and drop any that don't.
4. Lines are versioned by date range, so "Elon on remote work, 2020" and "2022" stay distinct.
5. The output is `pack.json` + `PACK.md`.

Packs feed Law Book (principles), Agents Hub (a pack becomes a skill: "build like Theo"), and advisors (the pack is a
table of contents over the corpus, not the source of answers). Detail in `knowledge-packs.md`.

## 8. First build order (cheap to valuable)

1. **Skeleton:** filter a Wikidata dump to humans+orgs into Parquet on the mini, then join our 339k on hard keys
   (GitHub P2037, crates, Gutenberg author IDs, VIAF). Measure how many of ours gain a QID. Fix Socrates x2.
2. **Join Elon:** move `elon_extraction.sqlite` into the `utterance` and `source` shape under his QID (Q317521). He
   becomes the first T3 page.
3. **Watchlist T2:** turn `source-map.json` into adapters: RSS, X since_id and GitHub events for 5 people + 3 orgs.
4. **rank_score_v1** with components, plus the bias audit.
5. **Advisor v0** on Elon with the silence test set, then the first 3 packs.

## 9. What would prove this design wrong

- Wikidata hard keys link under 30% of our T1 people. That would mean the skeleton is the wrong spine for living
  builders; OpenAlex/GitHub would become co-spines.
- Speaker attribution can't reach 0.9 on interviews. Then advisors would be limited to posts and essays.
- X pay-per-use costs on a 5-person watchlist exceed ~$50/month. That would force posts-as-counts at T2.
