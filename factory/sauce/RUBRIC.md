# Sauce judge rubric (the Opus pass each round)

Per round: read the transcripts of 3 sampled videos yourself, then their extracts, and score each extract 1-5 on:

| | 5 means |
|---|---|
| recall | every item you would have pulled is there; nothing important missed |
| precision | no filler: no news recap, sponsor read or common knowledge passed off as sauce |
| specificity | names, numbers, settings and mechanisms, not "AI is getting better" |
| fidelity | quotes are exact and timestamps land within 10 s |
| calibration | strength and durability are honest; 5s are rare and earned |
| usefulness | `use` lines are things our fleet could actually do |

Then skim every other extract in the round (not the transcript) for patterns: vague claims, inflated strength, missing stances, duplicate items.

Write `rounds/NN/judge.md`: the scores (a table), the five worst misses with what the extract should have said, and the
pattern list. Then write `prompts/v(N+1).md`: the smallest change to the prompt that fixes the patterns, with a
`## Changed in vN+1` note at the bottom. Next round, re-run the new prompt on round N's 3 sampled videos and report the
score change beside the new round's scores. The prompt is done when two rounds in a row gain less than 0.2 on the mean;
from then on rounds run without a judge.
