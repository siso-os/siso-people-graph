#!/bin/zsh
# Archive each creator via Apify, three passes each (the actor returns part of a batch; passes converge). Shaan, 16 Oct.
cd ~/SISO_Workspace/_data/people-watch
for slug in "$@"; do for pass in 1 2 3; do python3 app/people_watch.py archive $slug --via apify; done; done
