# {title}

| | |
|---|---|
| Source | {url} |
| Channel / host | {channel} |
| Speakers | one row per speaker: name · graph `person_id` · Wikidata QID · role (host, guest) |
| Published | {date} · {duration} · {views} views |
| Processed | {processed} by output-factory v1 · quotes checked: N of N |
| Files | [transcript](transcript.md) · [chunk notes](notes/) · [meta](meta.json) · [feedback](feedback.md) |

## 1. In one paragraph
What the video is, who is speaking, and the single most important thing in it. Five sentences or fewer.

## 2. Why it matters to SISO
The 3 to 5 points that change what we build or how the fleet runs, each one line, most important first.

## 3. Chapter map (complete: every part of the video is covered)
One `###` per segment, in order, with its start time linked (`[0:12:30](url&t=750s)`) and a plain title.
Under each segment, 3 to 8 bullets on what was actually said: arguments, demos, numbers, examples.
Nothing is skipped because it seems minor. Sponsor reads get one line marked *(sponsor)*.

## 4. Quotes by speaker
Every quotable line worth keeping, grouped by speaker. Each one is a verbatim quote (from the captions, errors
included) followed by its timestamp link. These rows become the speaker's utterances in the graph
(`utterances.jsonl`), so the speaker must be right; mark *(speaker unclear)* rather than guess.

## 5. Ideas → SISO actions
| # | Idea (from the video) | Where it applies (seat, repo, loop) | What we'd do | Effort S/M/L | Priority | Status |
|---|---|---|---|---|---|---|

Every idea in section 3 that could change something of ours gets a row. Status starts at `proposed`.

## 6. Tools, products, repos, models and people named
| Name | Kind | What was said about it | Link | Graph id |
|---|---|---|---|---|

## 7. Numbers and facts stated
Each stated number (prices, users, stars, latencies, dates) with its timestamp. Mark claims that are unverified.

## 8. Doubts, disagreements and things to verify
Where the speaker is selling, contradicts himself or anyone else, or makes a claim we should check before acting on it.

## 9. Verdict and feedback
- **Agent verdict:** adopt, borrow or ignore, and why, in 3 lines.
- **Shaan:** *(left empty for his feedback; `feedback.md` keeps the history)*

## 10. Related
Other library entries, research files and graph people this links to.
