"""Synthetic L03 ports: explicit paths, read-only attachments and provenance."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from query_v3 import QueryEngine  # noqa: E402
from query_v3.config import Config, load  # noqa: E402
from tests.query_v3.fixtures import build_books_db, build_people_db  # noqa: E402


class LocalSourceConsolidationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        # SQL and URI punctuation must stay in the filename. ?mode=rwc must
        # never become a URI option that relaxes the read contract.
        self.people = self.root / "creator's graph?mode=rwc#%.sqlite"
        self.books = self.root / "books' domain?mode=rwc#%.sqlite"
        build_people_db(str(self.people))
        build_books_db(str(self.books))
        self.meta = '{"rights":"unknown","fixture":true,"note":"quoted \' value"}'
        con = sqlite3.connect(self.people)
        with con:
            con.execute(
                "UPDATE person_content SET source=?, observed_at=?, meta_json=? "
                "WHERE person_id='bk:kant' AND domain='book' AND content_ref='4280'",
                ("fixture-loader", "2000-01-01T00:00:00Z", self.meta),
            )
        # Use rollback journals for byte-for-byte, no-sidecar preservation checks.
        # This does not claim immutable snapshot semantics for live WAL writers.
        con.execute('PRAGMA journal_mode=DELETE')
        con.close()
        # Isolate every test from machine database configuration.
        self.env = {k: v for k, v in os.environ.items()
                    if not k.startswith('PEOPLE_GRAPH_')}
        self.env['PYTHONDONTWRITEBYTECODE'] = '1'
        self.env_patch = patch.dict(os.environ, self.env, clear=True)
        self.env_patch.start()
        self.addCleanup(self.env_patch.stop)

    def snapshot(self):
        return {str(p.relative_to(self.root)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.root.rglob('*') if p.is_file()}

    def cli(self, *args):
        return subprocess.run(
            [sys.executable, '-B', str(REPO / 'loaders/ask.py'), *args],
            cwd=self.root, env=self.env, capture_output=True, text=True,
        )

    def test_provenance_and_identity_survive_encoded_readonly_attachments(self):
        before = self.snapshot()
        with QueryEngine(explicit_paths={'people': str(self.people),
                                         'books': str(self.books)},
                         root=str(self.root)) as engine:
            result = engine.works('Kant')
            self.assertEqual(result['page']['total_matched'], 4)
            self.assertEqual(result['result']['person']['member_ids'],
                             ['bk:kant', 'gh:kant'])
            work = next(w for w in result['result']['works'] if w['ref'] == '4280')
            self.assertEqual(work['source'], 'fixture-loader')
            self.assertEqual(work['observed_at'], '2000-01-01T00:00:00Z')
            self.assertEqual(work['meta_json'], self.meta)
            self.assertEqual(work['evidence']['source'], work['source'])
            self.assertEqual(work['evidence']['observed_at'], work['observed_at'])
            self.assertEqual(work['evidence']['grade'], 'source_observation')
            self.assertEqual(set(engine.caps.domains), {'people', 'books'})
            self.assertTrue(engine.who('Plato')['result']['matches'])
            self.assertGreater(engine.con.execute(
                'SELECT COUNT(*) FROM people.identity_claim').fetchone()[0], 0)
            for schema, table in [('main', 'identity_claim'),
                                  ('people', 'identity_claim'), ('books', 'book')]:
                with self.subTest(schema=schema):
                    with self.assertRaisesRegex(sqlite3.OperationalError, 'readonly'):
                        engine.con.execute(f'DELETE FROM {schema}.{table}')
        self.assertEqual(self.snapshot(), before)

    def test_people_db_alias_preserves_current_cli_envelope(self):
        before = self.snapshot()
        results = []
        for flag in ['--people', '--people-db']:
            proc = self.cli(flag, str(self.people), '--works', 'Kant', '--limit', '1')
            self.assertEqual(proc.returncode, 0, proc.stderr)
            result = json.loads(proc.stdout)
            self.assertEqual(result['page']['returned'], 1)
            self.assertEqual(result['page']['total_matched'], 4)
            self.assertTrue(result['page']['truncated'])
            self.assertEqual(result['sources']['people']['path_origin'], 'explicit')
            self.assertEqual(result['sources']['people']['path'], str(self.people))
            self.assertIn('meta_json', result['result']['works'][0])
            results.append(result)
        for key in ['result', 'page', 'sources', 'identity_resolution']:
            self.assertEqual(results[0][key], results[1][key])
        self.assertEqual(self.snapshot(), before)

    def test_bad_explicit_path_never_falls_back_or_creates_files(self):
        # Valid local and environment defaults must not hide a bad explicit path.
        build_people_db(str(self.root / 'people_v2.sqlite'))
        self.env['PEOPLE_GRAPH_PEOPLE'] = str(self.people)
        before = self.snapshot()
        for path in [self.root / 'not-created.sqlite', self.root, '']:
            for flag in ['--people', '--people-db']:
                with self.subTest(path=str(path), flag=flag):
                    proc = self.cli(flag, str(path), '--works', 'Kant')
                    self.assertEqual(proc.returncode, 2)
                    self.assertIn('people database is not a file', proc.stderr)
                    self.assertEqual(proc.stdout, '')
            with self.assertRaisesRegex(ValueError, 'people database is not a file'):
                load(explicit={'people': str(path)}, root=str(self.root), env=self.env)
        self.assertEqual(self.snapshot(), before)

    def test_missing_attachment_does_not_create_a_database(self):
        missing = self.root / "missing' domain?mode=rwc#.sqlite"
        before = self.snapshot()
        cfg = Config(paths={'people': str(self.people), 'books': str(missing)})
        with QueryEngine(config=cfg) as engine:
            self.assertEqual(set(engine.caps.domains), {'people'})
            self.assertFalse(engine.source()['sources']['books']['attached'])
            self.assertTrue(engine.who('Plato')['result']['matches'])
        self.assertEqual(self.snapshot(), before)
        self.assertFalse(missing.exists())

    def test_missing_main_does_not_create_a_database(self):
        missing = self.root / 'absent?mode=rwc#.sqlite'
        before = self.snapshot()
        with self.assertRaises(sqlite3.OperationalError):
            QueryEngine(config=Config(paths={'people': str(missing)}))
        self.assertEqual(self.snapshot(), before)

    def test_existing_configuration_precedence_is_preserved(self):
        local = self.root / 'people_v2.sqlite'
        build_people_db(str(local))
        conf = self.root / 'domains.json'
        conf.write_text(json.dumps({'domains': {'people': str(self.people)}}))
        env = {'PEOPLE_GRAPH_CONFIG': str(conf),
               'PEOPLE_GRAPH_PEOPLE': str(local)}
        cfg = load(explicit={'people': str(local)}, root=str(self.root), env=env)
        self.assertEqual(cfg.paths['people'], str(local))
        self.assertEqual(cfg.origins['people'], 'explicit')
        cfg = load(root=str(self.root), env=env)
        self.assertEqual(cfg.paths['people'], str(self.people))
        self.assertEqual(cfg.origins['people'], f'config:{conf}')
        cfg = load(root=str(self.root), env={'PEOPLE_GRAPH_PEOPLE': str(self.people)})
        self.assertEqual(cfg.paths['people'], str(self.people))
        self.assertEqual(cfg.origins['people'], 'env')
        cfg = load(root=str(self.root), env={})
        self.assertEqual(cfg.paths['people'], str(local))
        self.assertEqual(cfg.origins['people'], 'default_local')


if __name__ == '__main__':
    unittest.main()
