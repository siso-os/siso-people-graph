# Output factory: every interesting video or post becomes a full library entry

| Step | Tool | Writes |
|---|---|---|
| 1. Ingest | `ingest.py <slug> <video-id> --library <data>/library` (pulls from people-watch on the mini) | `meta.json`, `transcript.md` (full, with timestamp links), `chunks/`, `feedback.md` |
| 2. Read everything | one Haiku per entry, following `READER.md` | `notes/NN.md`: every point, quote, number and name, per 12-minute chunk |
| 3. Write | one Opus writer per entry, following `WRITER.md` and `TEMPLATE.md` | `DOC.md` (10 sections, complete, not top-N) and `utterances.jsonl` (each quote credited to its real speaker, guests included) |
| 4. Publish | `publish.sh` | quotes checked, data repo committed, site rebuilt and deployed |

**Where it goes**
- Data: the private repo `sisodias/siso-people-graph-data`, under `library/<person>/<date>_<id>/`.
- The tracker-to-graph join: `watchlist/links.json`, made by `link_watch.py`.
- Site: https://siso-library.pages.dev. It's password-gated until Cloudflare Access is enabled.
- Feedback: comments go in each entry's `feedback.md`, newest first. Edits to `DOC.md` are commits.
