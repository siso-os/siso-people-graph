# gap-said: primary sources for "everything Elon Musk said"

Run date 2026-10-14. 24 rows in rows/gap-said.jsonl, all verified=null. About 33 tool calls used. GitHub API was rate-limited mid-run, so the GitHub repo search was not completed. trumptwitterarchive.com and web.archive.org could not be fetched.

## 1. What we can join to the Elon corpus now

| Source | Coverage | Licence | Join key | Use |
|---|---|---|---|---|
| Zenodo 15062791 (Profiling Musk's X evolution) | 60,567 tweets (D1) and 18,262 (D2), 2010-06-04 to 2025-01-24 | CC-BY-4.0 (stated on record) | tweet_id, created_at | Cross-check and licence-clean subset of our 92,380 Zenodo corpus; the window overlaps. |
| Kaggle dadalyndell "2010 to 2025 (April)" | through 2025-04-13 (snippet) | not read | tweet_id | Overlap check only; confirm licence on Kaggle before use. |
| Kaggle aryansingh0909 "Daily Updated" | unverified; snscrape-based | not read | tweet_id | Only post-May-2025 candidate, but freshness is doubtful. |
| HF dawood/elon-tweets | old (Jan 2023 upload) | afl-3.0 | text | Small, adds little. |
| HF MasaFoundation/elonmusk_elon_tweets | 1K-10K rows, updated Aug 2024 | not visible | text | Little value. |

Gap that remains: no verified dataset of Musk X posts from 2025-05 to 2026-10. The only route found is a paid export (Circleboom) or own scraping, both with X-terms risk. Our 92,380-post corpus should be treated as ending around May 2025.

Spoken-word joins (no X posts):
- Lex Fridman #400 (2023-11-09) at lexfridman.com/elon-musk-4-transcript: speaker labels, clickable timestamps, human generated, about 148.8k characters. Best template for a quote row (URL + timestamp anchor). Other Musk Lex episodes not yet checked.
- Lexicap (karpathy.ai/lexicap): Whisper transcripts of Lex episodes. The fetch returned the Karpathy homepage, so the page was not reached. Re-check the URL before building on it.
- JRE #2223 (TurboScribe share page, Nov 2024): machine transcript, copyrighted content, research use only.
- Factbase Trump/Hannity/Musk (2025-02-18): dated, speaker-labelled, Roll Call.
- Not found: a complete index of Musk interviews. Search results were scattered transcript pages; the Economist July 2026 transcript appeared only on an aggregator and was not checked.

Quote sites (pointers only, not corpora): Graciousquotes (7 checked, 3 verified), Glasp author page (~156 quotes, no dates), Garin Substack, and The Book of Elon (curated, Jorgenson; 2026 edition listed). Use them to seed quotes, then trace each to a dated primary source.

Deleted posts for Musk: no tracker found. Politwoops and similar archives cover officials only.

## 2. Transcript indexes for tech YouTubers

- Filmot (filmot.com): self-reported 1.7B caption entries, 1.5B videos, 84M channels; boolean, proximity and wildcard search; max 200 channels per search. No API docs, pricing or export on the page. Timestamp link behaviour not described. Verify before bulk use.
- YouTube itself: most captioned videos have a Show transcript panel with in-transcript search and clickable timestamps. Auto-captions can be wrong (YouTube Help).
- Glasp: highlights of transcripts with timestamp links to the video; free tier with daily limits; paid price not found.
- Snipd: podcast app, speaker transcripts, keyword and semantic search; free 2 episodes/week; premium about $6.99/month per Toolradar; no API.
- Podscribe.io: transcription service, pricing conflicts ($5 vs $15 start). Name collides with an ad-tech product.
- ytks: no match. Closest are the Chrome extension "YouTube Transcript Search" (bulk transcripts per channel, timestamp results) and Apify "YouTube Transcript Keyword Search" (from $10 per 1,000 results).

## 3. Per-person archive UI

- Trump Twitter Archive: could not be fetched today (DNS error on www, command failure on bare host, Wayback blocked). Status BLOCKED, not confirmed live. The companion GitHub repo bpb27/political_twitter_archive has per-account folders with four files: a CSV, user_ids.json, user_long.zip (full JSON with metadata) and user_short.zip. The README says "Feel free to use the data", no licence stated.
- Politwoops (ProPublica): "no longer maintained"; partial snapshot 2025; original Sunlight 2016-12-11; last updated 2022-11-21. Tracking of deletions stopped in early 2023 when X changed API access (Venturebeat, 2023). The per-tweet page shows the post with a deleted label. Date, device and search fields not confirmed.

Best per-person archive UI pattern to copy (from the sources above):
1. One page per person with a search box and a list of posts, newest first.
2. Each post shows its timestamp, a permalink, and a deleted label where applicable (Politwoops).
3. Bulk download per account: CSV for spreadsheets, full JSON with metadata for analysis (bpb27 layout).
4. Keyword search across the list, with a saved-search or alert option (Filmot style).

For quotes: each quote row should carry the source URL and a timestamp anchor (Lex Fridman / YouTube style), a verified flag (Graciousquotes style), and the platform (X, podcast, interview).

## Licence and ToS summary

- Zenodo record: CC-BY-4.0.
- HF dawood: afl-3.0. Others: not read.
- Kaggle: not read on any page (rendering failed). Check before use.
- All X post content: X terms apply, even where the dataset licence is open.
- Transcripts from Lex Fridman, JRE and Fox: copyrighted; use for research and cite, do not republish.
- Filmot, Snipd, Glasp, Apify, Circleboom: check ToS; bulk scraping of YouTube or X is restricted.

## Next steps

1. Pull the Zenodo CSVs and match on tweet_id against our 92,380-post corpus; record overlap.
2. Read Kaggle licence fields with a browser or the Kaggle API (not run here).
3. Re-check karpathy.ai/lexicap and the Lex Fridman transcript index for a list of Musk episodes.
4. Retry trumptwitterarchive.com later; GitHub search needs the rate limit to reset.
