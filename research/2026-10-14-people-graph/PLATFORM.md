# PLATFORM: every person, run on GitHub + Cloudflare (Opus, 14 Oct 2026)

Sits beside `SYSTEM.md`. That file is the data model. This one says where the model lives, how it runs and how
agents use it. No new research went into it: the inputs are our notes, SYSTEM.md and what we already hold.

**In one line:**
- **Git** holds what has been *decided*: code, merges, the watchlist, consent and packs.
- **Cloudflare R2** holds what is *bulk*: the Parquet lake.
- **GitHub Actions and Worker crons** do the *work*.
- **A Cloudflare Worker** *serves* the pages, and an MCP server lets agents use them.
- **The Mac mini** stores nothing. It is an optional runner only.

## 0. Decisions taken from Shaan's 14 Oct answers (questions still open are at the bottom)
1. **David Andre:** a YouTuber, confirmed. The channel is David Ondrej's. The YouTube adapter checks the channel ID
   the first time it runs.
2. **"Cueb":** dropped from watchlist v0. Nobody knows who it is.
3. **Matthew Miller:** the BridgeMind founder, confirmed.
4. **Transcripts:** captions cost nothing, so every video from a watched person gets its captions. Audio is
   transcribed only for videos with no captions that are on the pick list. Shaan adds a video by putting its URL in
   `watchlist/picks.txt`.
5. **Advisor:** answers for everyone in text, quoting only public words verbatim. Nobody gets a voice or likeness
   without opting in.
6. **Not the mini:** it has 36 GB free of 228 GB, and `estate storage` returns HOLD (`machines/fleet.json`, probe at
   12:37 on 14 Oct). Shaan's instinct is right: nothing big goes there.

## 1. How do we map every person who ever lived? (first principles)
1. **A person can only enter the graph if a record names them.** About 117B people have ever been born, but most
   left no record. So "every person" means every person named in any record we can reach. The size is bounded by
   records, not by humanity: roughly 1-2B named people at the outside *(estimate)*.
2. **Every row is one of three things, and only the third is a person:**
   - a **mention**: a name in a record. It is cheap and close to unbounded.
   - a **candidate**: mentions grouped together.
   - an **entity**: a confirmed person or org.

   Entities grow as judgements land. That is the honest way to count "everyone".
3. **Breadth comes from bulk dumps, ordered by people per dollar.** All of these are free:

   | Source | People | Format |
   |---|---|---|
   | Wikidata | 13.7M humans and 5M orgs | one dump, CC0 |
   | Authority files (VIAF, ISNI, LoC, GND) | tens of millions | dumps |
   | OpenAlex | 96M authors | S3 snapshot |
   | ORCID | — | dump |
   | Our 79k books | the long tail of history | named-entity pass: every person mentioned, back to Socrates' contemporaries |
   | GitHub and crates (we hold 245k) | accounts | an account is **not** a person until it is linked |

   Closed genealogy sets such as FamilySearch's 1.74B are skipped. WikiTree and Find a Grave are used one person at a
   time, never in bulk.
4. **Depth comes from attention (tiers T0-T3 in SYSTEM.md §1).** Scraping is paid for only for people someone
   watches.
5. **The long tail grows on demand.** When an agent asks about someone who is missing, the resolver mints a stub on
   the spot from live lookups: Wikidata search, a GitHub user, a YouTube channel. It then queues that stub for T0.
   Coverage grows where questions land.
6. **Storage is not the cost.** A T0 row is about 200-300 bytes in zstd Parquet, so 100M entities take roughly
   30 GB. On R2 that is about $0.45 a month, and egress is free. The real costs are API reads (X) and audio
   transcription, and both are gated by tier. *(Byte sizes are estimates. The first Wikidata job measures them.)*

## 2. Where each piece lives
| Layer | Where | What is in it | Why there |
|---|---|---|---|
| Code | `sisodias/siso-people-graph` (this repo) | adapters, schemas, resolver, Worker, MCP | normal repo |
| **Decided layer** | new repo `sisodias/siso-people-graph-data` | `judgements/*.jsonl`, `watchlist/`, `consent/`, `picks.txt`, `packs/<id>/pack.json + PACK.md` | Every merge or split is a commit you can diff and revert. A pull request is the review queue. It stays small: 1M judgements is about 150 MB, sharded. |
| **Bulk lake** | R2 bucket `people-lake` | `raw/source=<s>/run=<id>/*.parquet` (statements), `views/` (entity, work, utterance), `serve/` (per-entity JSON, atlas points) | zero egress, about $0.015/GB-month, and any client can read Parquet over HTTP range requests |
| Backup | GitHub Release assets on the data repo | monthly snapshot of `views/`, sharded under 2 GB per asset | a free second copy that sits outside Cloudflare |
| **Heavy jobs** | GitHub Actions (scheduled, matrix-sharded) | dump filters, resolve, build views, pack builds, D1 import | Free minutes on public repos; 2,000/month on a private one. 4 cores, 16 GB, about 14 GB disk, 6 h per job. |
| **Light polling** | Cloudflare Worker cron triggers | YouTube RSS, GitHub events, blog RSS, X `since_id` | Seconds of CPU per poll. Raw items go to R2 and the next Action picks them up. |
| **Serving** | Worker on `people.sisolabs.space` + D1 + R2 | D1 holds the hot index (search, lists, cards; sharded by id-hash if it nears the 10 GB-per-database cap). Widgets read precomputed JSON from R2 at the edge. Vectorize covers T3 utterances only, for the advisor. | No server to run, and caching is free |
| **Agents** | remote MCP server on the same Worker, plus direct DuckDB | see §4 | every seat reaches the graph the same way |
| Optional | the Mac mini as a self-hosted runner | jobs that need a logged-in browser (camofox) or long local ASR | It stores nothing. The jobs fall back to the Groq API if it is off. |
| Laptop | nothing | `work.sqlite` moves to the lake once | |

**Privacy line:** both repos and the bucket stay **private** to start. The data is compiled from public records,
but a public dump of living people needs a consent and erasure path first (the `consent/` folder and a takedown
form). The Worker serves public pages only at T0, plus watched public figures. If private Actions minutes run out,
the fallback is a self-hosted runner on the mini or paid minutes. *(All the limits in this file are from memory and
were not re-checked today. The first job prints the runner's real disk and RAM.)*

## 3. The write path: how data keeps coming in
```
adapters (Actions or Worker cron)
  → R2 raw/ statements (append-only, by run_id; a cursor per source lives in the data repo)
  → nightly Action "resolve":
      1. hard keys (QID, P2037 GitHub, P2002 X, P2397 YouTube, VIAF, Gutenberg id)
      2. Splink probabilistic matching over the rest
      → judgements: score ≥ 0.95 is committed straight to the data repo;
        0.6-0.95 opens a PR (Haiku checker first, then Shaan only for disputed cases);
        below 0.6 is dropped
  → Action "build": entity views (statements + judgements) → serve/ JSON → D1 import → atlas points → deploy
```
- Nothing overwrites anything.
- A bad merge is fixed by reverting a commit, and the next build runs clean. That fixes the double Socrates for good.

## 4. The read path, for pages and for agents
- **Pages** go Worker → D1 (search, lists) → R2 `serve/entity/<id>/*.json`, one file per widget.
- **The UI is a widget system.** The overview is a grid of widgets:
  - identity
  - rank components
  - works
  - said
  - network
  - pack
  - timeline
  - orgs

  Each widget opens its own subpage, `/p/<id>/<widget>`, with the full view. Components come from the UI hub
  (`ui-pick`). The v1 wireframes were structure only, and Shaan does not need anything more from them.
- **The agents' MCP server** (on the Worker, behind a Cloudflare Access service token) offers these tools:

  | Tool | What it does |
  |---|---|
  | `people.search(q, kind?, filters?)` | find people or orgs |
  | `people.get(id, widgets?)` | one entity, with the widgets asked for |
  | `people.said(id, topic?, from?, to?)` | dated verbatim spans with URLs |
  | `people.pack(id)` | the knowledge pack |
  | `people.ask(id, question)` | the verbatim advisor; abstains on silence (advisor-design.md) |
  | `people.who(topic)` | ranked people for a topic: "who is best at X" |
  | `people.propose(statement or judgement)` | writes to an inbox; the next resolve run turns it into a PR |
- **Bulk questions skip the Worker.** An agent runs DuckDB straight against the lake:
  `select … from read_parquet('https://lake…/views/entity/*.parquet')`. Range requests mean only the needed columns
  are read.

## 5. What it does for the rest of the estate
| Who | Gets |
|---|---|
| Great Library (79k books) | Every book is tied to its author, and every person mentioned in a book gets a person page. Search becomes "books by or about X". |
| Law Book | Principles from packs, with several people cited for one rule ("delete before you optimise": Musk, plus others) |
| Agents Hub | Methods turned into skills (`build-like-theo`), each step cited |
| Every agent seat | One shared memory of people: who someone is, who is best at something, what someone said about something, all through MCP |
| Foundry YouTube pipeline | `foundry/pipelines/youtube/scrape_channel_transcripts.py` (yt-dlp + youtube-transcript-api) becomes the YouTube adapter as it stands. The 97-row `people_video_queue` (24 people) is its seed. |
| Shaan | A daily "what watched people said and shipped" digest from the T2 polls, and an advisor per T3 person |

## 6. Build order (replaces SYSTEM.md §8 steps 1-2; the rest stands)
1. **Export what we hold.** `work.sqlite` (1.1 GB) becomes Parquet in R2, one job. Elon's extraction DB does the
   same.
2. **Wikidata T0 job.** An Action streams `latest-truthy.nt.bz2` → lbzip2 → filter (P31 = human or org-class, plus
   the key properties) → Parquet → R2. The 43.5 GB dump is never written to the runner's disk.
   - It prints rows, bytes and minutes.
   - If it runs past 6 hours, split the dump by bz2 block ranges across matrix jobs.
3. **Hard-key join** of our 339k rows onto the Wikidata skeleton, written as judgements. **Falsifier:** if fewer
   than 30% of our rows gain a QID, the design is wrong.
4. **Worker + D1, read only.** Search, the person overview with widgets, and two subpages (works, said), plus MCP
   `search`, `get` and `said`.
5. **Watchlist T2.**
   - Worker crons for RSS, GitHub and X.
   - The YouTube adapter wraps the foundry scripts.
   - Captions for every video from a watched person.
6. **Elon utterances, then pack 1, then `people.ask` for Elon**, measured on the silence test set.

**Monthly cost, estimated:**

| Item | Cost |
|---|---|
| Workers paid plan (D1 included) | $5 |
| R2 | under $1 |
| Actions | $0 |
| X watchlist reads | about $12-15 |
| Groq ASR, picks only | a few dollars |
| **Total** | **about $20-25** |

The mini and the laptop add $0.

## 7. Known mess to fix on the way (from our own data)
- **The YouTube queue doesn't match its output.** `people_video_queue.sqlite` marks 14 rows `transcript_ready`,
  but `~/SISO_Foundry_Data/domains/youtube/channels/` is empty. Step 5 checks where those transcripts went before
  trusting the queue.
- **One table has a bad count.** The `channel_id` column in `people_video_queue.sqlite` has 1 distinct value across
  25 channel names.
- **87% of graph rows are `kind=unknown`.** These are GitHub and crates logins. Under §1 they are accounts, not
  people, until linked.

## Open questions for Shaan (decided defaults in brackets; the build goes ahead on the default)
1. Which Fable is on the watchlist? [Showrunner, the AI-TV studio]
2. Public pages for living people now, or after the takedown form exists? [after]
3. Should the data repo be public (free Actions, CC0 data) or private? [private]
