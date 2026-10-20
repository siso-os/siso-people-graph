# PLAN: people graphs, person pages, advisors (PEOPLE-GRAPH, hub-research v1, 14 Oct 2026)

**Goal (Shaan, 13 Oct):** "finding a way to track everything that Elon's ever said ... people of interest go on the
people graph, then all of their stuff from Twitter and YouTube and wherever gets extracted ... and then we can start
making the page templates." Bar: "we don't build it unless it's best in the world". We are the layer above everything.

**Coverage target:** ~80% of what exists: every major people database, quote/transcript archive, persona/advisor
product, ranking method, extraction route, person-page UI and graph explorer. Merge target 40 rows per slice.

## Already held (no Haiku re-finds these)
- Our graph: 339,217 people, 901,524 person-content edges, 442,499 external ids, schema v2 (person, external_ids,
  person_content, identity_claim, person_topic). `README.md`.
- Elon corpus: `Great_Library_of_SISO/knowledge/pipelines/people/corpus/elon-musk/` (84 sources, 1,981 quotes,
  92,380 X posts 2010-2025 from Zenodo CSVs, accepted_items 0).
- First look: `_data/app-factory/research/people-graph.md` (Delphi, Pantheon HPI, Wikidata P31=Q5, Rai "Ipazia").

## Slices (row schema shared; budget = tool calls)
| # | slice | objective | sources to try | out of scope | budget | falsifier |
|---|---|---|---|---|---|---|
| 1 | people-dbs | every large people DB/graph: size, licence, API, id scheme, how they merge identities | Wikidata, Pantheon, OpenAlex, ORCID, VIAF, Crunchbase, PitchBook, LinkedIn, Golden, Muck Rack, Exa, People Data Labs, Apollo, Clay, Diffbot, DBpedia, IMDb, MusicBrainz | B2B lead-gen detail | 40 | a DB >1M people we did not list |
| 2 | said-archives | "everything X said" archives and trackers | Wikiquote, Quote Investigator, Elon trackers (elonmusk.today, Musk quote DBs), Trump Twitter Archive, Factba.se, Podscribe, Listen Notes, Snipd, podcast transcript indexes, Internet Archive X, Social Blade | generic quote-of-the-day sites | 40 | a person archive with dated citations per quote that beats Factba.se |
| 3 | advisors | person-as-advisor products: grounding, citation, refusal, consent | Delphi.ai, Character.ai, Hello History, Paul Graham GPT, Naval GPT, Huberman AI, Steve Jobs archive bots, Meta AI personas, ElevenLabs voice licensing, Rai Ipazia, academic papers on persona faithfulness | voice cloning tech | 40 | a product that cites every sentence AND refuses on silence |
| 4 | ranking | how people get ranked and the biases | Pantheon HPI, h-index/OpenAlex, Klout, Kred, Time 100, Forbes, Wikipedia pageviews, PageRank-on-Wikipedia (Wikirank), Peoplepill, Famous Birthdays, Social Blade | sports Elo | 40 | a validated ranking that beats HPI on bias |
| 5 | extraction | pipelines: YouTube/podcast transcription, X limits and APIs, dedup, diarization | yt-dlp, youtube-transcript-api, WhisperX, pyannote, Deepgram, AssemblyAI, X API tiers/prices, twscrape, Nitter status, Apify actors, near-dup (MinHash), quote attribution research | model training | 40 | a cheaper route to all of one person's X posts than X API Pro |
| 6 | person-ui | person-page UIs + headless screenshots to `ui-bases/` | Wikipedia, Pantheon, Crunchbase, OpenAlex, Google Scholar, Perplexity, X profile, Letterboxd, IMDb, Factba.se | styling | 40 | — |
| 7 | graph-explorers | what makes big graphs browsable | Kumu, Obsidian, Connected Papers, Litmaps, ResearchRabbit, Gephi Lite, Cosmograph, Sigma.js, Neo4j Bloom, Graphistry, LittleSis, OpenSanctions | graph DB engines | 40 | — |
| 8 | github | repos: people KGs, persona RAG, digital twins, people search | gh-sweep (script) + README reads of top 30 | — | script + 30 | — |

Blind map: 2 Haikus with the domain only. Checkers: 2. Wireframes: 3 (person, explore, advisor).
