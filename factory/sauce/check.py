#!/usr/bin/env python3
"""Check a round's extracts without a model: valid JSON, the schema, and whether each quote really is in the
transcript and starts near its timestamp. The judge reads this before reading anything else.

  check.py <round dir>      # expects videos/<id>/transcript.txt and out/<id>.json
"""
import json
import pathlib
import re
import sys

KINDS = {"principle", "technique", "stance", "prediction", "fact", "warning"}
DUR = {"timeless", "years", "months", "weeks"}


def norm(s):
    return re.sub(r"[^a-z0-9 ]+", "", re.sub(r"\s+", " ", s.lower())).strip()


def secs(t):
    p = [int(x) for x in (t or "0").split(":") if x.isdigit()]
    return sum(v * 60 ** i for i, v in enumerate(reversed(p)))


def transcript(path):
    """Joined text plus (char offset, seconds) marks, so a quote's position gives its time."""
    text, marks = "", []
    for line in open(path):
        m = re.match(r"\[(\d+:\d\d(?::\d\d)?)\]\s*(.*)", line)
        if m:
            marks.append((len(text), secs(m.group(1))))
            text += norm(m.group(2)) + " "
    return text, marks


def at(marks, pos):
    t = 0
    for off, s in marks:
        if off > pos:
            break
        t = s
    return t


def check(rnd):
    rnd = pathlib.Path(rnd)
    rows, total = [], {"files": 0, "bad_json": 0, "items": 0, "quote_found": 0, "t_within_30s": 0, "s5": 0, "s4": 0}
    for vid in sorted((rnd / "videos").iterdir()):
        out = rnd / "out" / f"{vid.name}.json"
        if not out.exists():
            rows.append((vid.name, "MISSING"))
            continue
        total["files"] += 1
        try:
            d = json.load(open(out))
        except Exception as e:
            total["bad_json"] += 1
            rows.append((vid.name, f"BAD JSON {e}"[:80]))
            continue
        text, marks = transcript(vid / "transcript.txt")
        items = d.get("sauce", [])
        found = near = schema = 0
        for it in items:
            schema += it.get("kind") not in KINDS or it.get("durability") not in DUR or not isinstance(it.get("strength"), int)
            q = norm(it.get("quote") or "")
            pos = text.find(q) if len(q) > 10 else -1
            if pos >= 0:
                found += 1
                near += abs(at(marks, pos) - secs(it.get("t"))) <= 30
            total["s5"] += it.get("strength") == 5
            total["s4"] += it.get("strength") == 4
        total["items"] += len(items)
        total["quote_found"] += found
        total["t_within_30s"] += near
        kinds = {}
        for it in items:
            kinds[it.get("kind")] = kinds.get(it.get("kind"), 0) + 1
        rows.append((vid.name, f"{len(items):>2} items  quotes {found}/{len(items)}  t±30s {near}  schema_err {schema}"
                     f"  stances {len(d.get('stances', []))}  {kinds}"))
    return rows, total


if __name__ == "__main__":
    rows, total = check(sys.argv[1])
    for r in rows:
        print(f"{r[0]:28} {r[1]}")
    print(json.dumps(total))
