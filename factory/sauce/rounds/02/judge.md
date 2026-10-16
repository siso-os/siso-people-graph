# Round 02 judge: Theo, next 25 videos (2026-07-28 to 2026-09-07), prompt v2, Haiku 5.5

The samples are held fixed as a benchmark: the same three as round 01, which the judge has read in full. This deviates
from RUBRIC.md (new samples each round) on purpose, so the score change measures the prompt and not the video. Rotate
in new samples once the prompt is stable, to catch overfitting.

## v2 on the benchmark samples (v1 in brackets)

| video | recall | precision | specificity | fidelity | calibration | usefulness | mean |
|---|---|---|---|---|---|---|---|
| F3YX "Jev is incredible" | 4 (4) | 4 (4) | 5 (5) | 4 (5) | 4 (3) | 4 (4) | 4.17 (4.17) |
| q1D90 "You're using AI agents wrong" | 3 (2) | 4 (4) | 5 (5) | 5 (5) | 4 (3) | 4 (4) | 4.17 (3.83) |
| vRS2 "AI gonna get cheaper?" | 4 (3) | 4 (3) | 4 (4) | 5 (5) | 4 (2) | 4 (4) | 4.00 (3.50) |
| **mean** | | | | | | | **4.11 (3.83), +0.28** |

## Fixed by v2
- **Changes of mind are caught.**
  - vRS2 records "AI had flatlined", with `was` filled in.
  - Across round 02, 18 stances carry a `was`.
- **Calibration is honest.** Items at 4 or 5 fell from 62% to 29% across the round.
- **Habits are caught.** q1D90 now has:
  - the thread opened the moment you see a bug;
  - the agent auditing its own history;
  - fixing every friction point;
  - verifying up front.
- **Own numbers are caught.** vRS2 has the spend jump, $1,000 a year to $1,000 a day. F3YX has the classifier run over 1,118 threads.
- **Claims name the speaker far less:** 1 in 272, down from 38 in 296.
- **Long videos get more items:** q1D90 went from 15 to 23 items.

## Still wrong
1. **q1D90 still misses the prompt anatomy (0:07-0:11):**
   - the no-compromise line;
   - "in my opinion" to invite pushback;
   - stating what you do not know;
   - the early-stop clause;
   - "confident path to a solution";
   - the closing question dump.

   It also misses the explain-like-I'm-five move. A general "how he works" sweep is not enough: prompts need an explicit must.
2. **F3YX adds a unit.** The transcript says "cost 37"; v2 wrote "$37". It is a fidelity error that a reader would trust.
3. **vRS2 misses "match the model to the task's token shape"** (input-heavy vs agentic), and "a few more points cost 3x".
4. **F3YX dropped the good v1 items** on cache-prefix invalidation and hallucination in dependency chains. That is the cost of
   fewer, stricter items: recall traded for precision.

## v3
- Prompts read out are a must, at one technique per deliberate phrase.
- The speaker's name never appears in a claim.
- Never add a unit the speaker did not say.
