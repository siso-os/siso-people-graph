# Extraction slice: routes, costs and pipeline (2026-10-14)

Scope: X, YouTube and podcasts, attributed to the right speaker, deduplicated, dated. Public data only. Rows are in `rows/extraction.jsonl` (26 rows). Nothing here is verified by a run; `verified` is null on every row.

## Bottom line

1. **Falsifier not met.** The cheapest route to all of one person's X posts that is also legal is the official X API pay-per-usage plan ($0.005 per post read, 3M reads/month cap). X API Pro ($5,000/mo) is legacy-only and is no longer the comparator. The cheap per-post routes (SocialData $0.0002/post, TwitterAPI.io about $0.00015/post, Apify about $0.18–0.40 per 1,000) are all scrapers that sit against X's 2023 ban on scraping. They are cheaper, but they are not the legal route.
2. **X recommendation:** official pay-per-use for incremental, legal pulls. Use a scraper only for a one-off back-fill if the owner accepts the ToS risk. Do not use Nitter or XCancel (X sent cease-and-desist letters on 24 Aug 2026; status unstable).
3. **YouTube recommendation:** yt-dlp for the upload inventory (free), the YouTube Data API for dates (1 unit per call), youtube-transcript-api or yt-dlp for captions (free, IP-blockable), and a local or hosted ASR fallback when captions are missing.
4. **Podcast recommendation:** Podcast Index (free) first for publisher transcripts, then Taddy ($75–150/mo) for transcripts the publisher did not ship, then local ASR.
5. **Speaker attribution:** pyannote community-1 gives anonymous turns (CC-BY-4.0, gated). Names come from an enrolled voiceprint (pyannote WeSpeaker embedding) plus a text cue (channel owner, host introduction, LLM quote-attribution pass). This step is the least proven part of the pipeline.

## Cost model per person (example: Elon Musk)

Assumptions are mine, not measured. Replace them with real counts before budgeting.

- Assumed X post count: 100,000 (unverified; check the profile's post count first). Cost per 1,000 posts drives everything else.
- Assumed YouTube/podcast audio: 500 hours of uncaptioned audio for the ASR case.

| Step | Route | Unit price | Example cost |
|---|---|---|---|
| X history, legal | X API pay-per-use | $0.005/read | 100k x $0.005 = **$500** (cap 3M reads/mo; delta pulls afterwards are small) |
| X history, scraper | SocialData.tools | $0.0002/post | 100k x $0.0002 = **$20** (ToS risk) |
| X history, scraper | TwitterAPI.io | about $0.00015/post | about **$15** (ToS risk) |
| X history, scraper | Apify Tweet Scraper (kaito) | $0.18–0.25 per 1,000 | **$18–25** (ToS risk) |
| X history, scraper | Apify Tweet Scraper V2 (apidojo) | $0.40 per 1,000 | **$40** (ToS risk) |
| X history, self-run | twscrape / twikit | $0 software | account cost and ban risk |
| YouTube inventory | yt-dlp + Data API playlistItems/videos.list | 1 unit per 50 items | a 5,000-video channel is about 200 units/day, inside the 10,000/day default |
| YouTube captions | youtube-transcript-api / yt-dlp | $0 | IP-blocking risk; use a proxy |
| YouTube audio ASR (500 h) | Deepgram Nova-3 batch, diarization included | $0.26/hr PAYG | **$130** |
| YouTube audio ASR (500 h) | AssemblyAI Universal-3.5 Pro + standard diarization | $0.23/hr | **$115** |
| YouTube audio ASR (500 h) | ElevenLabs Scribe | $0.27–0.40/hr (sources conflict) | **$135–200** (diarization unclear) |
| YouTube audio ASR (500 h) | faster-whisper / whisper.cpp on Mac, local | $0 software | compute time only (no benchmark run here) |
| Diarization | pyannote community-1 | $0 software | GPU time |
| Podcast transcripts | Podcast Index | $0 | publisher-provided only |
| Podcast transcripts | Taddy Pro $75/mo (100 transcripts) or Business $150/mo (2,000) | per month | fixed; overage 2.5c per transcript |

**Elon total, one-time back-fill, illustrative:** about $150–$700 (X history $15–500 depending on route, plus $115–200 for 500 hours of hosted ASR, or $0 if local). **Ongoing monthly:** delta pulls on X (tens of dollars at most on pay-per-use), new YouTube uploads (a few dollars of ASR per month), and a Taddy plan only if podcasts are in scope.

## Pipeline per source

### X (posts, replies, quote-posts)

1. **Acquire:** official X API pay-per-use, incremental by `since_id` (or the newest stored ID), with a monthly read budget. Scraper back-fill (SocialData or Apify) only if the owner approves the ToS risk, and only for history older than the official pull.
2. **Store raw:** each post with `id`, `created_at` (UTC), `author_id`, `referenced_tweets` (retweeted, quoted, replied_to), and the full text. Keep the raw JSON for audit.
3. **Dedup:**
   - Retweets: drop by `referenced_tweets` type "retweeted" (they are not the person's words); keep the original as its own record.
   - Quote-posts: keep as a separate record with the quoted text linked, not merged into the quoted post.
   - Near-duplicates across re-posts and edits: normalise text, then exact hash, then MinHash LSH on 5-gram shingles (datasketch). For very short posts, SimHash. Threshold to start: Jaccard about 0.8 (a starting guess, not measured here).
   - Canonical record = earliest `created_at`.
4. **Attribute:** the author is known from the account, so no speaker ID is needed. Speaker ID is needed only for posts that quote someone else, which the `referenced_tweets` field handles.
5. **Date:** `created_at` from the API; keep the timezone as UTC.

Risks: official route is low risk. Scrapers are high risk (X 2023 scraping ban; the June 2025 developer-agreement change bans using X content to train frontier models). Do not store cookies or account credentials in the repo. Nitter and XCancel are unstable after August 2026.

### YouTube (uploads, captions, interviews and podcast-style videos)

1. **Inventory:** `yt-dlp --flat-playlist --dump-json` on the channel's uploads playlist (free, latest release 2026.08.19). Confirm dates with YouTube Data API `playlistItems.list` and `videos.list` (1 unit each).
2. **Captions:** youtube-transcript-api or `yt-dlp --write-auto-subs` (free). Store the caption type (manual or auto) on each record. Auto-caption accuracy was NOT measured in this run; sample 10 videos and hand-check before relying on it for quotes.
3. **Audio fallback:** when there are no captions, download audio locally, then ASR (whisper.cpp medium on the Mac, or Deepgram/AssemblyAI for speed).
4. **Diarize:** pyannote community-1 with `num_speakers` (or min/max) from the video metadata. Output turns with timestamps.
5. **Attribute:**
   - Solo creator: all turns belong to the channel owner (verify on a sample).
   - Interview or panel: enroll each known guest and host from clean clips with the pyannote WeSpeaker embedding; match each SPEAKER_xx cluster by cosine score; mark low-score clusters as unknown.
   - Text cue: host introductions and on-screen names; LLM quote-attribution pass over the transcript (see paper row "Who Said What").
6. **Dedup:** the same talk often appears on YouTube and as a podcast. Align transcripts by time and text overlap, and keep one canonical copy plus a pointer to the other.
7. **Date:** `publishedAt` from the Data API, or the upload date from yt-dlp. Note that live streams and premieres may carry a different date.

Risks: YouTube ToS restricts downloading, so keep to metadata and captions where possible and never redistribute media. youtube-transcript-api warns that YouTube blocks most cloud IPs and bans static proxies; use rotating residential proxies. Cookie auth in that library is currently not available. Undocumented endpoints can break without notice.

### Podcasts

1. **Inventory:** Podcast Index API (free key, no card). Use the feed-by-ID episode endpoints to list episodes with dates.
2. **Transcripts first:** Podcast Index exposes publisher transcripts through the `podcast:transcript` RSS tag (field names not verified here; check the live docs). Use them when present; label them as publisher-supplied.
3. **Paid transcripts:** Taddy for episodes without a publisher transcript: Pro $75/mo covers 100 transcripts; Business $150/mo covers 2,000; webhooks need Business.
4. **Local ASR** for the rest, then the same diarization and attribution steps as YouTube.
5. **Dedup:** the same episode in several feeds or as a YouTube upload; use the audio hash or the transcript MinHash.

Risks: publisher transcripts can be wrong or missing speakers. Check the feed's licence terms. Taddy price pages conflict across sources (the 1M-request tier appears only on an old Notion page), so confirm at checkout.

## Speaker and quote attribution (cross-source)

- Diarization gives turns, not names. pyannote community-1 beats 3.1 on AMI, DIHARD 3 and RAMC, and is slightly worse on REPERE.
- NVIDIA Sortformer v1 is CC-BY-NC-4.0 (non-commercial); do not use it in a commercial product without checking the exact checkpoint.
- Naming a turn: enrolled embedding match (pyannote WeSpeaker, CC-BY-4.0 per model card), plus text cues. No match threshold or accuracy number was found; measure on the NewsInterview corpus (500 interviews, speaker names in transcript) before trusting it.
- Biometric caution: voiceprints of real people are sensitive. Keep enrolment clips and embeddings out of git, and keep them consent-based.

## Risks, ranked

1. **Legal (X):** any scraper is against X's terms. The official pay-per-use API is the only clean route. Enforceability of anti-scraping clauses is contested, but do not rely on that.
2. **Account and IP blocks (YouTube):** IP blocking is the main operational risk. Budget for proxies.
3. **Attribution accuracy:** speaker naming is the least proven step. Hand-check a sample per person before publishing any quote.
4. **Maintenance:** twikit is intermittent; Nitter is down or unstable; youtube-transcript-api and yt-dlp break when YouTube changes. Health-check every route before each batch.
5. **Price drift:** X prices conflict across vendor blogs ($0.005 vs $0.01 vs $0.015 per create). Re-check the live console before any budget decision.

## Gaps (still missing)

- No measured auto-caption accuracy for YouTube; no WER test on any ASR route.
- No Apple silicon benchmark for faster-whisper or whisper.cpp (faster-whisper has no Metal path; whisper.cpp is the Mac route).
- Official X developer-agreement page returned HTTP 402; the clauses here are from secondary coverage. Retention and deletion terms were not found.
- Podcast Index transcript endpoint field names not verified (docs site did not render).
- ElevenLabs Scribe per-hour price and diarization surcharge still conflict across sources.
- datasketch (MinHash/LSH) was not fetched; its licence and last release are unverified.
- No Zenodo or Kaggle archive of any target person's posts was found; the Hugging Face Musk datasets found are small (under 10K rows) and of unknown licence.
- Person post counts (the main cost driver) are not known; the Elon numbers above assume 100k posts.
- Speaker-ID threshold tuning for pyannote WeSpeaker embeddings is undocumented here.
