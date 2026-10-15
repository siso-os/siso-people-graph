#!/bin/sh
# Output factory, step 4: check quotes, commit the library to the data repo, rebuild and deploy the site.
# Usage: factory/publish.sh [data-repo]   (default ~/SISO_Workspace/_data/people-graph-data)
set -eu
here=$(cd "$(dirname "$0")" && pwd)
data=${1:-$HOME/SISO_Workspace/_data/people-graph-data}
fail=0
for d in "$data"/library/*/*/; do [ -f "$d/DOC.md" ] && { python3 "$here/verify.py" "$d" | head -1 || fail=1; }; done
git -C "$data" add -A library watchlist
git -C "$data" diff --cached --quiet || git -C "$data" commit -qm "library: $(date +%F) output factory run"
git -C "$data" push -q
out=$(mktemp -d)
uv run -q --with markdown "$here/build_site.py" "$data" "$out"
set -a; . "$HOME/SISO_Workspace/.credentials/projects/sisolabs-cloudflare.env"; set +a
(cd "$out" && wrangler pages deploy public --project-name siso-library --branch main --commit-dirty=true | tail -1)
echo "live: https://siso-library.pages.dev (user siso, password in .credentials/projects/siso-library.env)"
