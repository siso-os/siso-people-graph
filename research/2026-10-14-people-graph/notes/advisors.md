# Advisors slice: person-as-advisor products, research and law

Scope: public sources only, about 35 tool calls. Rows are in `rows/advisors.jsonl` (25 rows). `verified` is null on every row.

## Falsifier result

No product found that both cites every sentence and refuses on silence. The closest partial matches:

- Sensay: a per-answer "assumed information" flag (refusal half, product claim only).
- StoryFile: answers are verbatim recorded clips, so fidelity is total, but coverage is limited to pre-recorded questions and it redirects to the nearest question.
- Third-party "Essays by Paul Graham GPT": corpus-only with cites, but nothing shows it refuses.

No benchmark tests both properties together. Our bar would be the first.

## Product table

| Product | Grounding | Cites? | Refuses on silence? | Consent model |
|---|---|---|---|---|
| Delphi | Creator's books, podcasts, video, courses (RAG claimed) | Claimed by reviews only; not verified on site | Not verified | Creator self-serve |
| Dexa (Huberman) | Podcast transcripts, AI summary | Yes: timestamped episode links (TechCrunch 2024) | Not stated | Huberman Lab partnership |
| Character.AI | User-made roleplay, no corpus | No | No | Complaint-driven takedown; impersonation clause no longer published (ConductAtlas) |
| Meta celebrity personas (dead) | Persona prompt, archetypes | No | No | Licensed likeness, reported up to $5M each |
| Hello History | Unstated | No | No | Historical figures (no living subject) |
| Essays by PG GPT (3rd party) | paulgraham.com essays, RAG | Claimed yes | Not verified | Author not involved |
| Ask Naval (fan bots) | Tweets, interviews, Almanack | No | No | Unaffiliated |
| StoryFile | Pre-recorded answers, retrieved clips | Clip-level | Redirects to closest question | Subject records own answers |
| HereAfter AI | Subject's own recordings | Not found | Not found | Subject signs before death |
| Rai Ipazia | Show archive RAG (blog source) | Not stated | Not stated | Fictional avatar |
| ElevenLabs Iconic | Licensed voice model, no Q&A | No | Approval gate on scripts | Opt-in license, per-use approval (72h review) |
| Sensay | Documents, video, email | Hallucination flag, not citations | Flags assumed content | Proof-of-humanity |
| Personal.ai | Personal memory store | Not found | Not found | Owner controls data (company claim) |
| Amazon Ask This Book | Book text | Not confirmed | Not confirmed | No opt-out (Authors Guild dispute) |
| BBC Agatha Christie course | Christie's texts (paraphrase disputed) | No | No | Estate approved; criticised |
| Generative Agents (research) | 2-hour interview in prompt | No (not tested) | Not tested | Research participants consented |

## Numbers that matter

- Generative Agents (arXiv 2411.10109): 1,052 participants, 2-hour interviews; interview-only agents reach 83% of participants' own 2-week retest consistency on GSS, combined 86%, demographics-only 74%.
- ALCE (arXiv 2305.14627): on ELI5 the best models lack full citation support about 50% of the time.
- Dexa: 120+ podcasts (Feb 2024).
- StoryFile: about $250k per subject for one museum (press).
- Replika: EUR 5M Garante fine (May 2025), legal basis and age gate.

## Design rules to adopt

1. Retrieval only. Every answer is a span from the corpus, with a stable ID, date and URL per sentence. Model prose is not allowed.
2. Abstain on silence. If no passage clears a relevance threshold, return "not in the record" and list the nearest sources. Do not paraphrase from weights.
3. Show the evidence. The UI should display the quoted span next to each sentence, plus the publication date and link, with a click-through to the full source.
4. Metric. Use ALCE-style citation precision and recall per sentence, and a silence test set of questions the corpus cannot answer. Pass means the bot abstains.
5. Name what the bot is. Label every answer as "from [name]'s public record, not [name]." Use a visible AI and disclosure marker (EU Art. 50(1)).
6. Consent gate. Living people: opt-in, revocable, per-source. Dead people: only with a pre-death agreement (HereAfter pattern) or estate license with approval rights (ElevenLabs/BBC pattern), and no use of unlicensed likeness or voice.
7. Deletion. Removing a source removes its spans from the index and the answer cache within a stated window.

## Legal constraints for living people (and their estates)

- Tennessee ELVIS Act (in force since 1 Jul 2024): voice is a protected right; tool makers can be liable if the tool's primary purpose is unauthorised voice or likeness facsimile. Applies to any voice-based advisor sold into Tennessee.
- NO FAKES Act (S.1367 / H.R.2794, reintroduced 9 Apr 2025, still in committee as of last search): would create a federal voice and likeness right, platform takedown duties on knowledge, and post-mortem rights up to 70 years. Not law.
- Right of publicity (state law, e.g. California, New York): covers name, image, likeness and often post-mortem use via estates. Unclear whether it reaches writing style.
- EU AI Act Art. 50: chatbot disclosure (50(1)) and deepfake disclosure (50(4)) apply from 2 Aug 2026; machine-readable marking (50(2)) has grace to 2 Dec 2026 for existing systems. Fines up to EUR 15M or 3%. Read Reg. (EU) 2024/1689 itself; sources here are secondary.
- GDPR (Replika precedent): needs a valid legal basis for processing a person's data and age gating; consent wording alone is not enough.
- Terms of service of platforms (Character.AI): impersonation rules exist but were not re-verified; ConductAtlas notes the clause is no longer published.

## Gaps

- Could not open Dexa, Delphi, Hello History home pages (403, redirect, or no detail). Pricing and refusal behaviour for Delphi and Dexa are unverified.
- No primary source for Character.AI's current public-figure policy (URL returned 404).
- NPR deadbot article: fetch timed out; row uses the search snippet only.
- Stanford HAI page on Generative Agents gave no access controls for the interview data.
- No Sinai.ai, Coachvox, Tavus or Replika terms read.
- Next: read the ALCE metric section for exact citation precision and recall definitions; find TwinVoice primary paper; pull current NO FAKES status from congress.gov.
