# Advisor design: answers only in a person's own words (14 Oct 2026)

Evidence: `notes/advisors.md` (25 products, papers and laws). **No product we found both cites every sentence and
refuses when the record is silent.** Dexa cites timestamps but doesn't state a refusal rule. Sensay flags "assumed
information" but doesn't cite. StoryFile is verbatim but redirects instead of refusing. ALCE shows the best LLMs leave
about 50% of sentences without full citation support, so free generation can't meet our bar.

## 1. Grounding: retrieve, select, never write
- The corpus is `utterance` rows only (SYSTEM.md §2), with `attribution_conf >= 0.9`, deduped, and dated.
- Pipeline:
  1. Hybrid retrieval (FTS5 + vectors) gives the top 40 spans.
  2. A rerank scores relevance.
  3. The LLM **selects and orders** at most 6 spans and may add connective words only ("On X, he said:"), shown in a
     different style.
  4. It never adds a claim.
- An answer is a list of quote blocks. A "summary" view is allowed only if each summary sentence carries the span
  IDs it compresses, and a checker pass (an NLI or Haiku "does span support sentence?") drops any sentence that
  fails.

## 2. Citation: every sentence
Each block shows:
- the verbatim text
- the date said
- the medium (post, video, podcast, essay)
- the source title
- the URL, with a timestamp (`&t=`) for video
- a context toggle (`context_before/after`)

If a quote is a translation or an ASR transcript, that is labelled. Per-sentence citation precision and recall
(ALCE-style) go on an internal dashboard.

## 3. Refusal: silence is an answer
- Below the relevance threshold, reply "Not in [name]'s public record (N sources, YEAR-YEAR)", then list the 3
  nearest topics he did speak on.
- **Silence test set:** 50 questions per person the corpus can't answer. The advisor passes only if it abstains on
  at least 95% while answering at least 80% of an answerable set. This runs on every release.
- Time: answers are sorted by date, and contradicting spans are shown side by side ("2019: ... / 2023: ..."). It never
  says "he believes".

## 4. Consent, living people and the law
| Case | Rule |
|---|---|
| Living person, public record (posts, talks, essays) | Text-only advisor, verbatim quotes with links. This is the legal ground of quotation and commentary: no voice, no face, no first-person roleplay. Label: "From [name]'s public record. Not [name], not endorsed." |
| Living person who opts in | May add private sources, voice, first person; revocable per source (HereAfter / ElevenLabs Iconic pattern) |
| Living person who objects | Advisor off within a stated window; the person page stays (facts and works) |
| Dead, public domain (Socrates to Darwin) | Text advisor from public-domain works; first person allowed with a label |
| Dead, estate-controlled likeness | Text quotes only; no voice or likeness without an estate licence |

Laws to respect:
- EU AI Act Art. 50 (AI disclosure, from 2 Aug 2026)
- Tennessee ELVIS Act and state publicity rights (voice and likeness, so no voice for living people without a licence)
- NO FAKES Act (pending)
- GDPR legal basis (Replika fine)

Deletion: removing a source removes its spans from the index and the answer cache within 24 h.

## 5. Interface contract (for agents)
`ask(person, question, since?, until?) -> {answered: bool, blocks: [{utt_id, text, said_at, medium, url, span}],
coverage: {sources, years, words}, refusal?: {reason, nearest_topics[]}}`

Agents Hub ships it as a skill; the advisor page renders the same object.

## 6. What makes ours best in the world
1. Verbatim-only, with a measured citation rate.
2. A published silence test.
3. Date-aware contradictions.
4. Coverage stated on every answer.

No product we found does any two of these.
