#!/bin/sh
# Pull the Wikidata key tables hardkey_join.py needs from QLever (minutes, no 43.5 GB dump).
# Usage: t0/fetch_keys.sh <outdir>. Sequential on purpose: QLever answers 429 to parallel calls.
set -eu
out=${1:?outdir}; mkdir -p "$out"
Q=https://qlever.dev/api/wikidata
P='PREFIX wdt: <http://www.wikidata.org/prop/direct/> PREFIX wd: <http://www.wikidata.org/entity/> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>'
get() {
  curl -sf -m 900 --retry 3 --retry-delay 10 -G "$Q" --data-urlencode "query=$P $2" \
    -H 'Accept: text/tab-separated-values' -o "$out/$1.tsv"
  echo "$1 $(wc -l < "$out/$1.tsv") lines"
}
for p in P496 P2037 P2002 P2397 P1938; do get $p "SELECT ?i ?v WHERE { ?i wdt:$p ?v }"; done
get P2034_P50 'SELECT ?a ?g WHERE { ?b wdt:P2034 ?g . ?b wdt:P50 ?a }'
get human_years 'SELECT ?i ?l (YEAR(?b) AS ?by) (YEAR(?d) AS ?dy) WHERE { ?i wdt:P31 wd:Q5 ; wdt:P569 ?b ; wdt:P570 ?d ; rdfs:label ?l . FILTER(LANG(?l)="en") }'
