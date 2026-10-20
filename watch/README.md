# people-watch: track people, store what they post, distil it

The `people` command works from any machine. The data and the 6-hourly sweep live on the Mac mini. On the mini,
`people` runs locally; anywhere else it forwards over ssh (alias `mac-mini`).

| Do | Command |
|---|---|
| Track someone | `people add felix-rieseberg --name "Felix Rieseberg" --x felixrieseberg --youtube @handle --why "..."` |
| See who is tracked | `people list` |
| Fetch what is new (the launchd job does this every 6 h) | `people sweep [slug] [--backfill 10]` |
| What did X say about Y | `people said theo "react server components" [--since 2026-09-01]` (use `all` for everyone) |
| What's new | `people digest [slug] --since 2026-10-10` |
| Ship code changes to the mini | `people deploy` |

## Sources, and why each one
- **X:** `api.fxtwitter.com/2/profile/<handle>/statuses` gives the public timeline as JSON, 20 posts per page, with a
  cursor. It is free and needs no login or password; it was checked against @felixrieseberg on 15 Oct 2026.
  - It stops at the first post already stored.
  - Fallbacks, in order: the official X API pay-per-use ($0.005 per read), then camofox on :9377 with a logged-in
    session.
- **YouTube:** yt-dlp (a fresh copy in `app/venv`, with deno for YouTube's JS) lists the newest uploads, then saves
  metadata and English captions for ids not already stored. No audio is downloaded. A video with no captions is
  logged, and audio transcription is only for videos that are picked.

## Store: `~/SISO_Workspace/_data/people-watch` on the mini
This folder is the `people-watch` data plane in `siso-estate/plan/data-planes.json`.

```
people.json                                  who is tracked, their feeds, why
raw/<slug>/x/<YYYY-MM>.jsonl                 one post per line: id, url, date, text, kind, counts
raw/<slug>/youtube/<date>_<id>/meta.json     title, views, duration, description, chapters
raw/<slug>/youtube/<date>_<id>/transcript.*  captions with timestamps (.json, plus .txt)
state.json                                   ids already fetched, per person and source
index.sqlite                                 FTS5 over raw/, rebuilt on every sweep (`people reindex`)
logs/sweep.log
app/                                         code copied from this folder by `people deploy`
```

`people said` returns ranked passages, each with its date and a link back to the source; YouTube links carry
`?t=`. The calling agent does the distilling and cites those links. If nothing matches, that is the answer.
