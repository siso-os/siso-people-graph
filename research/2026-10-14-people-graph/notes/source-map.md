# Source map: a cheap, continuous scrape plan (Opus, 14 Oct 2026)

Entities and channels are in `../source-map.json` (Haiku slice 9, `verified` null). Identity confidence:
- **High:** Elon, Theo, BridgeMind (the company), Convex, Groq.
- **Medium-low:** Matthew Miller as BridgeMind founder (one aggregator source); Fable as Showrunner (could be another
  Fable).
- **Low:** David Andre (no channel by that name; David Ondrej is a phonetic guess, 420K subs); "Cueb" (Cole Medin
  20-30%, IndyDevDan under 15%).

## What to poll, how often, what it costs
| Channel | T2 (watched): metadata only | T3 (deep): content | Cadence | Cost/month (5 people + 3 orgs) |
|---|---|---|---|---|
| YouTube | channel RSS `feeds/videos.xml?channel_id=` (15 latest, free, no quota); a one-off yt-dlp `--flat-playlist` inventory for the back catalogue | captions via youtube-transcript-api **only for videos Shaan picks or under a signed rule** (e.g. "Theo: every video over 100k views tagged benchmarks"); ASR fallback local (whisper.cpp) | RSS hourly | $0 (captions free; local ASR) |
| X | profile counts + latest posts through official pay-per-use, `since_id` | the same posts become utterances; back-fill Elon from the 92k Zenodo set we hold, and pay only for the 2025-05 to now gap | daily | about 8 accounts x ~10 posts/day x 30 x $0.005, about **$12**; Elon alone ~100/day, about $15 |
| GitHub | `gh api users/<u>/events` + repos with ETag (free, 5k req/h) | READMEs and release notes for top repos; benchmarks' results files | daily | $0 |
| Blog / newsletter | RSS where it exists; sitemap diff otherwise (camofox, one tab) | full text as utterances (medium=essay) | daily | $0 |
| Podcasts | Podcast Index search by person name (free) for guest appearances | publisher transcripts only; others queued for Shaan's pick | weekly | $0 (Taddy $75 only if he wants podcasts at scale) |

**Total ongoing: about $25-30/month** for the v0 watchlist. The one-off Elon gap back-fill is about $50-100 on the
official route. Neither is measured yet: this is the falsifier in SYSTEM.md §9.

## The rule for transcripts (needs Shaan)
Default: no transcripts unless picked. A proposed standing rule for him to sign: "per watched person, transcribe
videos with more than N views or titles matching their notable works (source-map.json `notable_works`), capped at M
hours a month". The picker UI is a list of the inventory sorted by views, with a checkbox.

## Worth pulling first (from source-map.json)
- Theo: T3 Code (pingdotgg/t3code, 27,432 stars) and SnitchBench, plus his videos reviewing other builders (the link
  graph between people).
- BridgeMind: BridgeBench, BridgeSpace, BridgeMCP.
- Convex: chef, agent, convex-evals.
- Groq: openbench, groq-api-cookbook.
- Elon: the X gap since 2025-05 and his long interviews (already 84 sources).
