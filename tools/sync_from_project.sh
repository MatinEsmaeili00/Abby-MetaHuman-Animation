#!/bin/zsh
# Copies the tracked parts of the Unreal project (Perforce workspace) into this repo.
# The full project (~7 GB of MetaHuman / scan content) is NOT mirrored here, only:
#   - .uproject, Config/, Source/
#   - the specific .uasset files listed in tools/tracked_assets.txt (assets we create or change)
set -e
PROJECT="${PROJECT:-/Users/mesmae6/Perforce/maclab_digitalhuman_main/MetaHumanTestCopy2Mac}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"

mkdir -p "$REPO/project/Config" "$REPO/project/Content"
cp "$PROJECT/MetaHumanTest.uproject" "$REPO/project/"
cp "$PROJECT"/Config/*.ini "$REPO/project/Config/"
rsync -a --delete "$PROJECT/Source/" "$REPO/project/Source/"

# Never publish the Android File Server token.
sed -i '' -E 's/^SecurityToken=.*/SecurityToken=REDACTED/' "$REPO/project/Config/DefaultEngine.ini"

# Tracked assets: one Content-relative path per line, e.g. MetaHumans/MH_CH_Abby5/BP_MH_CH_Abby8.uasset
if [[ -f "$REPO/tools/tracked_assets.txt" ]]; then
  while IFS= read -r rel; do
    [[ -z "$rel" || "$rel" == \#* ]] && continue
    if [[ -f "$PROJECT/Content/$rel" ]]; then
      mkdir -p "$REPO/project/Content/$(dirname "$rel")"
      cp "$PROJECT/Content/$rel" "$REPO/project/Content/$rel"
    else
      echo "warning: missing $rel" >&2
    fi
  done < "$REPO/tools/tracked_assets.txt"
fi

chmod -R u+w "$REPO/project"
echo "synced from $PROJECT"
