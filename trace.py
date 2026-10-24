"""Audit the cooperative toy evaluator. Opens are conservative load proxies.

Only sandbox-relative paths are saved. This is not a security boundary:
native code, preloaded modules, subprocesses and hostile code are not covered.
"""
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys


def capture(root):
    root = Path(root).resolve()
    if not root.is_relative_to(Path(__file__).resolve().parent):
        raise ValueError("toy root must stay inside this repository")
    return subprocess.run(
        [sys.executable, "-I", "-B", str(Path(__file__).resolve()),
         "--child", str(root)],
        cwd=root, text=True, capture_output=True, check=True,
    )


def child(root):
    root = Path(root).resolve()
    if not root.is_relative_to(Path(__file__).resolve().parent):
        raise ValueError("toy root must stay inside this repository")
    events = set()
    active = True

    def audit(event, args):
        if not active or event not in ("open", "import"):
            return
        raw = args[0] if event == "open" else args[1]
        if not isinstance(raw, (str, bytes)):
            return
        try:
            relative = Path(os.path.abspath(os.fsdecode(raw))).relative_to(root)
        except (ValueError, OSError):
            return
        events.add((event, relative.as_posix()))

    sys.path.insert(0, str(root))
    sys.addaudithook(audit)
    runpy.run_path(str(root / "toy_grader.py"), run_name="__main__")
    active = False
    # Failed .pyc lookups and other nonexistent open attempts are not loads.
    events = sorted((event, name) for event, name in events if (root / name).is_file())
    report = {"loaded_files": sorted({name for _, name in events}),
              "events": [{"event": event, "file": name} for event, name in events]}
    (root / "toy-loads.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] != "--child":
        raise SystemExit("usage: trace.py --child SANDBOX_ROOT")
    child(sys.argv[2])
