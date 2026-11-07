#!/usr/bin/env python3
"""Run Python inside the running Unreal Editor via the PythonScriptPlugin remote-execution protocol.

Usage:
    ue_py.py -c "import unreal; print(unreal.SystemLibrary.get_engine_version())"
    ue_py.py path/to/script.py [--arg value ...]   (script args are exposed as sys.argv inside UE)

Requires Project Settings > Plugins > Python > Enable Remote Execution (localhost only by default).
"""
import argparse
import json
import os
import sys
import time

UE_PY = os.environ.get(
    "UE_REMOTE_EXEC_DIR",
    "/Users/Shared/Epic Games/UE_5.8/Engine/Plugins/Experimental/PythonScriptPlugin/Content/Python",
)
sys.path.insert(0, UE_PY)
import remote_execution  # noqa: E402


def run(command: str, timeout: float = 10.0, exec_mode: str = remote_execution.MODE_EXEC_FILE):
    re = remote_execution.RemoteExecution()
    re.start()
    try:
        deadline = time.time() + timeout
        while not re.remote_nodes and time.time() < deadline:
            time.sleep(0.2)
        if not re.remote_nodes:
            raise SystemExit("No Unreal Editor found (is the editor open with Remote Execution enabled?)")
        node = re.remote_nodes[0]
        re.open_command_connection(node["node_id"])
        result = re.run_command(command, unattended=True, exec_mode=exec_mode)
        re.close_command_connection()
        return result
    finally:
        re.stop()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script", nargs="?")
    ap.add_argument("-c", dest="code")
    ap.add_argument("--json", action="store_true", help="print raw JSON result")
    args, rest = ap.parse_known_args()
    if args.code:
        res = run(args.code, exec_mode=remote_execution.MODE_EXEC_FILE)
    elif args.script:
        path = os.path.abspath(args.script)
        argv = [path] + rest
        code = (
            "import sys, runpy\n"
            f"sys.argv = {json.dumps(argv)}\n"
            f"runpy.run_path({json.dumps(path)}, run_name='__main__')\n"
        )
        res = run(code)
    else:
        ap.error("give a script path or -c CODE")
    if args.json:
        print(json.dumps(res, indent=2))
        return
    for line in res.get("output", []):
        sys.stdout.write(line.get("output", "") + ("" if line.get("output", "").endswith("\n") else "\n"))
    if not res.get("success", False):
        sys.stdout.write("RESULT: " + str(res.get("result")) + "\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
