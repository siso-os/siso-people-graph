#!/usr/bin/env python3
"""people-watch: track people, collect what they post, answer "what did X say about Y".

Runs where the data lives (the Mac mini). Stdlib only, plus a yt-dlp binary.

  people add felix-rieseberg --name "Felix Rieseberg" --x felixrieseberg --why "..."
  people list
  people sweep [slug] [--backfill N]       fetch only what is new
  people archive <slug> [--limit N]        a creator's whole YouTube back catalogue, newest first
  people said <slug|all> "topic" [--since 2026-10-01] [--limit 8]
  people digest [slug] [--since 2026-10-10]
  people reindex

Store ($PEOPLE_WATCH_HOME, default ~/SISO_Workspace/_data/people-watch):
  people.json                                 who is tracked and why
  raw/<slug>/youtube/<date>_<id>/meta.json, transcript.json, transcript.txt
  raw/<slug>/x/<YYYY-MM>.jsonl                one post per line
  state.json                                  ids already fetched, per person and source
  index.sqlite                                FTS5 over raw/ (rebuildable: `people reindex`)
"""
import argparse, datetime as dt, glob, json, os, re, shutil, sqlite3, subprocess, sys, tempfile, time
import urllib.parse, urllib.request

HOME = os.path.expanduser(os.environ.get("PEOPLE_WATCH_HOME", "~/SISO_Workspace/_data/people-watch"))
YTDLP = os.environ.get("YTDLP", "")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) people-watch/1"
FX = "https://api.fxtwitter.com/2/profile/{}/statuses"


def p(*a):
    return os.path.join(HOME, *a)


def load(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def save(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
    os.replace(tmp, path)


def log(msg):
    line = f"{dt.datetime.now().isoformat(timespec='seconds')} {msg}"
    print(line, flush=True)
    os.makedirs(p("logs"), exist_ok=True)
    with open(p("logs", "sweep.log"), "a") as f:
        f.write(line + "\n")


def ytdlp():
    if YTDLP:
        return YTDLP
    venv = p("app", "venv", "bin", "yt-dlp")
    return venv if os.path.exists(venv) else (shutil.which("yt-dlp") or "/opt/homebrew/bin/yt-dlp")


# ---------- people ----------

def cmd_add(a):
    people = load(p("people.json"), {})
    slug = a.slug.lower().strip()
    cur = people.get(slug, {"slug": slug, "added": dt.date.today().isoformat(), "feeds": {}})
    if a.name:
        cur["name"] = a.name
    if a.why:
        cur["why"] = a.why
    if a.x:
        cur["feeds"]["x"] = a.x.lstrip("@")
    if a.youtube:
        cur["feeds"]["youtube"] = normalise_youtube(a.youtube)
    for r in a.rss or []:
        cur["feeds"].setdefault("rss", [])
        if r not in cur["feeds"]["rss"]:
            cur["feeds"]["rss"].append(r)
    cur.setdefault("name", slug)
    people[slug] = cur
    save(p("people.json"), dict(sorted(people.items())))
    print(f"tracking {slug}: {json.dumps(cur['feeds'])}  why: {cur.get('why', '-')}")


def normalise_youtube(v):
    v = v.strip()
    if v.startswith("http"):
        return v.rstrip("/")
    if v.startswith("UC") and len(v) == 24:
        return f"https://www.youtube.com/channel/{v}"
    return f"https://www.youtube.com/@{v.lstrip('@')}"


def cmd_list(a):
    people = load(p("people.json"), {})
    state = load(p("state.json"), {})
    for slug, person in people.items():
        seen = {k: len(v) for k, v in state.get(slug, {}).items()}
        print(f"{slug:22} {person.get('name', ''):22} feeds={','.join(person['feeds'])} stored={seen}  why: {person.get('why', '-')}")


# ---------- collectors ----------

def http_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def sweep_x(slug, handle, seen, backfill_pages, skipped=None):
    """fxtwitter's public profile timeline: free, no login. Stops at the first id already stored."""
    new, cursor, pages = [], None, 0
    max_pages = backfill_pages if not seen else 5
    while pages < max_pages:
        url = FX.format(handle) + (f"?cursor={urllib.parse.quote(cursor)}" if cursor else "")
        d = http_json(url)
        if d.get("code") != 200:
            raise RuntimeError(f"fxtwitter {d.get('code')} {d.get('message')}")
        results = d.get("results") or []
        hit_seen = False
        for t in results:
            if t["id"] in seen:
                hit_seen = True
                continue
            new.append(t)
        pages += 1
        cursor = (d.get("cursor") or {}).get("bottom")
        if hit_seen or not results or not cursor:
            break
        time.sleep(1)
    by_month = {}
    for t in new:
        when = dt.datetime.fromtimestamp(t["created_timestamp"], dt.timezone.utc)
        row = {
            "id": t["id"], "url": t["url"], "date": when.isoformat(), "text": t.get("text", ""),
            "kind": "repost" if t.get("reposted_by") else ("reply" if t.get("replying_to") else "post"),
            "replying_to": (t.get("replying_to") or {}).get("screen_name") if isinstance(t.get("replying_to"), dict) else t.get("replying_to"),
            "quote_url": (t.get("quote") or {}).get("url"),
            "media": [m.get("url") for m in ((t.get("media") or {}).get("all") or [])],
            "likes": t.get("likes"), "reposts": t.get("reposts"), "replies": t.get("replies"), "views": t.get("views"),
            "fetched": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "via": "fxtwitter",
        }
        by_month.setdefault(when.strftime("%Y-%m"), []).append(row)
    for month, rows in by_month.items():
        path = p("raw", slug, "x", f"{month}.jsonl")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a") as f:
            for row in sorted(rows, key=lambda r: r["date"]):
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return [t["id"] for t in new]


class _Text(__import__("html.parser").parser.HTMLParser):
    """HTML to plain text, keeping paragraph breaks; drops script/style/nav."""
    SKIP = {"script", "style", "nav", "header", "footer", "svg", "noscript"}
    BLOCK = {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "pre", "blockquote", "tr", "section", "article"}

    def __init__(self):
        super().__init__()
        self.out, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
        elif tag in self.BLOCK:
            self.out.append("\n\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data)


def html_text(html):
    t = _Text()
    t.feed(html or "")
    text = re.sub(r"[ \t]+", " ", "".join(t.out))
    return re.sub(r"\n\s*\n+", "\n\n", text).strip()


def http_text(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def sweep_rss(slug, feeds, seen, backfill, skipped=None):
    """Blog / newsletter feeds (RSS or Atom). Full text from the feed, or from the page when the feed has a stub."""
    import email.utils
    import xml.etree.ElementTree as ET
    ns = {"a": "http://www.w3.org/2005/Atom", "c": "http://purl.org/rss/1.0/modules/content/"}
    done = []
    for feed in feeds if isinstance(feeds, list) else [feeds]:
        root = ET.fromstring(http_text(feed))
        items = root.findall(".//item") or root.findall(".//a:entry", ns)
        if not seen:
            items = items[:backfill]
        for it in items:
            link = it.findtext("link") or (it.find("a:link", ns).get("href") if it.find("a:link", ns) is not None else "")
            guid = it.findtext("guid") or it.findtext("a:id", namespaces=ns) or link
            if not link or guid in seen:
                continue
            title = (it.findtext("title") or it.findtext("a:title", namespaces=ns) or "").strip()
            raw_date = it.findtext("pubDate") or it.findtext("a:published", namespaces=ns) or it.findtext("a:updated", namespaces=ns) or ""
            try:
                when = email.utils.parsedate_to_datetime(raw_date) if "," in raw_date else dt.datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
                date = when.date().isoformat()
            except Exception:
                date = dt.date.today().isoformat()
            body = it.findtext("c:encoded", namespaces=ns) or it.findtext("a:content", namespaces=ns) or it.findtext("description") or ""
            text = html_text(body)
            if len(text) < 1500:
                try:
                    text = html_text(http_text(link)) or text
                except Exception as e:
                    log(f"  web {slug} {link}: page fetch failed ({e})")
            name = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60] or "post"
            folder = p("raw", slug, "web", f"{date}_{name}")
            save(os.path.join(folder, "meta.json"), {"id": guid, "url": link, "title": title, "date": date, "feed": feed,
                                                     "fetched": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "via": "rss"})
            with open(os.path.join(folder, "text.md"), "w") as f:
                f.write(f"# {title}\n\n{link}\n\n{text}\n")
            done.append(guid)
    return done


def run(cmd, timeout=600):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout).strip().splitlines()[-1] if (r.stderr or r.stdout).strip() else f"exit {r.returncode}")
    return r.stdout


def sweep_youtube(slug, channel, seen, backfill, skipped):
    """List the channel's newest uploads, then fetch captions + metadata for ids not stored yet. No audio."""
    out = run([ytdlp(), "--flat-playlist", "-J", "--playlist-end", "15", channel + "/videos"])
    ids = [e["id"] for e in json.loads(out).get("entries") or [] if e.get("id")]
    skip = set(skipped)
    if not seen and not skip:  # first sweep: back-fill the newest N, skip the rest of the page for good
        skipped.extend(ids[backfill:])
        ids = ids[:backfill]
    todo = [i for i in ids if i not in seen and i not in skip]
    done = []
    for vid in todo:
        try:
            if fetch_video(slug, vid):
                done.append(vid)  # without captions it is retried next sweep
        except Exception as e:  # one bad video must not stop the sweep
            log(f"  youtube {slug} {vid}: {e}")
        time.sleep(2)
    return done


def fetch_video(slug, vid):
    url = f"https://www.youtube.com/watch?v={vid}"
    # Metadata first (one cheap call), then captions. Caption URLs hit HTTP 429 from our home IP now and then
    # (15 Oct); android_vr's fail less, and youtube-transcript-api is the fallback.
    info = json.loads(run([ytdlp(), "-J", "--skip-download", url]))
    segments, source = [], None
    with tempfile.TemporaryDirectory() as tmp:
        try:
            run([ytdlp(), "--skip-download", "--write-subs", "--write-auto-subs", "--sub-langs", "en",
                 "--sub-format", "json3", "--extractor-args", "youtube:player_client=android_vr,default",
                 "-o", os.path.join(tmp, "%(id)s.%(ext)s"), url])
        except RuntimeError as e:
            log(f"  youtube {slug} {vid}: yt-dlp captions failed ({str(e)[:80]}); trying youtube-transcript-api")
        subs = glob.glob(os.path.join(tmp, f"{vid}.*.json3"))
        if subs:
            segments, source = parse_json3(subs[0]), os.path.basename(subs[0]).split(".")[-2]
    if not segments:
        segments = transcript_api(vid)
        source = "youtube-transcript-api" if segments else None
    day = info.get("upload_date") or "00000000"
    date = f"{day[:4]}-{day[4:6]}-{day[6:]}"
    folder = p("raw", slug, "youtube", f"{date}_{vid}")
    meta = {k: info.get(k) for k in ("id", "title", "channel", "channel_id", "uploader_id", "duration",
                                     "view_count", "like_count", "comment_count", "description", "tags",
                                     "chapters", "categories", "language")}
    meta.update({"url": url, "date": date, "captions": source,
                 "fetched": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "via": "yt-dlp"})
    save(os.path.join(folder, "meta.json"), meta)
    save(os.path.join(folder, "transcript.json"), segments)
    with open(os.path.join(folder, "transcript.txt"), "w") as f:
        for s in segments:
            f.write(f"[{fmt_ts(s['t'])}] {s['text']}\n")
    if not segments:
        log(f"  youtube {slug} {vid}: no captions yet (retried next sweep; ASR only if picked)")
    return bool(segments)


def transcript_api(vid):
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        got = YouTubeTranscriptApi().fetch(vid, languages=["en", "en-US", "en-GB"])
        return [{"t": round(s.start, 1), "text": s.text.replace("\n", " ").strip()} for s in got.snippets if s.text.strip()]
    except Exception as e:
        log(f"  youtube {vid}: youtube-transcript-api failed ({type(e).__name__})")
        return []


def parse_json3(path):
    data = load(path, {})
    segs = []
    for ev in data.get("events", []):
        text = "".join(s.get("utf8", "") for s in ev.get("segs") or []).replace("\n", " ").strip()
        if text:
            segs.append({"t": round(ev.get("tStartMs", 0) / 1000, 1), "text": text})
    # auto-captions repeat rolling lines; drop exact repeats of the previous line
    out = []
    for s in segs:
        if not out or s["text"] != out[-1]["text"]:
            out.append(s)
    return out


def fmt_ts(sec):
    sec = int(sec)
    return f"{sec // 3600}:{sec % 3600 // 60:02d}:{sec % 60:02d}"


def cmd_sweep(a):
    people = load(p("people.json"), {})
    state = load(p("state.json"), {})
    targets = [a.slug] if a.slug else list(people)
    total = 0
    for slug in targets:
        person = people[slug]
        st = state.setdefault(slug, {})
        for source, fn in (("x", sweep_x), ("youtube", sweep_youtube), ("rss", sweep_rss)):
            feed = person["feeds"].get(source)
            if not feed:
                continue
            seen = set(st.get(source, []))
            try:
                backfill = max(1, a.backfill // 5) if source == "x" else a.backfill
                skipped = st.setdefault(source + "_skipped", [])
                got = fn(slug, feed, seen, backfill, skipped)
            except Exception as e:
                log(f"{slug} {source}: FAILED {e}")
                continue
            st[source] = sorted(seen | set(got))
            save(p("state.json"), state)
            total += len(got)
            log(f"{slug} {source}: {len(got)} new")
    reindex()
    log(f"sweep done: {total} new items")


import threading
META_GATE = threading.Semaphore(2)
APIFY_ACTOR = "supreme_coder~youtube-transcript-scraper"  # $0.001 a transcript (16 Oct 2026); 10 Dwarkesh episodes in 130 s


def apify_tokens():
    """Tokens from .apify.env beside the app (one per line, KEY=value; not in git). Each free account has $5 a month."""
    path = p(".apify.env")
    if not os.path.exists(path):
        return []
    return [l.split("=", 1)[1].strip().strip("\"'") for l in open(path) if "=" in l and not l.startswith("#")]


def apify_batch(token, vids):
    body = json.dumps({"urls": [{"url": f"https://www.youtube.com/watch?v={v}"} for v in vids], "outputFormat": "json"}).encode()
    req = urllib.request.Request(f"https://api.apify.com/v2/acts/{APIFY_ACTOR}/run-sync-get-dataset-items?timeout=290",
                                 data=body, headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=300))


def archive_apify(slug, todo, repo, batch=25):
    """Transcripts from Apify (its IPs, so no 429s at home), one batch per token in parallel; metadata from yt-dlp -J,
    which our IP answers fine. Same files as fetch_video, with via=apify."""
    import html
    from concurrent.futures import ThreadPoolExecutor
    tokens = apify_tokens()
    if not tokens:
        log(f"{slug} archive: no Apify tokens in .apify.env"); return
    chunks = [todo[i:i + batch] for i in range(0, len(todo), batch)]
    done = []

    def one(job):
        n, vids = job
        items = None
        for attempt in range(4):  # a 400 now and then at start-up (16 Oct); retry on the next token
            try:
                items = apify_batch(tokens[(n + attempt) % len(tokens)], vids); break
            except Exception as e:
                log(f"  apify {slug} batch {n} try {attempt + 1}: {str(e)[:120]}"); time.sleep(20 * (attempt + 1))
        if items is None:
            return []
        got = []
        for it in items:
            vid = (it.get("videoDetails") or {}).get("videoId") or it.get("videoUrl", "").split("v=")[-1]
            segs = [{"t": round(s["start"], 2), "text": html.unescape(s["text"]).replace(" ", " ").replace("\n", " ").strip()}
                    for s in it.get("transcript") or [] if s.get("text")]
            if not vid or not segs:
                continue
            try:
                with META_GATE:  # at most 2 metadata calls from our IP at once
                    info = json.loads(run([ytdlp(), "-J", "--skip-download", f"https://www.youtube.com/watch?v={vid}"]))
            except Exception:
                info = {"id": vid, "title": (it.get("videoDetails") or {}).get("title")}
            day = info.get("upload_date") or "00000000"
            date = f"{day[:4]}-{day[4:6]}-{day[6:]}"
            folder = p("raw", slug, "youtube", f"{date}_{vid}")
            meta = {k: info.get(k) for k in ("id", "title", "channel", "channel_id", "uploader_id", "duration",
                                             "view_count", "like_count", "comment_count", "description", "tags",
                                             "chapters", "categories", "language")}
            meta.update({"url": f"https://www.youtube.com/watch?v={vid}", "date": date,
                         "captions": "auto" if it.get("isGenerated") else it.get("languageCode"),
                         "fetched": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "via": "apify"})
            save(os.path.join(folder, "meta.json"), meta)
            save(os.path.join(folder, "transcript.json"), segs)
            with open(os.path.join(folder, "transcript.txt"), "w") as f:
                for s in segs:
                    f.write(f"[{fmt_ts(s['t'])}] {s['text']}\n")
            got.append(vid)
        return got

    with ThreadPoolExecutor(max_workers=len(tokens)) as pool:
        for got in pool.map(one, enumerate(chunks)):
            done += got
            state = load(p("state.json"), {})
            st = state.setdefault(slug, {})
            st["youtube"] = sorted(set(st.get("youtube", [])) | set(got))
            save(p("state.json"), state)
            if got and os.path.isdir(os.path.join(repo, ".git")):
                subprocess.run(["git", "-C", repo, "add", "-A"], capture_output=True)
                subprocess.run(["git", "-C", repo, "commit", "-qm", f"{len(done)} videos archived via Apify"], capture_output=True)
                subprocess.run(["git", "-C", repo, "push", "-q"], capture_output=True)
            log(f"{slug} archive (apify): {len(done)} of {len(todo)} fetched")
    reindex()
    log(f"{slug} archive done (apify): {len(done)} new videos")


def cmd_archive(a):
    """A creator's whole back catalogue, newest first (Shaan, 16 Oct: "Theo's videos is absolute source").
    Same files as sweep; every 25 videos it commits and pushes raw/<slug>/youtube when that folder is a git repo
    (its own GitHub repo, so the transcripts live off this disk too). Stops for 10 minutes after 3 failures in a row
    (YouTube answers 429 to a home IP that asks too fast), and resumes where it left off when run again."""
    people = load(p("people.json"), {})
    channel = people[a.slug]["feeds"]["youtube"]
    ids = []
    for tab in a.tabs.split(","):
        try:
            ids += [e["id"] for e in json.loads(run([ytdlp(), "--flat-playlist", "-J", f"{channel}/{tab}"])).get("entries") or [] if e.get("id")]
        except Exception as e:
            log(f"{a.slug} archive: listing {tab} failed: {e}")
    stored = {os.path.basename(f).split("_", 1)[1] for f in glob.glob(p("raw", a.slug, "youtube", "*_*"))
              if os.path.exists(os.path.join(f, "transcript.txt")) and os.path.getsize(os.path.join(f, "transcript.txt"))}
    todo = [i for i in dict.fromkeys(ids) if i not in stored][: a.limit or None]
    repo = p("raw", a.slug, "youtube")
    log(f"{a.slug} archive: {len(ids)} listed, {len(stored)} stored, {len(todo)} to fetch")
    if a.via == "apify":
        return archive_apify(a.slug, todo, repo)
    done, fails = [], 0
    for n, vid in enumerate(todo, 1):
        try:
            ok = fetch_video(a.slug, vid)
            fails = 0
        except Exception as e:
            ok, fails = False, fails + 1
            log(f"  youtube {a.slug} {vid}: {e}")
        if ok:
            done.append(vid)
        if fails >= 3:
            log(f"{a.slug} archive: 3 failures in a row; waiting 10 minutes")
            time.sleep(600)
            fails = 0
        if done and (len(done) % 25 == 0 or n == len(todo)):
            state = load(p("state.json"), {})  # re-read: a sweep may have written it meanwhile
            st = state.setdefault(a.slug, {})
            st["youtube"] = sorted(set(st.get("youtube", [])) | set(done))
            save(p("state.json"), state)
            if os.path.isdir(os.path.join(repo, ".git")):
                subprocess.run(["git", "-C", repo, "add", "-A"], capture_output=True)
                subprocess.run(["git", "-C", repo, "commit", "-qm", f"{len(done)} videos archived ({vid})"], capture_output=True)
                subprocess.run(["git", "-C", repo, "push", "-q"], capture_output=True)
            log(f"{a.slug} archive: {len(done)} of {len(todo)} fetched")
        time.sleep(a.pause)
    reindex()
    log(f"{a.slug} archive done: {len(done)} new videos")


# ---------- index + distill ----------

def reindex():
    path = p("index.sqlite")
    tmp = path + ".tmp"
    if os.path.exists(tmp):
        os.remove(tmp)
    db = sqlite3.connect(tmp)
    db.execute("create virtual table chunk using fts5(text, person unindexed, source unindexed, date unindexed,"
               " url unindexed, title unindexed, tokenize='porter unicode61')")
    people = load(p("people.json"), {})
    rows = []
    for slug in people:
        for f in glob.glob(p("raw", slug, "x", "*.jsonl")):
            for line in open(f):
                t = json.loads(line)
                rows.append((t["text"], slug, "x", t["date"][:10], t["url"], t["kind"]))
        for meta_path in glob.glob(p("raw", slug, "web", "*", "meta.json")):
            meta = load(meta_path, {})
            body = open(os.path.join(os.path.dirname(meta_path), "text.md")).read()
            for chunk in paragraphs(body, 1200):
                rows.append((chunk, slug, "web", meta["date"], meta["url"], meta["title"]))
        for meta_path in glob.glob(p("raw", slug, "youtube", "*", "meta.json")):
            meta = load(meta_path, {})
            segs = load(os.path.join(os.path.dirname(meta_path), "transcript.json"), [])
            rows.append(((meta.get("title") or "") + "\n" + (meta.get("description") or "")[:1500],
                         slug, "youtube", meta["date"], meta["url"], meta.get("title")))
            for start, text in windows(segs, 60):
                rows.append((text, slug, "youtube", meta["date"], f"https://youtu.be/{meta['id']}?t={int(start)}",
                             f"{meta.get('title')} @ {fmt_ts(start)}"))
    db.executemany("insert into chunk values (?,?,?,?,?,?)", rows)
    db.commit()
    db.close()
    os.replace(tmp, path)
    return len(rows)


def paragraphs(text, size):
    buf = ""
    for para in text.split("\n\n"):
        if buf and len(buf) + len(para) > size:
            yield buf.strip()
            buf = ""
        buf += para + "\n\n"
    if buf.strip():
        yield buf.strip()


def windows(segs, seconds):
    buf, start = [], None
    for s in segs:
        if start is None:
            start = s["t"]
        buf.append(s["text"])
        if s["t"] - start >= seconds:
            yield start, " ".join(buf)
            buf, start = [], None
    if buf:
        yield start, " ".join(buf)


def fts_query(q):
    words = [w for w in re.findall(r"[\w']+", q.lower()) if len(w) > 2 and w not in STOP]
    return " OR ".join(f'"{w}"' for w in words) or '""'


STOP = set("the and for are but not you all any can had her was one our out has him his how its may new now old see two way who did get let say she too use what about with from that this they them then than when will your into more some just like over said".split())


def cmd_said(a):
    db = sqlite3.connect(p("index.sqlite"))
    sql = "select date, source, url, title, text, bm25(chunk) as score from chunk where chunk match ?"
    args = [fts_query(a.query)]
    if a.slug != "all":
        sql += " and person = ?"
        args.append(a.slug)
    if a.since:
        sql += " and date >= ?"
        args.append(a.since)
    sql += " order by score limit ?"
    args.append(a.limit)
    rows = db.execute(sql, args).fetchall()
    who = load(p("people.json"), {}).get(a.slug, {}).get("name", a.slug)
    print(f"# What {who} said about \"{a.query}\"{' since ' + a.since if a.since else ''}: {len(rows)} passages, best first\n")
    for date, source, url, title, text, score in rows:
        snippet = text if len(text) <= 700 else text[:700] + " ..."
        label = f" {title}" if source in ("youtube", "web") and title else ""
        print(f"- **{date} · {source}**{label}\n  > {snippet.strip()}\n  {url}\n")
    if not rows:
        print("Nothing stored matches. Silence is an answer: do not fill it in.")


def cmd_digest(a):
    since = a.since or (dt.date.today() - dt.timedelta(days=7)).isoformat()
    people = load(p("people.json"), {})
    for slug in ([a.slug] if a.slug else people):
        items = []
        for f in glob.glob(p("raw", slug, "x", "*.jsonl")):
            for line in open(f):
                t = json.loads(line)
                if t["date"][:10] >= since and t["kind"] != "repost":
                    items.append((t["date"][:10], "x", t["text"].replace("\n", " ")[:240], t["url"]))
        for meta_path in glob.glob(p("raw", slug, "youtube", "*", "meta.json")):
            m = load(meta_path, {})
            if m["date"] >= since:
                mins = (m.get("duration") or 0) // 60
                items.append((m["date"], "youtube", f"{m.get('title')} ({mins} min, {m.get('view_count') or 0:,} views)", m["url"]))
        for meta_path in glob.glob(p("raw", slug, "web", "*", "meta.json")):
            m = load(meta_path, {})
            if m["date"] >= since:
                items.append((m["date"], "web", m["title"], m["url"]))
        print(f"## {people[slug].get('name', slug)}: {len(items)} items since {since}")
        for date, src, text, url in sorted(items, reverse=True):
            print(f"- {date} · {src} · {text}  {url}")
        print()


def main():
    ap = argparse.ArgumentParser(prog="people")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("add"); s.add_argument("slug"); s.add_argument("--name"); s.add_argument("--x")
    s.add_argument("--youtube"); s.add_argument("--rss", action="append"); s.add_argument("--why"); s.set_defaults(fn=cmd_add)
    s = sub.add_parser("list"); s.set_defaults(fn=cmd_list)
    s = sub.add_parser("sweep"); s.add_argument("slug", nargs="?"); s.add_argument("--backfill", type=int, default=10)
    s.set_defaults(fn=cmd_sweep)
    s = sub.add_parser("archive"); s.add_argument("slug"); s.add_argument("--tabs", default="videos,streams")
    s.add_argument("--limit", type=int, default=0); s.add_argument("--pause", type=float, default=3); s.add_argument("--via", choices=["ytdlp", "apify"], default="ytdlp"); s.set_defaults(fn=cmd_archive)
    s = sub.add_parser("said"); s.add_argument("slug"); s.add_argument("query"); s.add_argument("--since")
    s.add_argument("--limit", type=int, default=8); s.set_defaults(fn=cmd_said)
    s = sub.add_parser("digest"); s.add_argument("slug", nargs="?"); s.add_argument("--since"); s.set_defaults(fn=cmd_digest)
    s = sub.add_parser("reindex"); s.set_defaults(fn=lambda a: print(f"{reindex()} chunks indexed"))
    a = ap.parse_args()
    os.makedirs(HOME, exist_ok=True)
    a.fn(a)


if __name__ == "__main__":
    main()
