#!/usr/bin/env python3
"""Load a ranked list of YouTube creators into the people graph.

The graph held 35 YouTube channels against 245k GitHub accounts and 45k X handles. Creators are where the people who
make things explain them, and most of the ones worth following also ship code, so the first job is stitching: a
creator whose X handle or YouTube id is already on a person keeps that person and gains the channel, rather than
becoming a duplicate. Only the rest get a new 'yt:<handle>' row.

Each input line (JSONL) is one channel already checked against YouTube (yt_channel_facts.py):
  {"rank", "tier", "score", "handle": "@t3dotgg", "channel_id", "title", "name", "kind" (human|organisation), "show" (a podcast), "subscribers",
   "last_upload", "x_handle", "x_source", "slice", "why"}

Writes, all tagged source=SOURCE so the whole load is one DELETE to undo:
  person          new rows only (state 'linked', origin 'youtube'); an existing person keeps its own fields
  external_ids    youtube_handle, youtube_channel_id, x_handle
  person_content  domain 'youtube_channel', role 'owner' or 'host', meta: subscribers, last upload, rank, tier, slice

The long tail (--atlas): the June 2026 AI source atlas, a YouTube keyword sweep that found ~30k channels (name,
channel url, hits, total views, matching keywords). Unchecked, so each is state 'tracked', kind 'unknown' (a channel
may be a person or a company), id 'yt:<channel id>', its keywords in the edge's meta; a channel already in the graph
only gains the edge. Tagged source=ATLAS_SOURCE.

Facts (--facts): yt_channel_facts.py output for channels already in the graph. Each live channel gains the X account
its page links and its live subscribers / last upload on the edge's meta. When that X handle already belongs to another
person, nothing is merged: an identity_claim (shared_external_id, proposed) records the pair for review.

Usage:
  load_youtube_creators.py --graph people_v2.sqlite --facts atlas-facts.jsonl [--apply]
  load_youtube_creators.py --graph people_v2.sqlite --creators ranked.jsonl [--apply]
  load_youtube_creators.py --graph people_v2.sqlite --atlas creator_candidates.json [more.json] [--apply]
"""
import argparse
import json
import math
import re
import sqlite3
import time

SOURCE = "yt_creators_2026_10_16"
ATLAS_SOURCE = "yt_atlas_2026_06"


def slug(handle):
    return re.sub(r"[^a-z0-9_]+", "_", handle.lstrip("@").lower()).strip("_")


def find(db, c):
    """The person this channel already belongs to, and by which key; None when it is new."""
    keys = [("youtube_channel_id", c.get("channel_id")), ("youtube_handle", c["handle"]), ("x_handle", c.get("x_handle"))]
    for platform, value in keys:
        if not value:
            continue
        rows = db.execute(
            "SELECT DISTINCT e.person_id FROM external_ids e JOIN person p USING (person_id)"
            " WHERE e.platform = ? AND lower(ltrim(e.value, '@')) = lower(ltrim(?, '@')) AND p.state != 'merged'",
            (platform, value)).fetchall()
        if len(rows) == 1:
            return rows[0][0], platform
    pid = f"yt:{slug(c['handle'])}"
    if db.execute("SELECT 1 FROM person WHERE person_id = ?", (pid,)).fetchone():
        return pid, "person_id"
    return None, None


def load(graph, creators, apply):
    db = sqlite3.connect(graph)
    db.execute("PRAGMA foreign_keys = ON")
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    stats = {"matched": {}, "new": 0, "x_handles": 0}
    out = []
    for line in open(creators):
        c = json.loads(line)
        pid, via = find(db, c)
        if pid:
            stats["matched"][via] = stats["matched"].get(via, 0) + 1
        else:
            pid = f"yt:{slug(c['handle'])}"
            stats["new"] += 1
            db.execute(
                "INSERT INTO person (person_id, name, kind, state, primary_tier, rank_score, origin, built_at)"
                " VALUES (?, ?, ?, 'linked', ?, ?, 'youtube', ?)",
                (pid, c.get("name") or c["title"], c.get("kind", "human"), c.get("tier"), c.get("score"), now))
        ids = [("youtube_handle", c["handle"]), ("youtube_channel_id", c.get("channel_id")), ("x_handle", c.get("x_handle"))]
        for platform, value in ids:
            if value:
                db.execute("INSERT OR IGNORE INTO external_ids (person_id, platform, value, confidence, source)"
                           " VALUES (?, ?, ?, ?, ?)",
                           (pid, platform, value, 1.0 if platform != "x_handle" or c.get("x_source") == "youtube" else 0.9,
                            SOURCE))
        stats["x_handles"] += bool(c.get("x_handle"))
        meta = {k: c.get(k) for k in ("subscribers", "videos", "last_upload", "rank", "tier", "slice", "why", "x_source")}
        db.execute(
            "INSERT OR REPLACE INTO person_content (person_id, domain, content_ref, role, score, title, source, observed_at, meta_json)"
            " VALUES (?, 'youtube_channel', ?, ?, ?, ?, ?, ?, ?)",
            (pid, c.get("channel_id") or c["handle"], "host" if c.get("show") else "owner", c.get("score"),
             c["title"], SOURCE, now, json.dumps(meta)))
        out.append((c["rank"], c["handle"], pid, via or "new"))
    if apply:
        db.commit()
    else:
        db.rollback()
    return stats, out


def load_atlas(graph, files, apply):
    """Union the atlas files by channel id (the most hits wins), then add each channel once."""
    best = {}
    for f in files:
        for c in json.load(open(f)):
            m = re.search(r"/channel/(UC[\w-]{22})", c.get("url") or "")
            if m and c.get("hits", 0) >= best.get(m.group(1), {}).get("hits", 0):
                best[m.group(1)] = c
    db = sqlite3.connect(graph)
    db.execute("PRAGMA foreign_keys = ON")
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    known = dict(db.execute("SELECT value, person_id FROM external_ids WHERE platform = 'youtube_channel_id'").fetchall())
    new = had = 0
    for cid, c in best.items():
        pid = known.get(cid)
        if pid:
            had += 1
        else:
            pid = f"yt:{cid}"
            new += db.execute(
                "INSERT OR IGNORE INTO person (person_id, name, kind, state, rank_score, origin, built_at)"
                " VALUES (?, ?, 'unknown', 'tracked', ?, 'youtube', ?)",
                (pid, c["channel"], round(math.log10(1 + (c.get("total_views") or 0)), 2), now)).rowcount
            db.execute("INSERT OR IGNORE INTO external_ids (person_id, platform, value, confidence, source)"
                       " VALUES (?, 'youtube_channel_id', ?, 1.0, ?)", (pid, cid, ATLAS_SOURCE))
        meta = {"hits": c.get("hits"), "total_views": c.get("total_views"), "keywords": (c.get("keywords") or [])[:25]}
        db.execute(
            "INSERT OR IGNORE INTO person_content (person_id, domain, content_ref, role, score, title, source, observed_at, meta_json)"
            " VALUES (?, 'youtube_channel', ?, 'owner', ?, ?, ?, '2026-06-19', ?)",
            (pid, cid, c.get("hits"), c["channel"], ATLAS_SOURCE, json.dumps(meta)))
    if apply:
        db.commit()
    else:
        db.rollback()
    return {"channels": len(best), "new_people": new, "already_in_graph": had}


def load_facts(graph, facts, apply):
    db = sqlite3.connect(graph)
    db.execute("PRAGMA foreign_keys = ON")
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    owner = dict(db.execute("SELECT value, person_id FROM external_ids WHERE platform = 'youtube_channel_id'").fetchall())
    stats = {"live": 0, "x_handles": 0, "claims": 0, "not_in_graph": 0}
    for line in open(facts):
        f = json.loads(line)
        pid = owner.get(f.get("channel_id") or "")
        if not f.get("ok") or not pid:
            stats["not_in_graph"] += bool(f.get("ok"))
            continue
        stats["live"] += 1
        row = db.execute("SELECT rowid, meta_json FROM person_content WHERE person_id = ? AND domain = 'youtube_channel'"
                         " AND content_ref = ?", (pid, f["channel_id"])).fetchone()
        if row:
            meta = {**json.loads(row[1]), **{k: f.get(k) for k in ("subscribers", "videos", "last_upload")}, "facts_read": now[:10]}
            db.execute("UPDATE person_content SET meta_json = ? WHERE rowid = ?", (json.dumps(meta), row[0]))
        x = f.get("x_handle")
        if not x:
            continue
        stats["x_handles"] += db.execute("INSERT OR IGNORE INTO external_ids (person_id, platform, value, confidence, source)"
                                         " VALUES (?, 'x_handle', ?, 1.0, ?)", (pid, x, SOURCE)).rowcount
        for (other,) in db.execute("SELECT DISTINCT person_id FROM external_ids WHERE platform = 'x_handle'"
                                   " AND lower(ltrim(value, '@')) = lower(?) AND person_id != ?", (x, pid)).fetchall():
            a, b = sorted((pid, other))
            if not db.execute("SELECT 1 FROM identity_claim WHERE person_a = ? AND person_b = ?", (a, b)).fetchone():
                db.execute("INSERT INTO identity_claim (person_a, person_b, method, confidence, evidence, created_at)"
                           " VALUES (?, ?, 'shared_external_id', 0.9, ?, ?)",
                           (a, b, f"x_handle {x} linked from YouTube channel {f['channel_id']} and held by {other}", now))
                stats["claims"] += 1
    if apply:
        db.commit()
    else:
        db.rollback()
    return stats


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph", required=True)
    ap.add_argument("--creators")
    ap.add_argument("--atlas", nargs="+")
    ap.add_argument("--facts")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    if a.facts:
        print(json.dumps(load_facts(a.graph, a.facts, a.apply)), "applied" if a.apply else "dry run (add --apply)")
        raise SystemExit
    if a.atlas:
        print(json.dumps(load_atlas(a.graph, a.atlas, a.apply)), "applied" if a.apply else "dry run (add --apply)")
        raise SystemExit
    stats, out = load(a.graph, a.creators, a.apply)
    for rank, handle, pid, via in out:
        print(f"{rank:>4} {handle:28} {pid:32} {via}")
    print(json.dumps(stats), "applied" if a.apply else "dry run (add --apply)")
