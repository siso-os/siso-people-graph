# graph-explorers: patterns for a browsable 339k-person graph

Scale we are designing for: 339,217 people, ~900k person-work edges, ~2M topic edges (about 2.9M edges total). Drawing everything at once is the hairball; no tool in the slice does it well in 2D canvas or SVG. The working answer across tools is: never render the full graph. Show a small subgraph (ego or similarity neighbourhood), an overview map of points without edges, or a filtered timeline.

## Patterns that work at 300k+ nodes

1. **Ego view as the default (top-k, capped).** Connected Papers shows a few dozen papers chosen from ~50,000 candidates by similarity, with the origin in the middle. Obsidian's local graph uses a depth-limited neighbourhood. For us: pick a person, show the 1-hop neighbours ranked by edge weight, cap at about 200-300 nodes, drop the rest into a "more" list.
2. **Progressive expansion with relation-typed tabs.** ResearchRabbit separates expansions into earlier / later / similar / co-author. Expansion adds nodes to the same graphology graph (incremental), not a reload. Label each expansion by the edge type that produced it.
3. **Overview as points, not edges.** Embedding Atlas (MIT, WebGPU, "up to a few million points") and Nomic Atlas (hosted) place items on a 2D similarity map with density contours and clustering labels. Our 2M topic edges become a layout input (e.g. UMAP of a person-by-topic vector, computed offline), so they never reach the screen. Edges appear only after a click or lasso.
4. **Clustering and collapse.** Compute communities offline (Louvain via graphology-communities-louvain or igraph), store a cluster id per person, and show a super-node per cluster at low zoom. cosmos.gl ships a point-clustering force (v2) for pulling same-cluster points together; Cytoscape.js compound nodes let a cluster expand on double-click.
5. **Level of detail by zoom.** deck.gl ScatterplotLayer plus aggregation layers (hexbin counts) at low zoom, individual points on zoom-in (Uber: 860K circles instanced). Labels only above a zoom threshold.
6. **Filters before layout, with live counts.** Cosmograph's model: DuckDB-Wasm aggregates on filter, and only the visible subset goes to the GPU. Embedding Atlas and Gephi Lite do the same with side-panel cross-filter charts and attribute filters. Filter by work type, year, topic, role; drop edges before layout.
7. **Timeline and year axes.** Litmaps plots year against citation count (hollow vs solid nodes for suggested vs known). Histomania and Histropedia draw life-span lanes or query-driven timelines. For person-work edges, year is a native axis: one lane per person, with works as ticks.
8. **Path and "why is this near" highlight.** Connected Papers highlights the shortest similarity path to the origin on click. Wikidata metaphacts offers pathfinding between two items. Copy: click two people, show the shortest chain of shared works.
9. **Story mode for non-experts.** Oligrapher (GPL-3) and Kumu give click-through annotated views. A curated "start here" path through the graph beats a free canvas for first-time visitors.
10. **Browse by facet first, graph second.** Pantheon (BY-SA site, 85k bios) uses occupation x country x era landing pages, and each profile shows related people. Scholia uses a profile-first layout with a small co-author graph under the list. The graph is a panel on the profile, not the front page.

Limits we found (none are benchmarks on our data):
- cosmos.gl: "hundreds of thousands of points and links on modern hardware" (README); "over one million" (OpenJS blog, vendor claim).
- Embedding Atlas: "up to a few million points" (WebGPU, repo page).
- Graphistry client: up to 8M nodes+edges, 100K-2M smooth on older GPUs (PyPI listing).
- Sigma.js: "thousands of nodes and edges" (tagline, no number). Knogin.com claims 100k at 30-60 fps; anecdotal.
- react-force-graph and Cytoscape.js: no numeric limits on the repo pages; canvas-based, so assume thousands, not hundreds of thousands.
- Obsidian forum: practical 5k-25k notes; plugin claims 20k nodes at ~75 fps (unverified).

## Recommended stack for the explore page

Data (offline, in our pipeline):
- Precompute per person: x,y similarity coordinates (UMAP or Nomic-style projection of person vectors), cluster id (Louvain), degree, top-20 neighbours by weight. Write as static JSON or Parquet per district, plus a SQLite recursive-CTE ego query with LIMIT for on-demand depth 2.
- Keep all 2M topic edges in the database; expose topic as a filter and as cluster labels, not as drawn edges.

Browser stack (all MIT except where marked):
- Overview map: deck.gl ScatterplotLayer + hexbin aggregation (licence to verify on github.com/visgl/deck.gl), or Embedding Atlas as a reference/drop-in if its licence and WebGPU fallback suit (MIT, verified).
- Overview alternative for the actual graph shape: cosmos.gl (MIT, verified) with clustering force, only after a benchmark on our 900k edges.
- Ego view: sigma.js v3 + graphology (MIT, verified), ForceAtlas2 in a web worker, reducers to dim non-ego nodes. Cap at ~300 nodes.
- Timeline and facet panels: plain SVG/canvas; Pantheon-style facet landing pages.
- Avoid for the core: Cosmograph packages (CC-BY-NC conflict, unresolved); Gephi Lite and Oligrapher code (GPL-3, reuse ideas only); Kumu, Litmaps, ResearchRabbit, Connected Papers, Nomic (proprietary).

Interaction model (one page, one selection at a time):
1. Search a person or pick a facet (occupation, country, era, topic). The overview map re-filters with live counts.
2. Click a point: ego card opens with 1-hop neighbours (top 50 by weight) in sigma; hover dims the rest.
3. Click a neighbour: re-centre the ego view on it (keeps history as breadcrumbs). "Expand" adds its top 20 neighbours to the same graph.
4. Lasso or density-click on the overview: selects a cluster; right panel lists members and a year timeline of their works.
5. Two-person pathfinding: shortest chain of shared works, highlighted (Connected Papers pattern).
6. Export: GEXF or CSV of the current subgraph for power users (Gephi Lite opens GEXF from a URL).

## Still missing / to check
- Benchmark on our data: 339k nodes, 900k edges, synthetic and real, in sigma and cosmos.gl on a laptop and a phone. No vendor figure in this slice is measured on our graph.
- Licences unverified: deck.gl (LICENSE file), Cosmograph (Citing and licensing page), Scholia and Inciteful (repos not found), Fast 3D Graph plugin, Aleph Pro.
- Not covered by this slice: Neo4j Bloom and Linkurious Enterprise (commercial visualisers), Semantic Scholar's graph UI, Retina, OpenSanctions network view, LittleSis's own map pages, vis-network, datashader (BSD) for server-side point rasters. Worth a second pass if the explore page needs server rendering.
- Pricing for Kumu, Litmaps, Nomic and Connected Papers is unverified (third-party listings only).
