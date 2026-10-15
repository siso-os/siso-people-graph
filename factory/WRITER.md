# Output factory: the writer's brief (step 3 of 4)

Steps: 1 `ingest.py` (transcript.md + chunks) → 2 chunk readers (Haiku, one per entry, `notes/NN.md`) →
3 **writer** (this brief, one Opus per entry, `DOC.md` + `utterances.jsonl`) → 4 `verify.py` + `build_site.py` + deploy.

## Brief (paste with ENTRY filled in)
You write the library document for one video. Entry folder: ENTRY.

Read, in this order:
- `meta.json`
- every file in `notes/`, which together cover the whole video
- `factory/TEMPLATE.md` in the code repo (`~/SISO_Workspace/_data/worktrees/people-graph/t0-skeleton/factory/TEMPLATE.md`, or `people-graph/factory/` on main)
- `../../../watchlist/links.json`, for speakers' graph ids and QIDs

Open `transcript.md` only to settle a doubt or to copy a quote exactly.

Write `DOC.md` following the template exactly. Rules:
- **Complete, not top-N.** Section 3 covers every segment in the notes, in order. Sections 4-7 carry everything worth keeping. A 60-minute video usually makes 3,000-6,000 words.
- **Quotes are verbatim** from the captions, errors included, each followed by its timestamp link. `verify.py` fails the entry on any quote it can't find.
- **Section 5 is the payoff.** Each idea maps onto how SISO actually runs:
  - one person (Shaan) and a fleet of Claude Code agents
  - Opus "seats" own products; Haiku 5.5 sub-agents gather context and run checks
  - the orchestrator, Agent Zero, runs loops under standing authorization (merges, deploys, spend in budget, no green-lighting)
  - each lane has its own git worktree, on the laptop and on an always-on Mac mini
  - GitHub repos, with Cloudflare for hosting (Pages, Workers, D1)
  - token-ledger measures spend; routing.json picks models
  - the SISO console is at :8891, Agent Base / T3 Code is the front end
  - the people graph plus people-watch track people
  Name the seat, repo or loop it would land in, and be concrete.
- **Speakers:** label every quote. Use *(speaker unclear)* rather than guess.
- No preamble and no closers.

Also write `utterances.jsonl`, one line per quote in section 4:
`{"speaker": "<graph person_id or slug>", "qid": "<QID or null>", "t": <seconds>, "text": "<verbatim>", "source": "<video url>"}`
These lines credit each quote to the person who said it, guests included.

Return only: words written, quote count, and the 3 most important SISO actions, one line each.
