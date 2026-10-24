"""Draw the one-overlap checker report as a deterministic toy SVG diagram."""

from html import escape
import csv
import json
import ntpath
from pathlib import Path, PurePosixPath

import check
import sandbox


BASE = Path(__file__).resolve().parent
SOURCE = BASE / "results" / "raw" / "overlap.json"
OUTPUT = BASE / "results" / "overlap_diagram.svg"
CSV = BASE / "results" / "overlap_summary.csv"


def safe_file(name):
    if not isinstance(name, str) or not name or "\\" in name:
        raise ValueError("expected a sandbox-relative toy file name")
    path = PurePosixPath(name)
    if path.is_absolute() or ntpath.splitdrive(name)[0] or ".." in path.parts:
        raise ValueError("expected a sandbox-relative toy file name")
    return name


def card(x, y, name, highlighted):
    background = "#FBE9E7" if highlighted else "#F5F7FA"
    border = "#B13C3C" if highlighted else "#697586"
    weight = "bold" if highlighted else "normal"
    parts = [f'<rect x="{x}" y="{y}" width="260" height="44" rx="7" fill="{background}" stroke="{border}" stroke-width="2"/>']
    center = x + 130
    if len(name) > 23 and "/" in name:
        parent, leaf = name.rsplit("/", 1)
        parts.append(f'<text x="{center}" y="{y + 18}" text-anchor="middle" fill="#202830" font-size="18" font-weight="{weight}"><tspan x="{center}">{escape(parent)}/</tspan><tspan x="{center}" dy="19">{escape(leaf)}</tspan></text>')
    else:
        parts.append(f'<text x="{center}" y="{y + 29}" text-anchor="middle" fill="#202830" font-size="19" font-weight="{weight}">{escape(name)}</text>')
    return parts


def declared_writable_files():
    """Expand the overlap scenario's manifest against its generated toy files."""
    with sandbox.create("overlap") as directory:
        root = Path(directory)
        manifest = json.loads((root / "toy-declarations.json").read_text(encoding="utf-8"))
        inventory = sorted(path.relative_to(root).as_posix()
                           for path in root.rglob("*") if path.is_file())
        return [safe_file(name) for name in
                check.assess(manifest, {"loaded_files": inventory})["overlap"]]


def main():
    report = json.loads(SOURCE.read_text(encoding="utf-8"))
    rows = report["rows"]
    overlaps = [safe_file(name) for name in report["overlap"]]
    if len(overlaps) != 1 or report["score_accepted"] is not False:
        raise ValueError("the source must be the blocked one-overlap checker report")
    # The raw checker JSON only lists loaded files; its other writable file is
    # obtained from the scenario manifest and initial toy-file inventory.
    writable = declared_writable_files()
    loaded = [safe_file(row["file"]) for row in rows if row["loaded_by_evaluator"]]
    with CSV.open(encoding="utf-8", newline="") as stream:
        summary = next(row for row in csv.DictReader(stream) if row["scenario"] == "overlap")
    if len(writable) != int(summary["candidate_writable"]):
        raise ValueError("manifest-derived writable count disagrees with CSV")
    if set(writable) & set(loaded) != set(overlaps):
        raise ValueError("checker rows disagree with its overlap decision")
    if {row["file"] for row in rows if row["writable_by_candidate"]} != set(overlaps):
        raise ValueError("checker writable rows disagree with its overlap decision")

    left_x, right_x = 25, 355
    right_ys = [150 + index * 55 for index in range(len(loaded))]
    if right_ys[-1] + 44 > 420:
        raise ValueError("too many files for this diagram")
    overlap_y = right_ys[loaded.index(overlaps[0])]
    left_ys = [205 + index * 55 for index in range(len(writable))]
    if left_ys[-1] + 44 > 420:
        raise ValueError("too many writable files for this diagram")
    left_overlap_y = left_ys[writable.index(overlaps[0])]
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="640" height="460" viewBox="0 0 640 460" role="img" aria-labelledby="diagram-title diagram-desc">',
        '<title id="diagram-title">Synthetic demo - how an overlap is flagged</title>',
        '<desc id="diagram-desc">The same toy file is declared candidate writable and observed loaded by the toy evaluator, so its provisional score is blocked.</desc>',
        '<rect width="640" height="460" fill="#ffffff"/>',
        '<g font-family="Arial, Helvetica, sans-serif">',
        '<text x="320" y="31" text-anchor="middle" font-size="22" font-weight="bold" fill="#202830">Synthetic demo - how an overlap is flagged</text>',
        '<text text-anchor="middle" font-size="20" font-weight="bold" fill="#202830"><tspan x="155" y="63">Files the candidate</tspan><tspan x="155" dy="22">may write</tspan></text>',
        '<text text-anchor="middle" font-size="20" font-weight="bold" fill="#202830"><tspan x="485" y="63">Files the evaluator</tspan><tspan x="485" dy="22">loaded</tspan></text>',
        '<text x="320" y="125" text-anchor="middle" font-size="21" font-weight="bold" fill="#9D2626">OVERLAP - score blocked</text>',
        f'<line x1="{left_x + 260}" y1="{left_overlap_y + 22}" x2="{right_x}" y2="{overlap_y + 22}" stroke="#B13C3C" stroke-width="4"/>',
    ]
    for name, y in zip(writable, left_ys):
        parts.extend(card(left_x, y, name, name == overlaps[0]))
    for name, y in zip(loaded, right_ys):
        parts.extend(card(right_x, y, name, name == overlaps[0]))
    parts.extend((
        '<text x="320" y="443" text-anchor="middle" font-size="18" fill="#394959">Sources: checker JSON + generated toy manifest</text>',
        '</g>',
        '</svg>',
    ))
    OUTPUT.write_text("\n".join(parts) + "\n", encoding="utf-8", newline="\n")
    print("Saved results/overlap_diagram.svg")


if __name__ == "__main__":
    main()
