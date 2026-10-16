# Sauce: pull what matters out of a creator's videos, cheaply, and make the puller better each round

The people graph knows who made what. Sauce is the next layer: what they said that a builder would kick themselves for missing.
That covers the principles, techniques, stances (and how they change), predictions, facts and warnings, each with an exact
quote and timestamp, so every claim can be checked.

## The loop

1. **Transcripts** come from people-watch (`watch/people_watch.py archive <slug>`). Each one goes to the creator's own private
   GitHub repo, e.g. `sisodias/transcripts-theo`, so nothing heavy lives on the laptop.
2. **Extract.**
   - One Haiku per video runs `prompts/vN.md`, reading `transcript.txt` and `meta.json` and writing one JSON.
   - A video costs about 60k Haiku tokens and takes 1-2 minutes; 20 run at once.
3. **Check** with no model: `check.py <round dir>` covers valid JSON, the schema, each quote found in the transcript, its
   timestamp within 30 s, and the strength spread.
4. **Judge** (Opus, `RUBRIC.md`).
   - Read 3 sampled transcripts in full, score their extracts 1-5 on six axes, and skim the rest for patterns.
   - Write `rounds/NN/judge.md` and the smallest prompt change as `prompts/vN+1.md`.
5. **Repeat** on the next 25 videos, re-running the new prompt on the last round's samples to measure the gain.
   - The prompt is done when two rounds in a row gain less than 0.2.
   - After that, rounds run without a judge.

Outputs go to the transcript repo under `sauce/vN/<date>_<id>.json`.

## Rounds so far (Theo, @t3dotgg)

| round | prompt | videos | sample mean | what changed |
|---|---|---|---|---|
| 01 | v1 | 25 newest (2026-09-09 to 10-16) | 3.83 | baseline: fidelity 5, but missed "how he works", inflated strength, duplicates |
| 02 | v2 | next 25 (2026-07-28 to 09-07) | 4.11 (+0.28) | second sweep for prompts, habits, own numbers and changes of mind; strength budget |

## Paused (16 Oct 2026)

Shaan: the value in a video depends on what he is working on when he watches it, so a fixed extraction schema misses it
and spends a Haiku per video. The loop is paused after round 02. Instead, every archived transcript goes into a full-text
index (`watch/transcript_index.py`, on the mini at `_data/people-watch/index/transcripts.sqlite`), and an agent searches
it when a question comes up, linking each hit to the second it was said. That costs tokens per question, not per video.
