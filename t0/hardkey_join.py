#!/usr/bin/env python3
"""Hard-key join of our people graph onto Wikidata (PLATFORM.md section 6 step 3).

Reads work.sqlite read-only plus Wikidata key tables (TSV from QLever, see
fetch_keys.sh), writes one judgement per (person_id, qid) as JSONL and prints
the falsifier: what share of our rows gain a QID.

Keys, strongest first:
  wikidata   the QID we already hold
  orcid      P496
  github     P2037 (login, case-insensitive)
  x          P2002 (handle, case-insensitive, no @)
  youtube    P2397 (channel id)
  gutenberg  P2034 ebook id -> P50 author, for book authors
  name_years English label + birth year + death year, unique in Wikidata (books only)
"""
import argparse, collections, json, re, sqlite3, sys, unicodedata
from pathlib import Path

QID = re.compile(r"/(Q\d+)>")


def qid(cell):
    m = QID.search(cell)
    return m.group(1) if m else None


def val(cell):
    cell = cell.strip()
    if cell.startswith('"'):
        cell = cell[1:cell.rindex('"')]
    return cell


def load_pairs(path, norm=lambda s: s):
    """value -> set of QIDs."""
    out = collections.defaultdict(set)
    with open(path, encoding="utf-8") as f:
        next(f)
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 2:
                continue
            q = qid(parts[0])
            if q:
                out[norm(val(parts[1]))].add(q)
    return out


def norm_name(s):
    s = re.sub(r"\(.*?\)", " ", s)
    if "," in s:  # "Kennedy, John F." -> "John F. Kennedy"
        last, _, first = s.partition(",")
        s = f"{first} {last}"
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return " ".join(re.sub(r"[^a-z ]", " ", s.lower()).split())


def first_last(n):
    t = n.split()
    return f"{t[0]} {t[-1]}" if len(t) >= 2 else n


def load_years(path):
    """(name, by, dy) -> QIDs, for full names and first+last."""
    full, short = collections.defaultdict(set), collections.defaultdict(set)
    with open(path, encoding="utf-8") as f:
        next(f)
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) < 4 or not p[2] or not p[3]:
                continue
            q, n = qid(p[0]), norm_name(val(p[1]))
            try:
                by, dy = int(val(p[2])), int(val(p[3]))
            except ValueError:
                continue
            full[(n, by, dy)].add(q)
            short[(first_last(n), by, dy)].add(q)
    return full, short


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--keys", required=True, help="dir with P*.tsv from fetch_keys.sh")
    ap.add_argument("--out", required=True, help="judgements JSONL")
    a = ap.parse_args()
    k = Path(a.keys)
    lower = str.lower
    keys = {
        "orcid": ("orcid", load_pairs(k / "P496.tsv")),
        "github": ("github_login", load_pairs(k / "P2037.tsv", lower)),
        "x": ("x_handle", load_pairs(k / "P2002.tsv", lower)),
        "youtube": ("youtube_channel_id", load_pairs(k / "P2397.tsv")),
    }
    gut = load_pairs(k / "P2034_P50.tsv")  # ebook id -> author QIDs
    full, short = load_years(k / "human_years.tsv")

    db = sqlite3.connect(f"file:{a.db}?mode=ro", uri=True)
    people = {r[0]: r[1:] for r in db.execute(
        "select person_id, name, kind, origin, birth_year, death_year from person where state != 'merged'")}
    ids = collections.defaultdict(list)
    for pid, plat, v in db.execute("select person_id, platform, value from external_ids"):
        ids[pid].append((plat, v))
    books = collections.defaultdict(set)
    for pid, ref in db.execute("select person_id, content_ref from person_content where domain='book'"):
        books[pid].add(ref)

    found = {}  # pid -> (qid, method, evidence, score)
    ambiguous = collections.Counter()

    def take(pid, qs, method, ev, score):
        if pid in found:
            return
        if len(qs) == 1:
            found[pid] = (next(iter(qs)), method, ev, score)
        elif qs:
            ambiguous[method] += 1

    for pid, pairs in ids.items():
        if pid not in people:
            continue
        for plat, v in pairs:
            if plat == "wikidata":
                take(pid, {v.rsplit("/", 1)[-1]}, "wikidata", v, 1.0)
        for method, (plat, table) in keys.items():
            for p, v in pairs:
                if p == plat:
                    n = v.lstrip("@").lower() if method in ("github", "x") else v
                    if method == "orcid":
                        n = v.rsplit("/", 1)[-1]
                    take(pid, table.get(n, set()), method, f"{plat}={v}", 0.99)
    for pid, refs in books.items():
        qs = set().union(*(gut.get(r, set()) for r in refs))
        take(pid, qs, "gutenberg", f"ebooks={sorted(refs)[:3]}", 0.98)
    for pid, (name, kind, origin, by, dy) in people.items():
        if pid in found or by is None or dy is None or kind != "human":
            continue
        n = norm_name(name)
        qs = full.get((n, by, dy)) or short.get((first_last(n), by, dy), set())
        take(pid, qs, "name_years", f"{n}|{by}|{dy}", 0.95)

    with open(a.out, "w") as f:
        for pid, (q, m, ev, s) in sorted(found.items()):
            f.write(json.dumps({"person_id": pid, "qid": q, "method": m, "evidence": ev,
                                "score": s, "decided_by": "hardkey_join_v1"}) + "\n")

    total = len(people)
    by_method = collections.Counter(m for _, m, _, _ in found.values())
    by_kind = collections.Counter(people[p][1] for p in found)
    kinds = collections.Counter(v[1] for v in people.values())
    qids = collections.Counter(q for q, *_ in found.values())
    print(f"rows {total:,}  gained QID {len(found):,} = {len(found)/total:.1%}")
    for kd, n in kinds.most_common():
        print(f"  {kd:13} {by_kind[kd]:>7,} of {n:>7,} = {by_kind[kd]/n:.1%}")
    print("by method", dict(by_method.most_common()))
    print("ambiguous skipped", dict(ambiguous))
    print("QIDs shared by >1 row (merge candidates):", sum(1 for c in qids.values() if c > 1))
    verdict = "PASS" if len(found) / total >= 0.30 else "FAIL"
    print(f"falsifier (>=30% of all rows): {verdict}")


if __name__ == "__main__":
    sys.exit(main())
