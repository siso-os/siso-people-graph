# Research spec: people graphs, person pages and advisors (PEOPLE-GRAPH, locked 14 Oct 2026)

**Goal:** know everything that exists about people graphs, so ours is the best: everyone and their works, ranked;
people of interest (Elon first) with everything they said on X and YouTube extracted; advisors agents can call that
answer only in a person's own words. Also: **low-fi wireframes, built by Haikus,** of the pages we'll need. UI Hub
builds the real thing later from its kit, so these are structure, not style.

**Start from:** `_data/app-factory/research/people-graph.md` (14 Oct first look). It covers our 339,217 people, 901,524
edges and the Elon extraction (84 sources, 1,981 quotes, 92k X posts, none accepted). Also
`siso-os-release/ecosystem/research/people.md`.

**Method:** `hub-research` v1. About **12 Haikus**: 2 blind map, 8 slices, 2 checkers. Then 3 wireframe Haikus.

## Slices
1. **People databases and graphs:** Wikidata, MIT Pantheon, OpenAlex authors, Crunchbase, LinkedIn-style graphs,
   Golden, Muck Rack, Exa people search.
2. **"Everything a person said" archives:** quote databases, Elon trackers, podcast and transcript indexes, X archives.
3. **Person-as-advisor products:** Delphi.ai, Character-style personas, RAG-on-a-person, "ask Naval/Paul Graham" sites.
   How they ground and cite, and how they handle consent.
4. **Ranking people:** Pantheon HPI, h-index, follower and influence scores, "most influential" lists. How they rank,
   and the biases they carry.
5. **Extraction pipelines:** YouTube and podcast transcription, X scraping limits and APIs, dedup, speaker
   attribution.
6. **Person-page UIs:** Wikipedia, Pantheon, Crunchbase, OpenAlex, Perplexity profiles, Twitter/X. Headless
   screenshots (camofox) to `ui-bases/`.
7. **Graph explorers:** Kumu, Obsidian graph, Connected Papers, Litmaps. What makes a big graph browsable.
8. **GitHub sweep:** `gh-sweep.py` for "knowledge graph people", "persona rag", "digital twin", topic:knowledge-graph,
   topic:people-search.

## Wireframes (3 Haikus, after the slices; plain HTML with grey boxes, one file each, in `wireframes/`)
- `person.html`: header, rank, works, "what they said" by topic with sources, advisor chat that cites, links to other
  people.
- `explore.html`: search, filters, leaderboard, graph view.
- `advisor.html`: ask a person; every answer sentence cites a source, date and URL; it refuses when the corpus is
  silent.

Each one borrows from the best UI bases found in slice 6 and says which.

## Write-up
- INDEX.md and COVERAGE.md
- `advisor-design.md`: grounding, citation, refusal, consent for living people
- `wireframes/INDEX.md`
- 3 open questions for Shaan

## Added by Shaan, 14 Oct ~10:20 (his words, verbatim, in `_data/app-factory/WORDS-2026-10-14.md`)
The people graph is part of our research engine: research on everything people post on YouTube, GitHub and X. It maps
each person's output so we can decide what to scrape, then distill it into **knowledge packs**.

**Watchlist v0, his names:**
- Elon Musk (principles)
- Theo (t3.gg: T3 Code, his benchmarks, everything he's made, and his YouTube videos about other builders)
- the BridgeMind founder ("that Matthew guy"; find his full name)
- David Andre (his YouTube)
- "Cueb" (the name is unclear in the transcript; find the likely creator from context: an AI/dev YouTuber)
- Organisations he named in the same breath: Convex, Fable, Groq

**Add slice 9: the per-person source map.**
- For each watchlist person: every channel (YouTube, GitHub, X, blog, podcast), with how much they post, how often,
  and what's worth pulling.
- Their notable works: repos, products, benchmarks, videos.
- `source-map.json`, plus a "scrape plan" that is cheap and continuous.
- Transcripts are pulled only for the videos Shaan picks, or under rules he signs off.

**Add to the write-up: `knowledge-packs.md`.** What a pack is (a person's or org's distilled principles, methods and
works, cited), the first 3 packs to make, and how a pack feeds Law Book, Agents Hub skills and the advisors.

Also follow `hub-research` rule 0: at most 4 Haikus at once, one camofox at a time.

## Scope widened by Shaan, 14 Oct ~10:30
"every single human that we know of, of all time ... People, organization, whatever ... a map of all knowledge
basically and this is just the people and orgs". Important people of all time, Socrates onwards, plus organisations.
- **Prior art under other names first:** people graphs exist under other names (knowledge graphs, prosopography
  databases, Wikidata, Pantheon, VIAF and authority files, Crunchbase for orgs, OpenAlex, genealogy graphs). The blind
  map must look for those names, not only "people graph".
- **What we already hold, used first:** 339,217 people and 901,524 edges in our DB, the book library (79k public-domain
  books, with authors back to Socrates: `Great_Library_of_SISO/works/siso-book-library`), `knowledge/books`, and the
  Elon extraction. Most people are probably in already; what's missing is proper scraping.
- **You, the Opus, design the whole system in `SYSTEM.md`:**
  - the data model (people, orgs, works, sources, claims, edges)
  - how it scales to unlimited data (storage, incremental scraping, dedup and identity across sources)
  - how it serves the UI (person, org, explore, advisor)
  - how knowledge packs come out of it

  Keep it cheap and continuous. This matters more than any single scrape.
