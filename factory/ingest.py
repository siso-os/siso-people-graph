#!/usr/bin/env python3
"""Output factory, step 1: put one people-watch video into the library.

  factory/ingest.py <person-slug> <video-id> --library <data-repo>/library [--src <dir>]

Writes library/<slug>/<date>_<id>/:
  meta.json        copied from people-watch
  transcript.md    the full captions as readable paragraphs (one per ~60 s), each with a timestamp link
  chunks/NN.txt    ~12-minute slices for the chunk readers (the map step)
  feedback.md      an empty feedback log, if there isn't one already
--src defaults to fetching the folder from the Mac mini's people-watch store over ssh.
"""
import argparse, json, shutil, subprocess, sys, tempfile
from pathlib import Path

STORE = "SISO_Workspace/_data/people-watch/raw"
CHUNK_S, PARA_S = 720, 60


def hms(t):
    t = int(t)
    return f"{t // 3600}:{t % 3600 // 60:02d}:{t % 60:02d}"


def fetch(slug, vid):
    tmp = Path(tempfile.mkdtemp(prefix="factory-"))
    ls = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "RemoteCommand=none", "-T", "mac-mini",
                         f"ls -d {STORE}/{slug}/youtube/*_{vid}"], capture_output=True, text=True, check=True)
    remote = ls.stdout.split()[0]
    subprocess.run(["scp", "-q", "-o", "BatchMode=yes", "-o", "RemoteCommand=none", "-r",
                    f"mac-mini:{remote}", str(tmp)], check=True)
    return tmp / Path(remote).name


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("video_id")
    ap.add_argument("--library", required=True)
    ap.add_argument("--src")
    a = ap.parse_args()
    src = Path(a.src) if a.src else fetch(a.slug, a.video_id)
    meta = json.loads((src / "meta.json").read_text())
    lines = json.loads((src / "transcript.json").read_text())
    out = Path(a.library) / a.slug / src.name
    (out / "chunks").mkdir(parents=True, exist_ok=True)
    shutil.copy(src / "meta.json", out / "meta.json")
    url = f"https://www.youtube.com/watch?v={a.video_id}"

    paras, cur, start = [], [], 0.0
    for ln in lines:
        if cur and ln["t"] - start >= PARA_S:
            paras.append((start, " ".join(cur)))
            cur = []
        if not cur:
            start = ln["t"]
        cur.append(ln["text"].strip())
    if cur:
        paras.append((start, " ".join(cur)))

    words = sum(len(p.split()) for _, p in paras)
    head = (f"# Transcript: {meta['title']}\n\n{url} · {meta.get('channel')} · {meta.get('date')} · "
            f"{hms(meta.get('duration') or 0)} · {words:,} words · auto-captions (names may be mis-heard)\n\n")
    body = "\n\n".join(f"**[{hms(t)}]({url}&t={int(t)}s)** {p}" for t, p in paras)
    (out / "transcript.md").write_text(head + body + "\n")

    for old in (out / "chunks").glob("*.txt"):
        old.unlink()
    n = 0
    for i in range(0, int(lines[-1]["t"]) + 1, CHUNK_S):
        part = [ln for ln in lines if i <= ln["t"] < i + CHUNK_S]
        if part:
            n += 1
            (out / "chunks" / f"{n:02d}.txt").write_text(
                "\n".join(f"[{hms(ln['t'])}] {ln['text'].strip()}" for ln in part) + "\n")
    fb = out / "feedback.md"
    if not fb.exists():
        fb.write_text(f"# Feedback: {meta['title']}\n\nNewest first. One entry per comment: date, who, what, and what changed because of it.\n")
    print(f"{out}  {len(paras)} paragraphs, {words:,} words, {n} chunks")


if __name__ == "__main__":
    sys.exit(main())
