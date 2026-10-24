"""Draw a deterministic grouped SVG chart using only the standard library."""

import csv
from html import escape
from pathlib import Path


BASE = Path(__file__).resolve().parent
CSV = BASE / "results" / "overlap_summary.csv"
SVG = BASE / "results" / "overlap_summary.svg"
SERIES = (
    ("candidate_writable", "Candidate writable", "#0072B2"),
    ("evaluator_loaded", "Evaluator loaded", "#E69F00"),
    ("overlap", "Overlap", "#009E73"),
)
DISPLAY_LABELS = {
    "clean": "0 overlaps",
    "overlap": "1 overlap",
    "synthetic_2": "2 overlaps",
    "synthetic_3": "3 overlaps",
}


def main():
    with CSV.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError("CSV has no scenarios")
    if len(rows) != 4 or len({row["scenario"] for row in rows}) != 4:
        raise ValueError("expected four distinct scenarios")
    if {row["scenario"] for row in rows} != set(DISPLAY_LABELS):
        raise ValueError("unknown scenario label")
    values = {key: [int(row[key]) for row in rows] for key, _, _ in SERIES}
    maximum = max(max(numbers) for numbers in values.values())
    ceiling = max(1, maximum + 1)
    left, right, top, bottom = 65, 575, 145, 345
    height = bottom - top
    group = (right - left) / len(rows)
    bar_width, bar_gap = 26, 6
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="640" height="460" viewBox="0 0 640 460" role="img" aria-labelledby="chart-title chart-desc">',
        '<title id="chart-title">Synthetic demo scenarios - not data from my real project</title>',
        '<desc id="chart-desc">Grouped bars show declared candidate writable files, evaluator loaded files, and their overlap for four toy scenarios.</desc>',
        '<rect width="640" height="460" fill="#ffffff"/>',
        '<g font-family="Arial, Helvetica, sans-serif" fill="#222222">',
        '<text x="320" y="31" text-anchor="middle" font-size="22" font-weight="bold">Synthetic demo scenarios</text>',
        '<text x="320" y="56" text-anchor="middle" font-size="22" font-weight="bold">- not data from my real project</text>',
    ]
    for index, (_, label, color) in enumerate(SERIES):
        x = (35, 268, 474)[index]
        parts.append(f'<rect x="{x}" y="86" width="19" height="19" fill="{color}"/>')
        parts.append(f'<text x="{x + 26}" y="103" font-size="18">{escape(label)}</text>')
    for tick in range(ceiling + 1):
        y = bottom - height * tick / ceiling
        parts.append(f'<line x1="{left}" y1="{y:.2f}" x2="{right}" y2="{y:.2f}" stroke="#dddddd"/>')
        parts.append(f'<text x="{left - 12}" y="{y + 6:.2f}" text-anchor="end" font-size="18">{tick}</text>')
    parts.extend((
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" stroke="#333333" stroke-width="2"/>',
        f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="#333333" stroke-width="2"/>',
        '<text x="25" y="245" transform="rotate(-90 25 245)" text-anchor="middle" font-size="18">Number of toy files</text>',
    ))
    for scenario_index, row in enumerate(rows):
        center = left + group * (scenario_index + .5)
        start = center - (3 * bar_width + 2 * bar_gap) / 2
        for series_index, (key, _, color) in enumerate(SERIES):
            value = values[key][scenario_index]
            x = start + series_index * (bar_width + bar_gap)
            y = bottom - height * value / ceiling
            parts.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_width}" height="{bottom - y:.2f}" fill="{color}"/>')
            parts.append(f'<text x="{x + bar_width / 2:.2f}" y="{max(top + 18, y - 7):.2f}" text-anchor="middle" font-size="19" font-weight="bold">{value}</text>')
        label = DISPLAY_LABELS[row["scenario"]]
        parts.append(f'<text x="{center:.2f}" y="372" text-anchor="middle" font-size="18">{escape(label)}</text>')
    parts.extend((
        '<text x="320" y="404" text-anchor="middle" font-size="18">Synthetic scenario</text>',
        '<text x="320" y="442" text-anchor="middle" font-size="18">Source: results/overlap_summary.csv | Chart: make_chart.py</text>',
        '</g>',
        '</svg>',
    ))
    SVG.write_text("\n".join(parts) + "\n", encoding="utf-8", newline="\n")
    print("Saved results/overlap_summary.svg")


if __name__ == "__main__":
    main()
