"""Demo overlap check: manifest declarations, NOT real OS ACL writability.

Paths are sandbox-relative, case-insensitive, with either slash separator.
Literal entries match a file or directory subtree; globs use fnmatch semantics
(including '*' matching '/'). No symlink, junction or hardlink resolution.
"""
import argparse
import fnmatch
import json
import ntpath
import posixpath
from pathlib import Path


def normalize(path):
    if not isinstance(path, str) or not path:
        raise ValueError("paths must be nonempty strings")
    path = path.replace("\\", "/")
    if ntpath.splitdrive(path)[0] or path.startswith("/"):
        raise ValueError("paths must be sandbox-relative")
    path = posixpath.normpath(path).casefold()
    if path == ".." or path.startswith("../"):
        raise ValueError("paths must stay inside sandbox")
    return path


def assess(manifest, loaded):
    patterns = manifest.get("candidate_writable", [])
    if not isinstance(patterns, list) or not isinstance(loaded["loaded_files"], list):
        raise ValueError("candidate_writable and loaded_files must be lists")
    patterns = [normalize(pattern) for pattern in patterns]
    rows = []
    for name in sorted({normalize(name) for name in loaded["loaded_files"]}):
        writable = any(
            pattern == "." or fnmatch.fnmatchcase(name, pattern)
            or (not any(c in pattern for c in "*?[") and name.startswith(pattern + "/"))
            for pattern in patterns
        )
        rows.append({"file": name, "writable_by_candidate": writable,
                     "loaded_by_evaluator": True, "flag": "OVERLAP" if writable else "-"})
    overlap = [row["file"] for row in rows if row["writable_by_candidate"]]
    return {"basis": "declared manifest; not OS ACLs", "overlap": overlap,
            "score_accepted": not overlap, "rows": rows}


def local_file(name):
    """Keep CLI inputs and output inside this demo repository."""
    if ntpath.splitdrive(name)[0] or Path(name).is_absolute():
        raise ValueError("CLI file paths must be repository-relative")
    repository = Path(__file__).resolve().parent
    path = (Path.cwd() / name).resolve()
    if not path.is_relative_to(repository):
        raise ValueError("CLI file paths must stay inside this repository")
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest")
    parser.add_argument("loaded")
    parser.add_argument("--report", default="report.json")
    args = parser.parse_args()
    report = assess(json.loads(local_file(args.manifest).read_text(encoding="utf-8")),
                    json.loads(local_file(args.loaded).read_text(encoding="utf-8")))
    print("file | writable-by-candidate | loaded-by-evaluator | flag")
    for row in report["rows"]:
        print(f"{row['file']} | {str(row['writable_by_candidate']).lower()} | true | {row['flag']}")
    local_file(args.report).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("JSON:", json.dumps(report, sort_keys=True))
    return int(bool(report["overlap"]))


if __name__ == "__main__":
    raise SystemExit(main())
