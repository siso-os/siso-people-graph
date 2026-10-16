# Round 01 judge: Theo, 25 newest videos (2026-09-09 to 2026-10-16), prompt v1, Haiku 5.5

`check.py` over the round: 25 of 25 files valid JSON; 296 items in the first 20, of which 295 quote the transcript exactly
and start within 30 s of `t`. Strength: 42 fives and 143 fours (62% at 4 or 5).

## Scores on the 3 samples (Opus read each transcript in full)

| video | recall | precision | specificity | fidelity | calibration | usefulness | mean |
|---|---|---|---|---|---|---|---|
| 2026-09-21_F3YXg7AaKWE "Jev is incredible" (30 min) | 4 | 4 | 5 | 5 | 3 | 4 | 4.17 |
| 2026-09-09_q1D90-uGvBg "You're using AI agents wrong" (49 min) | 2 | 4 | 5 | 5 | 3 | 4 | 3.83 |
| 2026-10-12_vRS2leJLAI0 "I thought AI was gonna get cheaper?" (18 min) | 3 | 3 | 4 | 5 | 2 | 4 | 3.50 |
| **round mean** | | | | | | | **3.83** |

## The five worst misses

1. **q1D90 0:07:00-0:11:00, his prompt anatomy, missed entirely.** It should have produced about five techniques:
   - State the priority as a no-compromise line, then add "in my opinion" to invite pushback.
   - Say what you do not understand, so the agent explains exactly that.
   - Make the ask separate from the end goal.
   - Add "if you see a simple fix, stop and tell me" as an early exit.
   - Ask for "a confident path to a solution" when you do not want code written.

   This is the most reusable material in the round.
2. **q1D90 0:21:00 + 0:44:00, the habits behind 50 PRs a week, missed.**
   - When an answer is hard to read, ask for an explain-like-I'm-five version instead of tabbing away; "fight it with tokens".
   - Open a thread the moment you notice an issue.
   - Ask the agent to audit an assumption against its own history.
   - Every friction point that stops you merging is the next thing to build.
3. **F3YX 0:27:15, classifying his own agent history, skipped as "chat-history numbers".**
   - He ran 32,311 messages from 1,118 T3 Code threads through the classifier for about $0.37.
   - Nearly half the threads were bug fixing and PR work.
   - Moving the confidence bar from 80% to 90% cut "expanding scope" from 22% to 6.8% of threads.

   It is a technique, his own number, and directly usable on our fleet's history.
4. **vRS2 0:16:34, his own reversal, missed.**
   - In 2024 he made a video titled "AI isn't going to keep improving". He now says: "I was so wrong. I've never in my life had a take that was that bad."
   - A change of mind is the most valuable stance the graph can hold, and v1 has no place for it.
5. **vRS2 0:07:30, match the model to the task's token shape, missed.**
   - For input-heavy work (ingest 800k tokens and categorise), buy the cheapest input tokens.
   - For agentic dev, caching, reliability and token efficiency decide it.

   Also missed: his own spend, from $800-1,000 for all of 2025 to about $1,000 a day in 2026.

## Patterns (all 25 extracts)

- **Strength is inflated.**
  - 62% of items are rated 4 or 5. vRS2 has five 5s in 13 items, and two of them are the same idea.
  - The video's thesis is usually item 1 at strength 5, even when it is just the headline.
- **There are duplicates.** vRS2 items 1, 2 and 8 are one idea, "spend rises with usage, not price", said three times.
- **Long videos are under-extracted.** Items do not scale with length: 6k words gets 12-17 items, and 17k words gets 15-20.
- **"How he works" is missed.**
  - Prompts he types, habits, tools he built for himself, and his own numbers (spend, PRs, cost of a run).
  - The extractor pulls what the video is about, and drops what the speaker does.
- **Changes of mind have no slot.** "I used to think", "I was wrong" and "I've changed my mind" are not captured.
- **"Theo says" leaks into claims.** 38 of 296 claims name the speaker, and 25 claims run over 40 words.
- **`use` is padded.** Only 4 of 296 are null. Facts and stances get invented actions ("consider X for Y").

## Kept from v1 (working)

- Exact quotes and timestamps: fidelity 5 on every sample.
- Sponsor reads are skipped cleanly.
- Specific numbers and names.
- Valid JSON every time.
