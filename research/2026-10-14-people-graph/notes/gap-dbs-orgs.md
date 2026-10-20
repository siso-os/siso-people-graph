# gap-dbs-orgs notes (2026-10-14)

Measured today unless marked "search" (search snippet only) or "est." (my estimate, not measured).

## 1. People and org databases

| Source | Size / count | Licence | Alive / status | Note |
|---|---|---|---|---|
| DBpedia (ontology page) | Person 1,592,912; Organisation 317,867 | CC BY-SA 3.0 + GFDL (about page) | Live endpoint answers | Live count of dbo:Person with en label = 1,277,612. Release number not on page. |
| Muck Rack | no count found | quote-only, API licence not found | sells quotes | Third-party pricing only. |
| Golden.com | "millions" (directory) | not found | not confirmed | No primary page reached. |
| LinkedIn Economic Graph | aggregate indicators only | partner/research terms | public programme | No person- or company-level dump is public. |
| Clay | aggregator of 150-200+ providers | commercial | active | Not a proprietary DB; "100M+ contacts" unverified. |
| Dealroom | 4M+ profiles (third-party) | commercial; API on Enterprise | active | Premium EUR 12,500/yr; Premium Plus EUR 17,000/yr. |
| Harmonic.ai | 20M+ companies, 150M+ people (pricing page); 35M+ / 195M+ (newer vendor page) | commercial | active | Refresh cadence claims conflict. |
| CB Insights, PitchBook, Owler | NOT researched (budget) | - | - | Still missing. |
| OpenCorporates | no company count on terms page | DB under ODbL; site content CC BY-SA; free use limited to Permitted Users; corporations not permitted | active | Bulk = "contact us". Share-alike applies to derived DBs. Scraping prohibited. |
| ROR | API 141,387 (measured); Zenodo v2.5 124,882 (31 Mar 2026, search) | CC0 1.0 | monthly updates | Resolve the count gap before quoting. |
| GLEIF | LEI API total 3,460,635 (measured) | CC0 stated only by a third-party doc, not confirmed on gleif.org | Golden Copy 3x daily | Level 2 gives parent relationships. |
| Wikidata Q43229 (organisation) with P279* | 4,986,530 (QLever); 4,986,579 (WDQS) | CC0 | live | Humans (P31 Q5): 13,738,078 (QLever). |

Wikidata counts were measured with COUNT queries on the public endpoints; subclass closure via `wdt:P31/wdt:P279*`.

Conclusion for the graph: the free, licence-clean spines are Wikidata (CC0), GLEIF (CC0 pending check), ROR (CC0), and DBpedia (CC BY-SA, share-alike). OpenCorporates is ODbL share-alike with commercial limits. Harmonic, Dealroom, Muck Rack, Clay, PitchBook and CB Insights are paid overlays with no bulk redistribution rights.

## 2. Pantheon

- Pantheon 2.0 exists as dated person CSVs: 2019, 2020, 2025 (`person_YEAR_update.csv.bz2`) on the pantheon.world download page. The 2025 file has 126,582 person rows, 12.35 MB compressed, 38.9 MB uncompressed (measured).
- Columns include `wd_id` (Wikidata Q-id, the join key), `hpi_raw`, `l` (language editions), `occupation`, birth and death place with lat/lon and geonameid.
- Pantheon 1.0 (legacy) TSVs: `legacy_pantheon.tsv.bz2` 643 KB, plus wikilangs and pageviews 2008-2013. Paper is CC BY 4.0. Pantheon 1.0 has 11,341 biographies with more than 25 language editions.
- Site footer: "more than 85,000 biographies", which conflicts with 126k rows. Treat the CSV as the authority, with a caveat.
- Licence for the 2.0 files is NOT stated on the dataset page. Check `/en/data/permissions` before redistributing.
- HPI formula: the exact Equation 4 with weights was NOT retrieved. The PDF fetch exceeded the size limit, and the Nature page redirected to a login. A 2025 paper (https://arxiv.org/pdf/2505.09399) gives an approximation: log10(V) + ln(L) + log4(A), minus (70-A)/7 when A<70, R^2 = 0.76 against Pantheon HPI. The original adds a coefficient-of-variation term and an entropy-based L*. Next step: fetch the Scientific Data article (doi 10.1038/sdata.2015.75) from a browser or PMC, or the arXiv PDF on the Mac mini.

## 3. Wikidata dump practicalities

**Sizes (measured 2026-10-14, dir 20261012):**
- latest-all.json.bz2: 103.4 GB compressed
- latest-truthy.nt.bz2: 43.5 GB
- latest-all.nt.bz2: 196.2 GB
- latest-all.ttl.bz2: 125.8 GB
- Uncompressed full dump about 1.6 TB (Meta, Jan 2026).

**Formats and cadence:** JSON dumps weekly (one entity per line in a JSON array). Truthy NT keeps best-rank direct values only, no qualifiers or references. Incremental daily dumps: https://dumps.wikimedia.org/other/incr/wikidatawiki/. Live change feed: EventStreams `recentchange` (search snippet; check wikitech before use).

**Tools:**
- Named on the official download page: wdumper (filtered RDF), qwikidata (Python), wd2sql (Rust, JSON to SQLite), WDSub, JsonDumpReader, simple-wikidata-db, gitlab.com/tozd/go/mediawiki (Go).
- NOT on the page and NOT verified: wikidata-filter, KGTK. Do not cite them as official.
- QLever: public endpoint works (needs PREFIX). Local QLever is heavy; a 2023 Freiburg benchmark used a 128 GB RAM, 7.1 TB NVMe box (search snippet). A Phabricator thread reports about 7 hours to index Wikidata main, but the numbers conflict (search snippet).

## Recommended T0 skeleton on the Mac mini (est., not measured)

Goal: humans (Q5) plus organisation-class items (Q43229 closure), with labels and `wd_id`, one row per Q-id.

Preferred route: streaming two-pass filter over `latest-truthy.nt.bz2`, not the full JSON.

1. **Disk check first.** Run `estate storage --help`, then budget for the 43.5 GB download, about 2x for temp files, and a few GB for outputs. Est. total 100-150 GB free. The mini is the target, so pulling there is fine; do not put it on the laptop.
2. **Download** with `curl -C -` (resumable) to the mini's data volume, not into the repo. Est. 30-90 min on a good link.
3. **Pass 1 (P279 closure):** `lbzip2 -dc` (or `pbzip2`) piped to a grep for `<http://www.wikidata.org/prop/direct/P279>` lines. Build the set of Q43229 descendants in Python or Rust (a few hundred thousand subclass edges). Est. 1-3 h on an M-series mini with parallel bzip2.
4. **Pass 2 (instances):** same stream, grep `P31` lines whose object is Q5 or in the org-closure set. Write Q-id, type, and label for `@en`. Est. 1-3 h. Output est. 5-10 GB TSV or Parquet.
5. **Cross-check:** compare the counts with the QLever numbers above (13.7M humans, 4.99M org-class). A small drift is expected; a large one means the filter is wrong.
6. **Incremental:** apply the daily `other/incr` files or EventStreams events for changed Q-ids. Re-run the closure weekly.

Alternative if the mini is short on disk or time: pull the JSON dump (103 GB) with `wd2sql` or `qwikidata` on the mini. That is larger and slower, and gives qualifiers, so it is best only if qualifiers are needed for T0.

Alternative for a small test: paginate QLever `SELECT ... LIMIT/OFFSET` over Q5 with an org filter. Good for a 100k-row test; not for a full skeleton.

## Still missing (budget)
- CB Insights, PitchBook, Owler: not researched.
- Golden.com alive status: no primary page.
- Muck Rack: no primary page or size.
- GLEIF CC0 on gleif.org: not confirmed.
- DBpedia current release number and live-endpoint graph list.
- Pantheon HPI Equation 4 weights.
- Wikidata human count on WDQS (timed out); QLever value used instead.
