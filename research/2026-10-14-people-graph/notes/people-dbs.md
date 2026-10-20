# people-dbs: large people databases and how they resolve identity

Run: 2026-10-14. Slice: people-dbs. Rows: `rows/people-dbs.jsonl` (18 rows). Figures are as cited; "unverified" means the number came from a third-party page or was not captured.

## Falsifier result

Hit. Several people databases over 1M people are not on the held list:
- FamilySearch Family Tree: 1.96B people (official company facts, 6 Oct 2026).
- Coresignal: 859M+ employee profiles (third-party, 2026).
- Apollo.io: 240M+ contacts (self-reported).
- People Data Labs: 1.5B (third-party review, March 2026; unverified).
- OpenAlex: 124.7M authors (third-party blog, 9 Aug 2026).
- OpenSanctions: 1,141,784 persons (official licensing page).
- Wikidata: 13.6M humans (older table; treat as floor).

## Comparison table

| Name | People | Licence | API / price | Identity-resolution method |
|---|---|---|---|---|
| Wikidata | 13.66M humans (older table; total items 123.6M) | CC0 (standard, not re-read) | Free SPARQL/API | Editor-created Q-ids, manual merges, external-id properties; Mix'n'match for bulk with human confirm |
| OpenAlex authors | 124.7M (third-party, Aug 2026) | CC0 (not confirmed on fetched page) | Free; no key 10 req/s, free key 30 req/s, annual 50 req/s | ML clustering on six signals (name, co-authors, affiliations, topics, citations, ORCID); NULL author bucket; curations; no public confidence score |
| ORCID | Unverified; ~10.5M active (end-2025, secondary) | CC0 website text; data-file policy not read | Free public API | Self-claimed iD; no merge model |
| FamilySearch Tree | 1.96B persons | Proprietary, free account | Developer API exists (not checked) | User-built; duplicates left unmerged |
| OpenSanctions persons | 1,141,784 | CC BY-NC 4.0 free; commercial licence | Screening API per query with prepaid credits; free for journalists/academics; bulk quote-only | FollowTheMoney entities; yente matcher on identifiers; statements |
| People Data Labs | 1.5B (third-party, unverified) | Commercial | Free 100 credits/mo; Pro $98/mo for 350 credits (~$0.28/credit); 1 credit per match | Input-to-record match (method not described) |
| Apollo.io | 240M+ contacts (self-reported) | Commercial | Search free (up to 50k/search); pay on data returned | Not described; waterfall enrichment across sources |
| Coresignal | 859M+ profiles (third-party) | Commercial | API from $49/mo; datasets ~$1,000+ | Not described |
| Diffbot KG | 10B+ entities, all types (people-only not found) | Commercial | Free 10k credits; $299/mo 250k; $899/mo 1M; 25 credits per KG record | ML entity extraction (method not described) |
| Exa Websets | No people count | Commercial | $49/mo (8k credits), $449/mo (100k); 10 credits per match | Criteria search (method not described) |
| LittleSis | 303,497 people; 1.87M relationships | Licence not verified | Free site | Volunteer editing; citations per relationship |
| VIAF | Counts not retrieved | ODC-BY | Free | Monthly clustering; identifier and string match; ISNI marker fields block false merges |
| Scopus Author Profiles | Not found | Commercial | Subscription | Auto-created profiles; split on change; human merge via feedback wizard (1-2 weeks) |
| UK Companies House officers | Not found | OGL v3 (one source) | Free API, 600 req/5 min | Officer lists per company; DOB month/year only |
| Google KG Search | Not disclosed | Google API terms | Free 100k reads/day | Google entity IDs; Wikidata links |
| S2AND (Semantic Scholar) | Benchmark, not a DB | Open code | Open | Reference AND model; B3 F1 ~90% vs 78.4% production |
| Mix'n'match | Catalogues, not people | Open tool | Free | Candidate match, human confirm/reject |
| Crunchbase | Not found | Commercial | Enterprise; quote-only | Person and org IDs; method not described |

## What we should copy

1. **Identity as a layer, not a merge.** OpenAlex's NULL-author bucket and Scopus's split-on-change show two ways to store uncertainty. Keep unresolved records as a bucket; never force a merge.
2. **Hard keys first.** ORCID and Wikidata Q-ids are join keys. Never merge two different ORCIDs. Use ML only for the remainder.
3. **Matching engine with reasons.** OpenSanctions' yente and FollowTheMoney statements give each match a stated reason. Copy the "identifiers separate true from false positive" rule.
4. **Corrective markers.** VIAF's ISNI marker fields let a curator block a false merge permanently. Add the same flag to our graph.
5. **Human confirm loop.** Mix'n'match's match/no-match/unsure review is the cheapest working crosswalk UI. Copy the queue.
6. **Benchmark before shipping.** S2AND gives B3 F1 on a shared dataset. Score our merges against it.
7. **Pay on return.** Apollo and PDL charge only when a record comes back. Use the same metering for our own lookups.
8. **Citation per edge.** LittleSis puts a citation on every relationship. Our book/repo/video links should carry the same.

## Still missing

- DBpedia, Clay, Muck Rack, Golden.com, LinkedIn Economic Graph, Lightcast: not searched (Golden returned no usable pages).
- Verified totals for ORCID (statistics page did not render), VIAF (2011 figure only), and Scopus Author Profiles.
- Official pricing pages for Diffbot, Coresignal, Apollo, Crunchbase, and OpenAlex (metered pricing claim unverified).
- Merge methods for People Data Labs, Apollo, Coresignal, Crunchbase, and Diffbot.
- Licence text for LittleSis and Companies House (the about page was blocked; OGL is unconfirmed).
- Proxycurl: search suggests its customers moved to PDL, but this was not verified.
