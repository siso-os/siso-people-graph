# prior-art notes (people + org graph)

Rows: `rows/prior-art.jsonl` (20 rows). Searches: about 35 tool calls. Items marked "snippet" came from search results, not a fetched page.

## 1. Data models

| System | Entity | Claim / statement | Source / provenance | Identity merge | Update cadence |
|---|---|---|---|---|---|
| Wikidata | item (Q) | statement = property + value + qualifiers + references + rank (preferred/normal/deprecated) | per-statement references; ~68% referenced (2021 paper) | no merge; duplicates resolved by editors and "same as" style links | live edits; public RDF dumps weekly |
| Factoid prosopography (KCL, PBW) | person, place, source | factoid = a spot in a source saying something about person(s) | source is the unit; interpretation left to user | person assembled from factoids; no truth flag | project-based, rebuilt per project |
| SNAP:DRGN | person URI | minimal RDF person core | URI shared across datasets | crosswalk by shared URI, not merge | project pilot |
| Trismegistos People | person (PER), attestation (REF) | person linked to documents via REF | document-level | TM IDs cross-reference other DBs | periodic releases |
| VIAF | cluster per person/corporate body | source authority records (LC, GND, BnF...) | source record IDs kept | algorithmic cluster across national files | monthly re-cluster; IDs can split or merge |
| FamilySearch Family Tree | person profile | fields with per-field choice on merge | sources attached to profile | person-level merge with survivor, field picks, change log, Undo Merge | live; 1.74B names (July 2025) |
| WikiTree | person profile | free-text biography plus fields | sources in profile | owner-consent merge, irreversible | live |
| Geni | person profile in user trees | tree links | MyHeritage matching | match + owner approval | live |
| GLEIF | legal entity (LEI) | Level 1 record; Level 2 parent relationship; exception record | LEI registrant data | LEI is the key; no merge | 3 Golden Copies daily + deltas |
| OpenCorporates | company, officer, jurisdiction | moved from datum to statement model (provenance per fact) | source URL per statement | jurisdiction + number key | continuous |
| ROR | research organisation | name, type, relationships (versioned JSON) | curated | stable ROR ID, crosswalk to GRID/ISNI/Wikidata | versioned dumps (v1.74 Nov 2025) |
| CIDOC-CRM | actor (E39, E21 Person, E74 Group), appellation (E82) | life facts as events (birth, death, formation) | P-properties | appellations per actor; no built-in merge | standard (ISO) |
| Nanopublications | assertion | named graph of assertion + provenance + pubinfo | provenance graph in same record | none; Trusty URI for immutability | per publication |
| PROV-O | entity, activity, agent | wasGeneratedBy, wasDerivedFrom, wasAttributedTo | Bundle (a named set), not per triple | n/a | standard |
| Splink | record | pairwise match probability | none | Fellegi-Sunter clusters into entity IDs | library |
| nomenklatura (OpenSanctions) | statement (prop, value, dataset, date) | judgement pair (same / different) | statement carries dataset + date | canonical ID minted per positive judgement; merge = view | per dataset release |
| YAGO 4.5 | entity typed by schema.org upper taxonomy | Wikidata facts with SHACL constraints | Wikidata-derived | inherits Wikidata | periodic release |
| Freebase | topic (type + properties) | fact in graph; mediators for n-ary facts | few per-fact sources | Metaweb merges | frozen at 2016 |
| Google KG | entity | fact (closed) | closed | closed | closed |
| Diffbot KG | person, org entity | extracted fact | not exposed in these pages | vendor merge | claimed every 3-5 days (vendor) |
| OpenAlex author | author profile | derived from works and authorships | work-level | disambiguation into person IDs; fix by changing works | updated_date stamp |

Scale anchors: Wikidata ~123.6M content pages (captured undated), about 17B-20B triples depending on year, growing ~1B triples/year. Google KG 500B facts on 5B entities (2020). Diffbot 1.3B persons and 715M orgs (2021 whitepaper). FamilySearch 1.74B names (2025). OpenCorporates 220M companies and 310M officers. Trismegistos 380,676 persons. GLEIF and ROR are the best open org-identity sources with clear cadence (daily; versioned).

## 2. Five design ideas to copy

1. **Statement-level provenance, every value.** Store each value as a statement: subject, property, value, source record ID, source date, rank. OpenSanctions (statement with dataset and date), OpenCorporates (datum to statement migration), Wikidata (references) and the factoid model all converge here. Never overwrite a source record; derive the person view at export.
2. **Factoid-style assertions, not one biography.** Keep conflicting claims as separate assertions with their source (factoid model, PBW). Interpretation (the canonical view) is a layer on top, so disputed dates and names do not get lost.
3. **Crosswalk IDs, not forced merges.** Mint our own stable ID per person and org, and carry an external ID table (Wikidata QID, VIAF cluster, ISNI, LEI, ROR, TM ID, SNAP URI, ORCID, OpenAlex ID). VIAF and SNAP:DRGN show this works at scale; VIAF's monthly re-cluster is the warning that cluster IDs move, so store the source IDs as the durable key.
4. **Reversible merges via a judgement graph.** Store pairwise judgements (same / different / unsure with who and when), compute connected components as a view (nomenklatura, Splink clusters). Undo means changing a judgement, not deleting data. FamilySearch's Undo Merge and WikiTree's irreversible merges show the two extremes; take the first.
5. **Blocking plus probabilistic linkage with an EM-trained model, then human review of the borderline band.** nomenklatura reports 130k entities would be ~17B pairwise comparisons, so blocking is mandatory; Splink does ~1M records per minute on a laptop with unsupervised EM. Use the judgement graph to feed training.

Bonus for cheapness and continuity: take daily deltas where they exist (GLEIF Golden Copy plus four delta windows), and prefer dumps you can re-process over live scraping.

## 3. What killed Freebase, and what to avoid

What happened (sources: Wikipedia Freebase page, Search Engine Land, i-programmer):
- Google bought Metaweb in 2010, used Freebase as a Knowledge Graph input, and in Dec 2014 announced shutdown. The site closed 2 May 2016 after the planned June 2015 date slipped.
- Google's stated reason, as reported: a community-driven effort is better served by Wikidata, which was growing fast. Search Engine Land flagged the volunteer-base risk: when a community changes hands, volunteers stop updating.
- Freebase had ~44M topics and 2.4B facts (Jan 2014), a folksonomy of types where only Metaweb staff promoted user types, and schema changes restricted because apps depended on them.

Lessons to avoid:
- **Single corporate owner and funder.** Freebase's data ran on one company's budget and one company's decision. Put the data in a dump-first, open-licence form that outlives any one host (Wikidata, GLEIF's public files).
- **No per-fact sources.** Freebase stored facts without a per-claim source record, so it could not be audited or repaired from the outside. Build statement-level provenance from day one.
- **Closed schema governance.** Types were promoted by staff, so the community could not evolve the model. Keep the schema public and versioned (ROR's v1 to v2 switch with deprecation dates is a good pattern).
- **Silent API dependency.** Downstream apps broke at shutdown. Publish stable IDs and dumps, not only an API.
- **Ignoring the provenance layer.** PROV-O has no per-triple provenance, so a Bundle or nanopublication-style wrapper must be built deliberately if we want it.

## Gaps still open

- Wikidata humans count and organisation count (not found); Special:Statistics page gives content pages only.
- ISNI, LC NAF, GND merge rules and counts (only VIAF was read).
- PIR record count and its API schema; PBW current person total.
- Geni and WikiTree total profile counts (not in sources read).
- Crunchbase orgs, Pantheon-style person counts beyond held items.
- Wikidata Help:Ranking official page not fetched (rank behaviour from secondary sources).
- Trismegistos About page fetch failed on certificate; counts from search snippet.
- No open dataset found that matches "all notable humans and orgs with per-claim sources, continuously updated, better than Wikidata". Wikidata is still the best open candidate; the nearest rivals (OpenCorporates, GLEIF, ROR, Diffbot) are narrower or closed. Falsifier not met.
