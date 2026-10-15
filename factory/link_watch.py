#!/usr/bin/env python3
"""Join the people-watch tracker to the people graph.

  factory/link_watch.py --people people.json --db work.sqlite --judgements <data>/judgements --out <data>/watchlist/links.json

For each watched slug, find every graph row that is the same person (X handle, YouTube handle, GitHub login,
or the exact name of a human row) and the Wikidata QID any of those rows resolved to. A slug with rows but no
QID still links; a slug with no rows is reported so a stub can be made.
"""
import argparse, glob, json, re, sqlite3


def norm(v):
    return v.lower().lstrip("@").rstrip("/").rsplit("/", 1)[-1].lstrip("@")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--people", required=True)
    ap.add_argument("--db", required=True)
    ap.add_argument("--judgements", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    people = json.load(open(a.people))
    db = sqlite3.connect(f"file:{a.db}?mode=ro", uri=True)
    qid = {}
    for f in glob.glob(f"{a.judgements}/*.jsonl"):
        for line in open(f):
            j = json.loads(line)
            qid.setdefault(j["person_id"], j["qid"])

    out = {}
    for slug, p in people.items():
        feeds, keys = p.get("feeds", {}), set()
        if feeds.get("x"):
            keys |= {("x_handle", norm(feeds["x"]))}
        if feeds.get("youtube"):
            keys |= {("youtube_handle", norm(feeds["youtube"])), ("youtube_channel_id", norm(feeds["youtube"]))}
        if feeds.get("github"):
            keys |= {("github_login", norm(feeds["github"]))}
        rows = {}
        for plat, v in keys:
            for (pid,) in db.execute("select person_id from external_ids where platform=? and lower(ltrim(value,'@'))=?",
                                     (plat, v)):
                rows[pid] = f"{plat}={v}"
        for (pid,) in db.execute("select person_id from person where name=? and kind='human'", (p["name"],)):
            rows.setdefault(pid, "name")
        # a GitHub row whose x_handle matches is the same person, so pull those in too
        for pid in list(rows):
            for (x,) in db.execute("select value from external_ids where person_id=? and platform='x_handle'", (pid,)):
                for (pid2,) in db.execute("select person_id from external_ids where platform='x_handle' and lower(ltrim(value,'@'))=?",
                                          (norm(x),)):
                    rows.setdefault(pid2, f"x_handle={norm(x)} via {pid}")
        orgs = {r for r in rows if db.execute("select kind from person where person_id=?", (r,)).fetchone()[0] == "organisation"}
        for r in orgs:
            rows.pop(r)
        qids = sorted({qid[r] for r in rows if r in qid})
        out[slug] = {"name": p["name"], "graph_rows": rows, "qid": qids[0] if len(qids) == 1 else None,
                     "qid_conflict": qids if len(qids) > 1 else None, "orgs": sorted(orgs), "feeds": feeds}
        print(f"{slug:18} rows={len(rows)} qid={out[slug]['qid']} {sorted(rows)}")
    json.dump(out, open(a.out, "w"), indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
