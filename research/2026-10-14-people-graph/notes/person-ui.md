# person-ui: structure of person pages (layout only, not styling)

Scope: 27 rows in rows/person-ui.jsonl. Usable captures: 13, plus GitHub at low confidence. Layout-only (wrong entity): 2. Blocked or 404: 10. Blank: 1.

Four new captures were taken this run: Wikidata Q317521 (usable), Factba.se (redirects to Roll Call Factbase, Joe Biden page, usable), Pantheon Elon profile (404), Crunchbase SpaceX org (Cloudflare).

## Section order, top to bottom, per site

1. **Wikipedia (Elon Musk).** Search bar, title, hatnote, bold lead with dated facts, right infobox (photo, Born, Citizenship, Education, Occupations), left ToC sidebar.
2. **Wikidata (Q317521).** Title with QID, one-line description, label/description/aliases table by language, statements grouped by property (instance of, image) with reference counts.
3. **Pantheon (Isaac Newton).** Nav, hero card (occupation tag, name in small caps, descriptor, life span, page-view sparkline), Discover-more list, then tabs for memorability, insights, trending, page views by language, peers in the same occupation.
4. **Google Scholar (Hinton).** Name, affiliation, verified-email line, topic chips, stats table (all vs since 2021), citations-per-year bars, works table sorted by citations, co-authors.
5. **Semantic Scholar (Hinton).** Count card (publications, h-index, citations, highly influential citations), follow button, co-authors with counts; right: tabs, filter row, paper list with TLDR and badges.
6. **IMDb (Spielberg).** Nav, name, role chips, headshot, featured clip, media tiles, bio, Born line, awards strip (wins and nominations), More to explore, Known-for cards, credit filter chips.
7. **Letterboxd (Nolan director).** Label, name, filter bar (decade, genre, service, sort, view), poster grid, right portrait card with bio and TMDB link.
8. **Goodreads (Stephen King).** Facts table (born, website, genre, influences), bio, Ask-the-author Q and A with likes, followers grid and videos in left column.
9. **FamousBirthdays (Elon Musk).** Headshot, name, role, 2x2 facts grid (birthday, sign, birthplace, age), rank pill with boost button, About, Before fame, Trivia.
10. **LittleSis (Elon Musk).** Title, one-line role sentence, tabs (Relationships, Interlocks, Giving, Data), grouped relationships with role subtitles, right column with Basic Info (types, aliases) and External Links (SEC, Wikipedia, Wikidata).
11. **LittleSis search.** Query box, then three buckets: Entities, Lists, Network Maps, each with snippets.
12. **Roll Call Factbase (formerly Factba.se).** Brand strip, name, search, filter column (event type, media), sort, then event rows (thumbnail, type, place, date, headline, View Transcript).
13. **X (@elonmusk).** Banner, avatar with verified badge, name, handle, bio link, join date, following and followers counts, Mention and Follow, tabs, pinned post.
14. **GitHub (ElonMusk).** Avatar, handle, follow, followers line, popular repos cards, contribution heatmap, year list. Low-confidence entity; zero activity.
15. **Muck Rack (layout only).** Name, outlet line, location, beat, "as seen in" outlets, bio, claim-profile box, article list (date, byline, outlet, snippet).
16. **Google Scholar, Semantic Scholar, IMDb (Ricky Tribord, layout only).** Known-for 2x2 card grid with rating, role, year.

## Best of

- **(a) Header plus rank:** FamousBirthdays. The 2x2 facts grid and the rank pill beside one action. Pantheon is the second choice for the sparkline attention signal (the Pantheon capture is Newton, not Elon).
- **(b) Works list:** Semantic Scholar for the per-paper TLDR and influence badge; Google Scholar for the sortable table and the since-2021 split. Letterboxd if the works are films (poster grid plus filters).
- **(c) Quotes and said timeline with sources:** Roll Call Factbase. Each row carries date, place, event type and a transcript action. Goodreads "Ask the author" is the only quote-style block, but it is not sourced.
- **(d) Identities and sources panel:** LittleSis External Links box (SEC, Wikipedia, Wikidata in one list) and the Wikidata aliases table for name variants.
- **(e) Related people:** Google Scholar co-authors and Semantic Scholar co-authors (both show counts beside each name). Goodreads influences row as link chips.
- **(f) Leaderboard:** FamousBirthdays rank pill (Most Popular #88). Pantheon's peer tab for the same occupation is the better model if the rank needs a peer set.
- **(g) Org page:** LittleSis relationship groups (Leadership and Staff, Business Positions, Board Memberships) with a per-org role line. Crunchbase org layout is still missing (blocked).

## Gaps still open

- Crunchbase (person and org) and OpenAlex are behind Cloudflare; PeoplePill too. A browser session that passes the check is needed, or use the APIs.
- No clean Pantheon Elon profile; the attempted URL 404s. Try a search route on Pantheon.
- Trump said-timeline: the Factbase URL we used returned File not found; the Roll Call Factbase page for Trump has not been captured.
- No Elon Musk Factbase/Roll Call page either; the captured Factbase page is Joe Biden.
- Entity checks: IMDb Ricky Tribord and Muck Rack Ray Finlayson are the wrong people; GitHub ElonMusk is unlikely to be the public figure.
