# INDEX: people graphs, person pages and advisors (PEOPLE-GRAPH, hub-research v1, 14 Oct 2026)

**What this run produced:**
- 354 unique rows (`merged.jsonl`) from 14 Haiku slices: 2 blind, 10 directed, 2 gap
- 91 rows re-opened by 2 checkers: 73 verified, 18 failed or could not be observed
- 3 wireframes
- the design: **`SYSTEM.md`** (read first), `advisor-design.md`, `knowledge-packs.md`, `source-map.json` +
  `notes/source-map.md`, and `notes/holdings.md` (what we already own)

Numbers below are verified unless marked *(unverified)*.

## 1. Map of the domain
| Region | Who's there | Best in class |
|---|---|---|
| **Identity spines** (all humans, all time) | Wikidata (13,738,279 humans live; 4.99M org-class items), VIAF/ISNI/GND/LC authority files, ORCID, OpenAlex (96,474,526 authors live), FamilySearch (1.74B names, user-built) | Wikidata: CC0, crosswalks to everything, statement + reference model |
| **Ranked notables** | Pantheon 1.0 (11,341) and 2.0 (126,582, `wd_id` key), HBR (7M+), Laouenan set (2M+), QRank pageviews, Pew pageview rankings | Pantheon 2.0 as a ranked seed; QRank for attention |
| **Org registries** | GLEIF (3.46M LEIs, daily deltas), ROR (141k, CC0), OpenCorporates (ODbL, share-alike), Crunchbase/PitchBook (closed) | GLEIF + ROR open; Wikidata orgs for the rest |
| **Prosopography / claim models** | factoid model (KCL, PBW), SNAP:DRGN, Trismegistos, CIDOC-CRM, nanopubs, nomenklatura statements | nomenklatura: statements + judgement graph with reversible merges |
| **Commercial people data** | PDL, Apollo, Coresignal, Diffbot (10B+ entities), Exa Websets | none open; pay-on-return pricing is the idea to copy |
| **"Everything they said" archives** | Factba.se (politicians only), Politwoops (frozen), Wikiquote, Filmot (YouTube captions), Lex Fridman transcripts, TV News Archive, ParlSpeech, Zenodo Musk tweets (CC-BY-4.0) | **No per-person archive for a builder or founder exists.** Factbase's dated rows are the UI to copy |
| **Person-as-advisor** | Delphi, Dexa (Huberman), StoryFile, HereAfter, Sensay, Character.AI, Simile ($200M at ~$2B, Jul 2026), ElevenLabs Iconic (licensed voices), Generative Agents (1,052 people, 85% of self-consistency) | **Nobody cites every sentence AND refuses on silence.** This is our opening |
| **Extraction** | X API pay-per-use ($0.005/read, verified), scrapers (cheaper, against ToS), yt-dlp + youtube-transcript-api, Deepgram ($0.26/h) / AssemblyAI ($0.21/h), pyannote community-1 (CC-BY-4.0) | official X + free YouTube captions + local ASR |
| **Graph explorers** | Connected Papers, Litmaps, ResearchRabbit, Kumu, Obsidian, LittleSis Oligrapher, Embedding Atlas, cosmos.gl, sigma.js, Graphistry | never draw the whole graph: points map + capped ego view |
| **Ranking methods** | HPI, PageRank on Wikipedia, sitelinks, h-index, Klout (dead 2018), Famous Birthdays | none beats HPI on bias; components plus a bias panel is ours |

## 2. Heavy and light: what we hold vs the world
**Heavy (ours):**
1. GitHub and crates people: 244,874 GitHub identities, 463,230 repo edges.
2. Gutenberg authors back to Plato (-428).
3. Elon's corpus: 92,380 posts, 1,981 quotes, 84 sources.

**Light (ours):**
1. **Wikidata QIDs on only 3,342 of 339,217 rows**, so the all-of-history skeleton is missing.
2. 87% of rows are `kind=unknown`.
3. YouTube has 132 edges and X has 0.
4. The Elon corpus isn't joined to the graph.
5. Socrates is duplicated.
6. `rank_score` has no documented method.
7. 1,131 orgs.
8. No consented or reviewed quotes: `accepted_items` = 0.

**GitHub (landed after write-up):** 2,105 repos swept; 34 people-relevant READMEs read (`notes/github-reads.md`). The
stack to use: Splink + nomenklatura (identity, MIT), datasketch (dedup, MIT), yt-dlp + youtube-transcript-api
(ingest), whisper.cpp or sherpa-onnx (ASR + diarization + speaker ID, Apache-2.0), pyannote (diarization; models
gated). GPL/AGPL (Gramps, Zingg, Scholia, webtrees): ideas only.

**Light (this research):**
- Crunchbase and OpenAlex page UIs (Cloudflare)
- the Pantheon HPI weights
- Musk posts after May 2025
- three watchlist identities (below)

## 3. Top picks, with reasons
1. **Wikidata as the spine (T0)**: free, CC0, 13.7M humans and 5M orgs, with handles for X (P2002), YouTube (P2397)
   and GitHub (P2037), so hard-key joins to our 339k cost nothing.
2. **nomenklatura's statement + judgement model**: every fact sourced, and merges become reversible views. It fixes
   Socrates x2 and every future bad merge.
3. **Pantheon 2.0 (126,582 people, `wd_id`) + QRank**: a ranked, joinable seed for the leaderboard on day one.
4. **Official X pay-per-use + free YouTube captions + local whisper.cpp/pyannote**: legal and cheap, about
   $25-30/month for the v0 watchlist *(estimate)*.
5. **Embedding Atlas (MIT) for the map + sigma.js/graphology (MIT) for the ego view**: browsable at 300k+ nodes.
6. **Verbatim-only advisor with a published silence test**: our world-first, and the best answer to consent and
   publicity law for living people.

## 4. Principles worth distilling (to the harvesting bank)
1. Attach to existing graphs; spend only where attention is (tiers T0-T3).
2. Every value is a statement with a source; never overwrite; derive views.
3. Identity is a judgement graph: hard keys first, probabilistic second, human/Haiku review in the band.
4. Show rank as components, with inputs present and the cohort base rate. Label it "attention", not "importance".
5. Quotes are dated events ("said on DATE in SOURCE"), never beliefs.
6. Silence is an answer: measure abstention as hard as accuracy.
7. Never render the whole graph.

## 5. UI references worth stealing (screenshots in `ui-bases/`, wireframes in `wireframes/`)
- FamousBirthdays: facts grid + rank pill (header)
- Pantheon: cohort rank "N of M in occupation"; facet pages
- Semantic Scholar: TLDR + influence badge per work
- Google Scholar: sortable works, co-author counts
- Roll Call Factbase: dated said-rows with a transcript action
- Lex Fridman transcripts: speaker labels + timestamp links
- LittleSis: external-links panel and relationship groups (org page)
- Wikidata: aliases table, QID in typeahead
- Connected Papers: ego from 50k candidates, shortest-path highlight
- Embedding Atlas: points map with lasso
- Dexa: timestamped citations
- Perplexity: source cards

## 6. Gaps (next round, if wanted)
- Crunchbase/OpenAlex/Pantheon person-page captures (need a passing camofox session)
- Pantheon HPI equation 4 weights
- Musk post data after May 2025 (decides whether the X back-fill is paid)
- a timed Wikidata truthy filter on the mini
- a sigma/cosmos benchmark on our 900k edges
- an org-page wireframe
- 263 rows unchecked (low-stakes; nothing in SYSTEM.md rests on them)

## 7. Watchlist v0 identities (source-map.json)
- **Confirmed:** Elon Musk; Theo Browne (t3code 27,432 stars, verified); BridgeMind (the company); Convex; Groq.
- **Not confirmed:** BridgeMind founder "Matthew Miller" (one source); "David Andre" (likely **David Ondrej**, 420K
  subs, numbers verified, name not); "Cueb" (likely **Cole Medin**, 228K subs, Archon 23,684 stars, verified numbers,
  identity ~25%); "Fable" (Showrunner picked, but an AI builder may mean something else).
