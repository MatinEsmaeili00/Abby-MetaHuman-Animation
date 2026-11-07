#!/bin/zsh
# Run the PIE probe job with an action, e.g.:  tools/pie.sh status | depth:0.3 | layer:2 | play | pause | reverse | time:0.5 | speed:0.9 | switch:1
REPO="$(cd "$(dirname "$0")/.." && pwd)"
TMP="${TMPDIR:-/tmp}/pie_probe_$$.py"
sed "s/__ACTION__/${1:-status}/" "$REPO/scripts/jobs/37_pie_probe.py" > "$TMP"
python3 -I "$REPO/tools/ue_bridge.py" "$TMP" --timeout "${2:-60}"
rm -f "$TMP"
