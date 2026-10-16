from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "loaders"))
import load_youtube_creators as L  # noqa: E402


def graph(tmp: Path) -> str:
    db = tmp / "g.sqlite"
    con = sqlite3.connect(db)
    con.executescript((ROOT / "schema" / "people_schema_v2.sql").read_text())
    con.executemany("INSERT INTO person (person_id, name, state, origin, built_at) VALUES (?, ?, 'linked', ?, 'x')",
                    [("gh:fireship-io", "Jeff Delaney", "github"), ("yt:old_fireship", "Fireship", "youtube")])
    con.executemany("INSERT INTO external_ids (person_id, platform, value) VALUES (?, ?, ?)",
                    [("gh:fireship-io", "x_handle", "fireship_dev"), ("yt:old_fireship", "youtube_channel_id", "UCsBjURrPoezykLs9EqgamOA")])
    con.commit()
    return str(db)


class LoadYoutubeCreators(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.db = graph(self.tmp)
        rows = [
            {"rank": 1, "tier": "S", "score": 100, "handle": "@t3dotgg", "channel_id": "UCbRP3c757lWg9M-U7TyEkXA", "title": "Theo - t3.gg",
             "name": "Theo - t3.gg", "kind": "human", "x_handle": "theo", "x_source": "youtube"},
            {"rank": 2, "tier": "S", "score": 99, "handle": "@fireship", "channel_id": "UCsBjURrPoezykLs9EqgamOA", "title": "Fireship",
             "name": "Fireship", "kind": "human", "x_handle": "fireship_dev", "x_source": "youtube"},
            {"rank": 3, "tier": "S", "score": 98, "handle": "@nerd-snipe", "channel_id": "UC2mPtIOYm1XihpmfrJKXjMw", "title": "Nerd Snipe",
             "name": "Nerd Snipe", "kind": "organisation", "show": True, "x_handle": None},
        ]
        self.ranked = self.tmp / "r.jsonl"
        self.ranked.write_text("".join(json.dumps(r) + "\n" for r in rows))

    def q(self, sql: str):
        return sqlite3.connect(self.db).execute(sql).fetchall()

    def test_dry_run_writes_nothing(self) -> None:
        stats, _ = L.load(self.db, str(self.ranked), apply=False)
        self.assertEqual(2, stats["new"])
        self.assertEqual([], self.q("SELECT * FROM person_content"))

    def test_channel_id_wins_over_x_handle_and_new_people_are_namespaced(self) -> None:
        _, out = L.load(self.db, str(self.ranked), apply=True)
        self.assertEqual({"@t3dotgg": "yt:t3dotgg", "@fireship": "yt:old_fireship", "@nerd-snipe": "yt:nerd_snipe"},
                         {h: pid for _, h, pid, _ in out})
        self.assertEqual([("yt:nerd_snipe", "host")], self.q("SELECT person_id, role FROM person_content WHERE content_ref = 'UC2mPtIOYm1XihpmfrJKXjMw'"))
        self.assertEqual([("organisation",)], self.q("SELECT kind FROM person WHERE person_id = 'yt:nerd_snipe'"))

    def test_load_twice_is_the_same_graph(self) -> None:
        L.load(self.db, str(self.ranked), apply=True)
        before = self.q("SELECT count(*) FROM person"), self.q("SELECT count(*) FROM external_ids"), self.q("SELECT count(*) FROM person_content")
        L.load(self.db, str(self.ranked), apply=True)
        self.assertEqual(before, (self.q("SELECT count(*) FROM person"), self.q("SELECT count(*) FROM external_ids"), self.q("SELECT count(*) FROM person_content")))

    def test_atlas_adds_unknown_channels_as_tracked_and_joins_known_ones(self) -> None:
        atlas = self.tmp / "a.json"
        atlas.write_text(json.dumps([
            {"channel": "Fireship", "url": "https://www.youtube.com/channel/UCsBjURrPoezykLs9EqgamOA", "hits": 5, "total_views": 10, "keywords": ["js"]},
            {"channel": "codebasics", "url": "https://www.youtube.com/channel/UCh9nVJoWXmFb7sLApWGcLPQ", "hits": 782, "total_views": 354496484, "keywords": ["AI agents"]},
            {"channel": "codebasics", "url": "https://www.youtube.com/channel/UCh9nVJoWXmFb7sLApWGcLPQ", "hits": 437, "total_views": 1, "keywords": []},
            {"channel": "No URL", "url": "NA", "hits": 1805},
        ]))
        self.assertEqual({"channels": 2, "new_people": 1, "already_in_graph": 1}, L.load_atlas(self.db, [str(atlas)], apply=True))
        self.assertEqual([("unknown", "tracked")], self.q("SELECT kind, state FROM person WHERE person_id = 'yt:UCh9nVJoWXmFb7sLApWGcLPQ'"))
        self.assertEqual([(782.0,)], self.q("SELECT score FROM person_content WHERE content_ref = 'UCh9nVJoWXmFb7sLApWGcLPQ'"))

    def test_facts_add_x_and_claim_a_shared_handle_without_merging(self) -> None:
        L.load(self.db, str(self.ranked), apply=True)
        facts = self.tmp / "f.jsonl"
        facts.write_text(json.dumps({"ok": True, "channel_id": "UC2mPtIOYm1XihpmfrJKXjMw", "subscribers": 13300, "videos": 4,
                                     "last_upload": "3 days ago", "x_handle": "fireship_dev"}) + "\n")
        self.assertEqual({"live": 1, "x_handles": 1, "claims": 2, "not_in_graph": 0}, L.load_facts(self.db, str(facts), apply=True))
        self.assertEqual({("gh:fireship-io", "yt:nerd_snipe"), ("yt:nerd_snipe", "yt:old_fireship")},
                         set(self.q("SELECT person_a, person_b FROM identity_claim WHERE status = 'proposed'")))
        meta = json.loads(self.q("SELECT meta_json FROM person_content WHERE person_id = 'yt:nerd_snipe'")[0][0])
        self.assertEqual((13300, 4), (meta["subscribers"], meta["videos"]))


if __name__ == "__main__":
    unittest.main()
