#!/usr/bin/env python3
"""Render the library (data repo) into a static site for Cloudflare Pages.

  uv run --with markdown factory/build_site.py <data-repo> <out-dir>

Pages: / (people), /<slug>/ (person: feeds, graph rows, QID, entries), /<slug>/<entry>/ (DOC),
and transcript/ notes/ feedback/ under each entry. functions/_middleware.js gates the whole site
behind a password until Cloudflare Access is enabled.
"""
import html, json, re, shutil, sys
from pathlib import Path
import markdown

CSS = """body{font:15px/1.6 -apple-system,system-ui,sans-serif;max-width:900px;margin:24px auto;padding:0 18px;color:#1d1d1f;background:#fafafa}
a{color:#0a58ca}h1{font-size:24px}h2{font-size:18px;border-bottom:1px solid #ddd;padding-bottom:4px;margin-top:30px}h3{font-size:15px}
table{border-collapse:collapse;width:100%;font-size:14px}td,th{border:1px solid #ddd;padding:5px 8px;vertical-align:top;text-align:left}
th{background:#f0f0f0}blockquote{border-left:3px solid #0a7cff;margin:8px 0;padding-left:10px;color:#444}
nav{font-size:13px;margin-bottom:14px}nav a{margin-right:12px}code{background:#eee;padding:0 4px;border-radius:4px}
.card{background:#fff;border:1px solid #e3e3e3;border-radius:10px;padding:12px 14px;margin:10px 0}small{color:#777}"""

MIDDLEWARE = r"""// One sign-in that lasts: the login form sets a year-long HttpOnly cookie. Agent Base's /people proxy sends Basic auth.
const COOKIE = "siso_lib";
async function token(pw) {
  const d = await crypto.subtle.digest("SHA-256", new TextEncoder().encode("siso-library-v1:" + pw));
  return [...new Uint8Array(d)].map((b) => b.toString(16).padStart(2, "0")).join("");
}
const safe = (n) => (typeof n === "string" && n.startsWith("/") && !n.startsWith("//") ? n : "/");
function login(next, error) {
  const esc = (v) => v.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
  return new Response(`<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>SISO library</title>
<body style="font:15px system-ui;background:#fafafa;display:grid;place-items:center;height:90vh"><form method="post" action="/login"
style="background:#fff;border:1px solid #ddd;border-radius:12px;padding:24px;width:280px"><h2 style="margin:0 0 12px">SISO library</h2>
<input type="hidden" name="next" value="${esc(next)}"><input name="username" value="siso" autocomplete="username" style="display:none">
<input type="password" name="password" autocomplete="current-password" placeholder="Password" autofocus style="width:100%;padding:8px;box-sizing:border-box">
<button style="margin-top:12px;width:100%;padding:8px">Sign in (stays signed in for a year)</button><p style="color:#b3261e">${esc(error)}</p></form></body>`,
    { status: 401, headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" } });
}
export async function onRequest({ request, env, next }) {
  const pw = env.LIBRARY_PASSWORD;
  if (!pw) return new Response("not configured", { status: 503 });
  const url = new URL(request.url), t = await token(pw);
  const cookie = (request.headers.get("Cookie") || "").split(/;\s*/).find((c) => c.startsWith(COOKIE + "="))?.slice(COOKIE.length + 1);
  if (cookie === t || request.headers.get("Authorization") === "Basic " + btoa("siso:" + pw)) return next();
  if (url.pathname === "/login" && request.method === "POST") {
    const f = await request.formData();
    if (f.get("password") === pw) return new Response(null, { status: 303, headers: { Location: safe(f.get("next")),
      "Set-Cookie": `${COOKIE}=${t}; Max-Age=31536000; Path=/; HttpOnly; Secure; SameSite=Lax` } });
    return login(safe(f.get("next")), "Wrong password");
  }
  return login(url.pathname === "/login" ? "/" : url.pathname + url.search, "");
}
"""


GRAPH_PAGE = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>People graph</title>
<style>body{margin:0;font:13px system-ui;background:#0f1115;color:#ddd}#top{position:fixed;top:10px;left:14px;z-index:2}#top a{color:#8ab4ff;margin-right:12px}
.k{display:inline-block;width:10px;height:10px;border-radius:50%;margin:0 4px 0 10px}svg{width:100vw;height:100vh}text{fill:#ccc;font-size:11px;pointer-events:none}</style></head>
<body><div id="top"><a href="/">← Library</a><b>People graph</b><span id="legend"></span></div><svg></svg>
<script src="../d3.min.js"></script><script>
const C={person:"#5eead4",speaker:"#fbbf24",video:"#f87171",account:"#94a3b8",wikidata:"#a78bfa"};
document.getElementById("legend").innerHTML=Object.entries(C).map(([k,v])=>`<span class=k style="background:${v}"></span>${k}`).join("");
fetch("../graph.json").then(r=>r.json()).then(({nodes,edges})=>{
 const svg=d3.select("svg"),W=innerWidth,H=innerHeight,g=svg.append("g");
 svg.call(d3.zoom().on("zoom",e=>g.attr("transform",e.transform)));
 const R=d=>({person:16,speaker:13,video:10,account:6,wikidata:7}[d.type]);
 const sim=d3.forceSimulation(nodes).force("link",d3.forceLink(edges).id(d=>d.id).distance(e=>e.kind==="graph row"?50:110))
  .force("charge",d3.forceManyBody().strength(-380)).force("center",d3.forceCenter(W/2,H/2)).force("collide",d3.forceCollide(d=>R(d)+18));
 const link=g.append("g").selectAll("line").data(edges).join("line").attr("stroke","#3b4252").attr("stroke-width",e=>e.n?Math.min(1+e.n/15,8):1.2);
 const node=g.append("g").selectAll("circle").data(nodes).join("circle").attr("r",R).attr("fill",d=>C[d.type]).style("cursor",d=>d.href?"pointer":"default")
  .on("click",(e,d)=>{if(d.href)location.href=d.href.startsWith("http")?d.href:".."+d.href}).call(d3.drag().on("start",(e,d)=>{if(!e.active)sim.alphaTarget(.3).restart();d.fx=d.x;d.fy=d.y})
  .on("drag",(e,d)=>{d.fx=e.x;d.fy=e.y}).on("end",(e,d)=>{if(!e.active)sim.alphaTarget(0);d.fx=null;d.fy=null}));
 node.append("title").text(d=>d.label);
 const label=g.append("g").selectAll("text").data(nodes).join("text").text(d=>d.label.length>42?d.label.slice(0,40)+"…":d.label).attr("dx",d=>R(d)+4).attr("dy",4);
 const elabel=g.append("g").selectAll("text").data(edges.filter(e=>e.n)).join("text").text(e=>e.kind).style("fill","#7f8796").style("font-size","10px");
 sim.on("tick",()=>{link.attr("x1",d=>d.source.x).attr("y1",d=>d.source.y).attr("x2",d=>d.target.x).attr("y2",d=>d.target.y);
  node.attr("cx",d=>d.x).attr("cy",d=>d.y);label.attr("x",d=>d.x).attr("y",d=>d.y);
  elabel.attr("x",e=>(e.source.x+e.target.x)/2).attr("y",e=>(e.source.y+e.target.y)/2)});
});
</script></body></html>"""


def slugify(v):
    return re.sub(r"[^a-z0-9]+", "-", v.lower()).strip("-")


def page(title, body, crumbs):
    nav = "".join(f'<a href="{h}">{html.escape(t)}</a>' for t, h in crumbs)
    return (f"<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'>"
            f"<title>{html.escape(title)}</title><style>{CSS}</style></head><body><nav>{nav}</nav>{body}</body></html>")


def md(text):
    return markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def main():
    data, out = Path(sys.argv[1]), Path(sys.argv[2])
    if out.exists():
        shutil.rmtree(out)
    pub = out / "public"  # deploy with: cd <out> && wrangler pages deploy public
    links = json.loads((data / "watchlist/links.json").read_text()) if (data / "watchlist/links.json").exists() else {}
    lib = data / "library"
    people = sorted(p for p in lib.iterdir() if p.is_dir()) if lib.exists() else []
    home = [("Library", "/")]
    rows = []
    for person in people:
        slug, link = person.name, links.get(person.name, {})
        entries = sorted((e for e in person.iterdir() if e.is_dir()), reverse=True)
        cards = []
        for e in entries:
            meta = json.loads((e / "meta.json").read_text())
            base = f"/{slug}/{e.name}/"
            crumbs = home + [(link.get("name", slug), f"/{slug}/"), (meta["title"], base)]
            sub = [("transcript", e / "transcript.md"), ("feedback", e / "feedback.md")]
            notes = sorted((e / "notes").glob("*.md")) if (e / "notes").exists() else []
            tabs = " · ".join([f'<a href="{base}">doc</a>'] + [f'<a href="{base}{n}/">{n}</a>' for n, f in sub if f.exists()]
                              + ([f'<a href="{base}notes/">chunk notes ({len(notes)})</a>'] if notes else []))
            doc = (e / "DOC.md").read_text() if (e / "DOC.md").exists() else "*DOC.md not written yet.*"
            write(pub / base.strip("/") / "index.html", page(meta["title"], f"<p>{tabs}</p>" + md(doc), crumbs))
            for n, f in sub:
                if f.exists():
                    write(pub / base.strip("/") / n / "index.html", page(f"{n}: {meta['title']}", f"<p>{tabs}</p>" + md(f.read_text()), crumbs))
            if notes:
                write(pub / base.strip("/") / "notes/index.html", page(f"notes: {meta['title']}",
                      f"<p>{tabs}</p>" + "".join(f"<h2>Chunk {f.stem}</h2>" + md(f.read_text()) for f in notes), crumbs))
            done = "✅" if (e / "DOC.md").exists() else "⏳"
            cards.append(f'<div class="card">{done} <a href="{base}"><b>{html.escape(meta["title"])}</b></a><br>'
                         f'<small>{meta.get("date")} · {int(meta.get("duration") or 0) // 60} min · {meta.get("view_count") or 0:,} views · '
                         f'<a href="{meta.get("url")}">source</a></small></div>')
        graph = link.get("graph_rows", {})
        qid = link.get("qid")
        head = (f"<h1>{html.escape(link.get('name', slug))}</h1><div class='card'>"
                f"<b>Wikidata:</b> {f'<a href=https://www.wikidata.org/wiki/{qid}>{qid}</a>' if qid else 'none yet'}<br>"
                f"<b>Graph rows:</b> {', '.join(f'<code>{html.escape(k)}</code> <small>({html.escape(v)})</small>' for k, v in graph.items()) or 'none'}<br>"
                f"<b>Watched feeds:</b> {html.escape(json.dumps(link.get('feeds', {})))}</div><h2>Library ({len(entries)})</h2>")
        write(pub / slug / "index.html", page(slug, head + "".join(cards), home + [(slug, f"/{slug}/")]))
        rows.append(f'<div class="card"><a href="/{slug}/"><b>{html.escape(link.get("name", slug))}</b></a> '
                    f'<small>{len(entries)} entries · QID {qid or "none"}</small></div>')
    # The graph: watched people, speakers, videos, graph rows and Wikidata ids, as nodes and edges (graph.json + /graph/).
    nodes, edges, said = {}, [], {}
    owner = {}  # graph row id -> watched slug, so a speaker id resolves to the person page
    for slug, l in links.items():
        nodes[f"p:{slug}"] = {"id": f"p:{slug}", "label": l.get("name", slug), "type": "person", "href": f"/{slug}/"}
        for r in l.get("graph_rows", {}):
            owner[r] = slug
            nodes[f"g:{r}"] = {"id": f"g:{r}", "label": r, "type": "account"}
            edges.append({"source": f"p:{slug}", "target": f"g:{r}", "kind": "graph row"})
        if l.get("qid"):
            nodes[f"q:{l['qid']}"] = {"id": f"q:{l['qid']}", "label": l["qid"], "type": "wikidata", "href": f"https://www.wikidata.org/wiki/{l['qid']}"}
            edges.append({"source": f"p:{slug}", "target": f"q:{l['qid']}", "kind": "same as"})
    for person in people:
        for e in sorted(x for x in person.iterdir() if x.is_dir()):
            meta = json.loads((e / "meta.json").read_text())
            vid = f"v:{e.name}"
            nodes[vid] = {"id": vid, "label": meta["title"], "type": "video", "href": f"/{person.name}/{e.name}/"}
            nodes.setdefault(f"p:{person.name}", {"id": f"p:{person.name}", "label": person.name, "type": "person", "href": f"/{person.name}/"})
            edges.append({"source": f"p:{person.name}", "target": vid, "kind": "published"})
            counts = {}
            for line in (e / "utterances.jsonl").read_text().splitlines() if (e / "utterances.jsonl").exists() else []:
                u = json.loads(line)
                if u["speaker"] in ("unclear", "(speaker unclear)", None):
                    continue
                sp = owner.get(u["speaker"], u["speaker"])
                said.setdefault(sp, {"qid": u.get("qid"), "quotes": []})["quotes"].append((meta["title"], f"/{person.name}/{e.name}/", u))
                counts[sp] = counts.get(sp, 0) + 1
            for sp, n in counts.items():
                if sp in links:
                    sid = f"p:{sp}"
                else:
                    sid = f"s:{sp}"
                    nodes.setdefault(sid, {"id": sid, "label": sp, "type": "speaker", "href": f"/said/{slugify(sp)}/"})
                    q = said[sp]["qid"]
                    if q:
                        nodes.setdefault(f"q:{q}", {"id": f"q:{q}", "label": q, "type": "wikidata", "href": f"https://www.wikidata.org/wiki/{q}"})
                        if not any(x["source"] == sid and x["target"] == f"q:{q}" for x in edges):
                            edges.append({"source": sid, "target": f"q:{q}", "kind": "same as"})
                edges.append({"source": sid, "target": vid, "kind": f"said {n} quotes", "n": n})
    write(pub / "graph.json", json.dumps({"nodes": list(nodes.values()), "edges": edges}))
    write(pub / "graph/index.html", GRAPH_PAGE)
    # d3 is served from the site itself, so the page works inside app frames that block other origins
    import urllib.request
    (pub / "d3.min.js").write_bytes(urllib.request.urlopen("https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js", timeout=60).read())
    for sp, d in said.items():
        name = links.get(sp, {}).get("name", sp)
        items = "".join(f'<blockquote>{html.escape(u["text"])}<br><small><a href="{u["source"]}&t={int(u["t"])}s">{int(u["t"]) // 3600}:{int(u["t"]) % 3600 // 60:02d}:{int(u["t"]) % 60:02d}</a> · '
                        f'<a href="{href}">{html.escape(title)}</a></small></blockquote>' for title, href, u in d["quotes"])
        write(pub / "said" / slugify(sp) / "index.html", page(f"What {name} said", f"<h1>What {html.escape(name)} said</h1><p><small>{len(d['quotes'])} verbatim quotes"
              f"{' · Wikidata ' + d['qid'] if d['qid'] else ''}</small></p>" + items, home + [("Graph", "/graph/"), (name, f"/said/{slugify(sp)}/")]))
    rows.insert(0, '<div class="card"><a href="/graph/"><b>People graph</b></a> <small>who made what, who said what, and who they are in the graph</small><br>'
                + " · ".join(f'<a href="/said/{slugify(sp)}/">{html.escape(links.get(sp, {}).get("name", sp))}</a> <small>({len(d["quotes"])} quotes)</small>' for sp, d in sorted(said.items(), key=lambda x: -len(x[1]["quotes"]))) + "</div>")
    write(pub / "index.html", page("SISO library", "<h1>SISO library</h1><p><small>Everything interesting we watched or read, "
                                   "distilled, with its full transcript. Built by the output factory.</small></p>" + "".join(rows), home))
    write(out / "functions/_middleware.js", MIDDLEWARE)
    print(f"built {out}: {len(people)} people")


if __name__ == "__main__":
    main()
