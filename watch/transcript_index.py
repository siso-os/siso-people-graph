#!/usr/bin/env python3
"""Full-text index over archived transcripts: ask any question of every video, no model, no per-video tokens.

build:  transcript_index.py build <raw dir> <index.sqlite>    (raw dir holds <slug>/youtube/<date>_<id>/)
search: transcript_index.py search <index.sqlite> <words...>  (FTS5 syntax: "exact phrase", a OR b, mono*)
Each row is a ~60 s window, so a hit links straight to the moment in the video.
"""
import json, re, sqlite3, sys
from pathlib import Path

LINE = re.compile(r"^\[(\d+):(\d\d):(\d\d)\] (.*)$")


def windows(txt, span=60):
    start, buf = None, []
    for line in txt.splitlines():
        m = LINE.match(line)
        if not m:
            continue
        s = int(m[1]) * 3600 + int(m[2]) * 60 + int(m[3])
        if start is None:
            start = s
        buf.append(m[4])
        if s - start >= span:
            yield start, " ".join(buf)
            start, buf = None, []
    if buf:
        yield start, " ".join(buf)


def build(raw, db):
    con = sqlite3.connect(db)
    con.executescript("""
      DROP TABLE IF EXISTS chunk; DROP TABLE IF EXISTS video;
      CREATE TABLE video(id TEXT PRIMARY KEY, creator TEXT, date TEXT, title TEXT, description TEXT, duration INT);
      CREATE VIRTUAL TABLE chunk USING fts5(text, video_id UNINDEXED, t UNINDEXED, tokenize='porter');""")
    n = 0
    for meta in sorted(Path(raw).glob("*/youtube/*/meta.json")):
        d, creator = meta.parent, meta.parents[2].name
        tx = d / "transcript.txt"
        if not tx.exists():
            continue
        m = json.loads(meta.read_text())
        con.execute("INSERT OR REPLACE INTO video VALUES(?,?,?,?,?,?)",
                    (m["id"], creator, m.get("date"), m.get("title"), m.get("description"), m.get("duration")))
        con.executemany("INSERT INTO chunk(text, video_id, t) VALUES(?,?,?)",
                        [(text, m["id"], t) for t, text in windows(tx.read_text())])
        n += 1
    con.commit()
    print(n, "videos indexed")


def search(db, q, limit=15):
    con = sqlite3.connect(db)
    rows = con.execute("""SELECT v.creator, v.date, v.title, c.video_id, c.t, snippet(chunk, 0, '[', ']', '…', 18)
                          FROM chunk c JOIN video v ON v.id = c.video_id
                          WHERE chunk MATCH ? ORDER BY rank LIMIT ?""", (q, limit)).fetchall()
    for creator, date, title, vid, t, snip in rows:
        print(f"{date} {creator} | {title}\n  https://youtu.be/{vid}?t={t}  {snip}\n")


if __name__ == "__main__":
    cmd, *a = sys.argv[1:]
    build(*a) if cmd == "build" else search(a[0], " ".join(a[1:]))
