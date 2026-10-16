#!/usr/bin/env python3
"""Read a YouTube channel's public page and return its facts, so a creator list is checked against YouTube itself
rather than a model's memory or a third-party tracker.

For each handle: channel id, title, subscribers, video count, last upload ("2 days ago"), description, and the X
account the channel links. One GET of youtube.com/@handle/videos each; no API key.

  yt_channel_facts.py handles.txt > facts.jsonl     # one handle (with or without @) or channel id per line, or JSONL with youtube_handle
"""
import concurrent.futures as cf
import json
import re
import sys
import urllib.request

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
X_SKIP = {"intent", "share", "home", "i", "search", "hashtag"}


def count(text):
    """'572K' -> 572000, '1.05M' -> 1050000."""
    m = re.match(r"([\d.,]+)\s*([KMB]?)", text or "")
    if not m:
        return None
    return int(float(m.group(1).replace(",", "")) * {"": 1, "K": 1e3, "M": 1e6, "B": 1e9}[m.group(2)])


def facts(handle):
    handle = handle.strip()
    handle = handle if re.fullmatch(r"UC[\w-]{22}", handle) else "@" + handle.lstrip("@")
    path = f"channel/{handle}" if handle.startswith("UC") else handle
    req = urllib.request.Request(f"https://www.youtube.com/{path}/videos",
                                 headers={"User-Agent": UA, "Accept-Language": "en-US", "Cookie": "CONSENT=YES+1"})
    try:
        s = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "replace")
    except Exception as e:  # 404 = no such handle
        return {"handle": handle, "ok": False, "error": str(e)[:80]}
    first = lambda pat: (re.search(pat, s) or [None, None])[1]
    xs = [x for x in re.findall(r'"https?://(?:www\.)?(?:twitter|x)\.com/([A-Za-z0-9_]{1,15})/?"', s) if x.lower() not in X_SKIP]
    title = first(r'<meta property="og:title" content="([^"]+)"')
    return {
        "handle": handle,
        "ok": bool(title),
        "channel_id": first(r'"externalId":"(UC[\w-]{22})"'),
        "title": title and title.replace("․", "."),
        "subscribers": count(first(r'"(\d[\d.,]*[KMB]?) subscribers"')),
        "videos": count(first(r'"(\d[\d.,]*[KMB]?) videos"')),
        "last_upload": first(r'"(\d+ (?:minutes?|hours?|days?|weeks?|months?|years?) ago)"'),
        "description": (first(r'<meta property="og:description" content="([^"]{0,300})') or "").strip(),
        "x_handle": xs[0] if xs else None,
    }


def handles(path):
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        if line.startswith("{"):
            h = json.loads(line).get("youtube_handle")
            if h:
                yield h
        else:
            yield line


if __name__ == "__main__":
    seen = list(dict.fromkeys(h if h.startswith("UC") else h.lstrip("@").lower() for h in handles(sys.argv[1])))
    with cf.ThreadPoolExecutor(6) as pool:
        for row in pool.map(facts, seen):
            print(json.dumps(row), flush=True)
