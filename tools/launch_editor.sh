#!/bin/zsh
# Launch the Unreal Editor on the MetaHumanTest project with
#   - the MCP server started (-ModelContextProtocolStartServer)
#   - the file-based Python bridge started (tools/claude_bridge.py via -ExecCmds="py ...")
set -e
ENGINE_APP="${ENGINE_APP:-/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app}"
PROJECT="${PROJECT:-/Users/mesmae6/Perforce/maclab_digitalhuman_main/MetaHumanTestCopy2Mac/MetaHumanTest.uproject}"
BRIDGE="$(cd "$(dirname "$0")" && pwd)/claude_bridge.py"

if pgrep -x UnrealEditor >/dev/null; then
  echo "Unreal Editor is already running"; exit 1
fi
# NOTE: -ExecutePythonScript quits the editor when the script returns (UE 5.8), so use ExecCmds + py instead.
open -a "$ENGINE_APP" --args "$PROJECT" -ModelContextProtocolStartServer "-ExecCmds=py $BRIDGE"
echo "launched"
