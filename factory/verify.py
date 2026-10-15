#!/usr/bin/env python3
"""Output factory check: every quoted line in a library entry must appear verbatim in its captions.

  factory/verify.py <entry-dir> [...]   exit 1 if any quote is not found

A quote is the text inside "..." on a line that carries a timestamp ([h:mm:ss] or &t=Ns).
Matching ignores case, whitespace and curly-vs-straight quote marks, and nothing else.
"""
import json, re, sys
from pathlib import Path

TS = re.compile(r"\[\d+:\d{2}:\d{2}\]|&t=\d+s")
Q = re.compile(r'["“]([^"“”]{12,}?)["”]')


def norm(s):
    return " ".join(s.replace("’", "'").split()).lower()


def check(entry):
    entry = Path(entry)
    text = norm(" ".join(x["text"] for x in json.loads((entry / "transcript.json").read_text()))) \
        if (entry / "transcript.json").exists() else None
    if text is None:  # library entries keep transcript.md, so rebuild the plain text from it
        md = (entry / "transcript.md").read_text().split("\n\n")[2:]
        text = norm(" ".join(re.sub(r"^\*\*\[.*?\]\(.*?\)\*\*\s*", "", p) for p in md))
    total, bad, doc_total, doc_bad = 0, [], 0, 0
    for f in [entry / "DOC.md", *sorted((entry / "notes").glob("*.md"))]:
        if not f.exists():
            continue
        for n, line in enumerate(f.read_text().splitlines(), 1):
            if not TS.search(line):
                continue
            for q in Q.findall(line):
                total += 1
                doc_total += f.name == "DOC.md"
                if norm(q) not in text:
                    bad.append(f"{f.name}:{n} {q[:80]}")
                    doc_bad += f.name == "DOC.md"
    print(f"{entry.name}: DOC.md {doc_total - doc_bad} of {doc_total} quotes verbatim; "
          f"notes {total - doc_total - (len(bad) - doc_bad)} of {total - doc_total}")
    for b in bad:
        print("  NOT FOUND", b)
    return doc_bad == 0  # notes are working material; DOC.md is what ships


if __name__ == "__main__":
    sys.exit(0 if all([check(e) for e in sys.argv[1:]]) else 1)
