# Knowledge packs (14 Oct 2026)

## What a pack is
A **knowledge pack** is one person's or org's distilled **principles, methods, works and positions over time**. It
is short enough for an agent to load whole (~2-5k tokens), and every line points at the utterances or works it came
from. It is a map of the person, not a replacement for their words.

```
pack.json
{ entity: "Q317521", name: "Elon Musk", version: "2026-10-14.1", built_from: {utterances: N, sources: N, years: "2010-2025"},
  sections: {
    principles: [{text: "Start from physics, not analogy", utt_ids: [...], first_said: "2013-..", last_said: "..", verified: true}],
    methods:    [{text: "The 5-step algorithm: question requirements, delete, simplify, accelerate, automate", utt_ids: [...]}],
    works:      [{work_id, title, kind, date, why}],
    positions:  [{topic, stance_by_period: [{from, to, text, utt_ids}]}],
    gaps:       ["no source before 2010", "podcasts not transcribed"] } }
PACK.md  - the same, readable, with links
```

The rules:
1. A line without `utt_ids` does not ship.
2. A checker (Haiku) confirms each cited span supports its line. Lines that fail are dropped, and the drop rate is
   recorded.
3. Positions are dated ranges, never "believes".
4. Each pack is a new version on rebuild. The old one is kept, so a diff shows how a person's thinking moved.

## How it is built (SYSTEM.md §7)
1. **Cluster:** T3 utterances are grouped by topic (embeddings + our topic vocabularies).
2. **Propose:** per cluster, an Opus/Sonnet pass writes candidate principles and methods, each with the utterance IDs.
3. **Verify:** Haiku checkers do span-supports-line checks.
4. **Assemble:** works are added from `work` (top by rank), and gaps from coverage.
5. **Publish:** `pack.json` goes to the lake, PACK.md to the person page, and the skill to Agents Hub.

Cost: one Elon-scale pack is roughly 2M input tokens of clustered quotes. That is a few dollars on Haiku for
verification and tens of dollars on the propose pass. It is rebuilt only when new utterances pass 10%.

## What a pack feeds
| Consumer | Takes | Example |
|---|---|---|
| **Law Book** | `principles` lines, cited, merged across people into one rule with several sources | "Delete before you optimise": Musk 2021, plus others who said the same |
| **Agents Hub skills** | `methods` turned into a SKILL.md: when to use, the steps, the citations | `build-like-theo`: ship small, benchmark publicly, opinionated stack |
| **Advisors** | the pack as a table of contents: topic routing and "nearest topics" on refusal; answers still come only from utterances | Ask Elon about hiring: routes to the hiring cluster, then retrieves verbatim spans |
| **Person page** | the "In their words" summary block, each line linking to its quotes | top of the said section |

## First 3 packs
1. **Elon Musk: principles.** Shaan named him first, and the corpus already exists: 1,981 quotes, 92k posts and 84
   sources, none reviewed yet. The work is the join into `utterance`, a review pass, and then the pack. It is the
   template for every T3 person.
2. **Theo Browne (t3.gg): builder methods.** He is on the watchlist, and his output is on YouTube, GitHub and X, which
   tests the full T2 to T3 path on a living builder. Transcripts are pulled only for videos Shaan picks (source-map.json
   lists them by views and topic).
3. **Seneca: a public-domain thinker from our own book library.** Letters are first-person and dated by letter number.
   This proves the all-of-history path (book, then utterance, then pack) at $0 scrape cost, with no consent question.
   Alternative: Marcus Aurelius.

Orgs (Convex, Groq) get packs later. An org pack comes from docs, changelogs and founders' talks, so it waits until
person packs prove the method.
