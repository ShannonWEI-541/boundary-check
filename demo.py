"""Two fake scenarios; a score is accepted only after the declared overlap check."""
from pathlib import Path
import subprocess
import sys
import sandbox
import trace


def run(scenario):
    with sandbox.create(scenario) as directory:
        root = Path(directory)
        traced = trace.capture(root)
        checked = subprocess.run(
            [sys.executable, "-I", "-B", str(Path(__file__).with_name("check.py").resolve()),
             "toy-declarations.json", "toy-loads.json", "--report", "toy-decision.json"],
            cwd=root, text=True, capture_output=True,
        )
        if checked.returncode not in (0, 1):
            raise RuntimeError("checker failed")
        report = (root / "toy-decision.json").read_text(encoding="utf-8")
        return traced.stdout + checked.stdout, checked.returncode, report


if __name__ == "__main__":
    for scenario in ("clean", "overlap"):
        output, code, _ = run(scenario)
        print(f"=== {scenario} ===\n{output}checker exit: {code}")
        print("Score accepted" if code == 0 else "Score blocked")
