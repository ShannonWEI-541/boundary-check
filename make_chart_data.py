"""Run four toy sandboxes and save measurements from the real checker."""

import csv
import json
from pathlib import Path
import subprocess
import sys

import check
import sandbox
import trace


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SCENARIOS = (("clean", 0), ("overlap", 1), ("synthetic_2", 2), ("synthetic_3", 3))
FIELDS = ("scenario", "files_total", "candidate_writable", "evaluator_loaded",
          "overlap", "score_accepted")


def measure(scenario, expected_overlap):
    with sandbox.create(scenario) as directory:
        root = Path(directory)
        # Inventory the initial sandbox before the tracer and checker add their files.
        inventory = sorted(path.relative_to(root).as_posix()
                           for path in root.rglob("*") if path.is_file())
        manifest = json.loads((root / "toy-declarations.json").read_text(encoding="utf-8"))
        trace.capture(root)
        checked = subprocess.run(
            [sys.executable, "-I", "-B", str(BASE / "check.py"),
             "toy-declarations.json", "toy-loads.json", "--report", "toy-decision.json"],
            cwd=root, capture_output=True, text=True, check=False,
        )
        if checked.returncode not in (0, 1):
            raise RuntimeError(f"checker failed for {scenario}: {checked.stderr}")
        raw = (root / "toy-decision.json").read_text(encoding="utf-8")
        decision = json.loads(raw)
        loaded = json.loads((root / "toy-loads.json").read_text(encoding="utf-8"))
        inventory_decision = check.assess(manifest, {"loaded_files": inventory})
        overlap = len(decision["overlap"])
        if overlap != expected_overlap or checked.returncode != int(overlap > 0):
            raise RuntimeError(f"unexpected checker outcome for {scenario}")
        if decision["score_accepted"] != (overlap == 0):
            raise RuntimeError(f"inconsistent checker decision for {scenario}")
        # The checker's report stores only normalized sandbox-relative toy paths.
        for name in decision["overlap"]:
            check.normalize(name)
        return {
            "scenario": scenario,
            "files_total": len(inventory),
            "candidate_writable": len(inventory_decision["overlap"]),
            "evaluator_loaded": len(loaded["loaded_files"]),
            "overlap": overlap,
            "score_accepted": str(decision["score_accepted"]).lower(),
        }, raw


def main():
    RESULTS.mkdir(exist_ok=True)
    raw_dir = RESULTS / "raw"
    raw_dir.mkdir(exist_ok=True)
    rows = []
    for scenario, expected_overlap in SCENARIOS:
        row, raw = measure(scenario, expected_overlap)
        (raw_dir / f"{scenario}.json").write_text(raw, encoding="utf-8", newline="\n")
        rows.append(row)
    csv_path = RESULTS / "overlap_summary.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(csv_path.read_text(encoding="utf-8"), end="")
    print("Saved 4 raw checker JSON reports in results/raw/")


if __name__ == "__main__":
    main()
