#!/bin/zsh
# Launch the Unreal Editor on the MetaHumanTest project with
#   - the MCP server started (-ModelContextProtocolStartServer)
#   - the file-based Python bridge started (tools/claude_bridge.py via -ExecutePythonScript)
set -e
ENGINE_APP="${ENGINE_APP:-/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app}"
PROJECT="${PROJECT:-/Users/mesmae6/Perforce/maclab_digitalhuman_main/MetaHumanTestCopy2Mac/MetaHumanTest.uproject}"
BRIDGE="$(cd "$(dirname "$0")" && pwd)/claude_bridge.py"

if pgrep -f 'UnrealEditor.app/Contents/MacOS/UnrealEditor' >/dev/null; then
  echo "Unreal Editor is already running"; exit 1
fi
open -a "$ENGINE_APP" --args "$PROJECT" -ModelContextProtocolStartServer "-ExecutePythonScript=$BRIDGE"
echo "launched"
