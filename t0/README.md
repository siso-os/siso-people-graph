# t0: Wikidata skeleton and hard-key join

```sh
t0/fetch_keys.sh /tmp/pg-wd          # QLever key tables, ~5 min, ~250 MB
python3 t0/hardkey_join.py --db work.sqlite --keys /tmp/pg-wd --out judgements.jsonl
```
Output goes to `sisodias/siso-people-graph-data/judgements/`. Run of 15 Oct 2026: 22,414 of 339,217 rows gained a QID.
That's 47.3% of humans, 8.8% of orgs and 1.3% of accounts; it took 39 s.
The ceiling for accounts is structural: Wikidata holds only 16,754 GitHub logins (P2037) in total.
