# said-archives: best-in-class and what a quote record must carry

Scope: "everything X said" archives for public figures (Musk first) across X and YouTube/podcasts. Tool calls used: about 29 of 40. Public sources only. Rows: `rows/said-archives.jsonl` (19 rows).

## Verdict on the falsifier

No archive we found beats Factba.se on the combination it has (dated transcripts, video, search) for a single person, but Factbase covers Trump, Biden and Harris only. For Musk we found no per-person archive with dated, URL-cited quotes across X and YouTube. Wikiquote is the closest (year-grouped, dated, cites tweets with URLs), but it is curated and partial. Falsifier not met.

## Best in class, by function

| Need | Best found | Why |
|---|---|---|
| Spoken word, dated, searchable, per person (politics) | Factbase (Roll Call) | Transcripts + video, search, sentiment and keyword tags. Trump/Biden/Harris only. |
| Tweets, one person, with deletions | Trump Twitter Archive | Captures deletions from Sept 2016; device and date per tweet. Current status unverified. |
| Deleted posts, politicians | Politwoops (ProPublica) | About 1.1M deletions; records time-to-delete. Frozen, no API. |
| YouTube subtitle search | Filmot | Claimed 1.7B caption tracks; channel filter; boolean operators. Timestamp links unconfirmed. |
| Podcast transcript search | Tapesearch; Listen Notes API | Phrase search, date filters, export as SRT/VTT/JSON. Counts conflict. |
| Broadcast TV captions | Internet Archive TV News Search | Caption search with station and time. Captions error-prone for names. |
| Single creator, official transcripts | Huberman Lab Premium | Topic/guest/keyword search; paid gate. |
| Quote verification method | Quote Investigator, Snopes | Earliest-source research; "no record found" verdicts. |

## What a quote record must carry

Based on what the best archives show, each quote row should have:

1. **Exact text** plus the surrounding context (at least the preceding and following sentence, or the full tweet thread).
2. **Date** of the original statement in ISO form, with timezone for tweets and the broadcast date for interviews. Use "year only" explicitly when the day is unknown.
3. **Source type and venue**: tweet, reply, quote-tweet, interview, podcast, book, speech. Wikiquote and Factbase both name the venue.
4. **Permanent URL** to the original (tweet ID, episode with timestamp `?t=`, transcript line) plus an archived copy URL (Wayback or local snapshot) when the original may disappear.
5. **Deletion status**: live, deleted (with the date seen missing), or unknown. Politwoops and the Trump archive show this is possible; X API access for deletions is no longer reliable, so record how we checked.
6. **Verification status** with method: original located and read; secondary report only; transcript-only (auto-caption, ASR); not found. The Snopes and Quote Investigator pages show that "not found" must be a stored outcome, not an omission.
7. **Speaker attribution check**: quoted from the speaker vs. quoting someone else (Musk replying to a post, or a host paraphrasing).
8. **Device/client and engagement** where available (Trump archive uses device; Gumroad and Kaggle sets carry likes and retweets).

## Failure modes seen

- Secondary-news citations stand in for the original tweet (Wikiquote, Factbase summaries).
- Captions misspell names ("Musk" to variants) in TV and podcast transcript search; search variants.
- Auto-captioned podcast transcripts (Tapesearch, Lexicap) carry error on names and fast speech.
- Public datasets have ID-only fields (Zenodo hate-speech set), so text must be rehydrated from IDs, and deleted IDs drop out.
- Archives go stale: Politwoops frozen; Trump archive status unconfirmed; Lexicap URL did not confirm.
- Quote aggregators (Quotewise, graciousquotes) show a source line that is often unverifiable (the Naval check).

## Gaps and next steps

- Confirm Trump Twitter Archive is live (Wayback) and its deleted-tweet field.
- Check Filmot for deep-link timestamps and whether it exposes an API, using a logged-out fetch of a sample search.
- Musk-specific: nothing per-person found beyond Wikiquote and secondary datasets. Next: X's own search (`from:elonmusk`, date-bounded) as a verifier, and the Wayback Machine for deleted posts.
- Podcast coverage for Musk appearances (Rogan, Lex, Dwarkesh, Axios): no single archive; plan a per-show transcript pull plus Filmot/Tapesearch cross-check.
- Not covered: Podscribe (search returned nothing), Social Blade (not a quote source), Lexicap (unconfirmed), official Naval archive (none found).
