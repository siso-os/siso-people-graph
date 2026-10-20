# GitHub reads (slice github-reads, 14 Oct 2026)

34 rows in `rows/github-reads.jsonl`, all read with `gh api repos/<o>/<r>` (stars, licence, pushed_at) on 14 Oct 2026. Verdicts: 10 use, 18 borrow-idea, 6 skip.

## Use table, mapped to SYSTEM.md parts

| SYSTEM.md part | Repo | Licence | Why |
|---|---|---|---|
| Identity (section 2 rules, judgement graph) | opensanctions/nomenklatura | MIT | Statement store and same/different judgements, the reversible-merge pattern |
| Identity (section 4 step 2) | moj-analytical-services/splink | MIT | EM probabilistic linkage on DuckDB |
| Dedup (section 4, level 2) | ekzhu/datasketch | MIT | MinHash-LSH for utterance dedup and blocking |
| Ingestion (section 4, YouTube row) | yt-dlp/yt-dlp | Unlicense | Channel inventory, metadata only |
| Ingestion (section 4, YouTube row) | jdepoix/youtube-transcript-api | MIT | Captions with timestamps for T3-picked videos |
| ASR (section 4) | ggml-org/whisper.cpp | MIT | Local batch ASR on Apple Silicon |
| ASR (section 4) | SYSTRAN/faster-whisper | MIT | Python batch ASR for long back-fills (pick one engine with whisper.cpp) |
| ASR and diarization (section 4) | k2-fsa/sherpa-onnx | Apache-2.0 | ASR, diarization and speaker ID in one offline stack |
| Diarization (section 4, speaker attribution) | pyannote/pyannote-audio | MIT code | Speaker turns; pretrained models are gated on Hugging Face with their own licences (not checked) |
| Diarization QA (section 4, 0.9 gate) | pyannote/pyannote-metrics | MIT | DER on a hand-labelled sample before attribution goes live |

Also worth a look (borrow-idea): WhisperX (word alignment), StanfordHCI/genagents (interview-to-agent for the quote-only advisor), dedupeio/dedupe (active-learning review loop), opentapioca (mention to QID linking), sigma.js (neighbourhood widget), embedding-atlas (internal QA of embeddings), yente (reconciliation API for review), OpenMOSS MOSS-Transcribe-Diarize (single-pass transcript plus speaker labels, to benchmark).

Not in the list: `karpathy/lexicap` does not exist on GitHub (404), and a repo search for "lexicap" finds only unrelated forks (e.g. Majdoddin/lexicaps, anotherjesse/lexicap). The Lex Fridman transcript work most likely to be meant is `lex-gpt` (rlancemartin, Whisper plus Pinecone RAG), which I did not verify directly.

`joonspk-research/genagents` redirects to `StanfordHCI/genagents` (MIT, last push 18 Nov 2024).

## Licence warnings

- **AGPL-3.0** (network copyleft, do not vendor): gramps-project/gramps-web, zinggAI/zingg.
- **GPL** (read for ideas only, no code copied into our repo): gramps-project/gramps (GPL-2.0), geneweb/geneweb (GPL-2.0), timhutton/twitter-archive-parser (GPL-3.0), WDscholia/scholia (GPL-3.0), fisharebest/webtrees (GPL-3.0), dahlia/wikidata (GPL-3.0).
- **No licence declared** (cannot be used): Quantatirsk/AsrServe. The data-matching-software list (J535D165) also declares none, but it is a list, not code.
- **Model licences are separate from code licences.** pyannote pipelines are gated on Hugging Face and need a token; sherpa-onnx and 3D-Speaker models each carry their own terms. Check each model's licence before use.
- **Stale:** twitter-archive-parser (Nov 2022), wptools (Aug 2023), Fujisaki (May 2023), dariusk/twitter-archiver (Nov 2023), genagents (Nov 2024), dedupe (Jul 2025), 3D-Speaker (Dec 2025).

## Still missing

- Model-level licence checks for pyannote, sherpa-onnx, and MOSS-Transcribe-Diarize weights (code licences only so far).
- A benchmark on our own labelled clip (sherpa-onnx vs pyannote vs MOSS-Transcribe-Diarize vs whisper-diarization).
- Wikidata bulk filtering tools (only the libraries in the shortlist were checked; QLever and the dump pipeline are covered in other slices).
- Verification of lex-gpt's licence and whether it is maintained.
