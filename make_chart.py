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


def main():
    with CSV.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError("CSV has no scenarios")
    if len(rows) != 4 or len({row["scenario"] for row in rows}) != 4:
        raise ValueError("expected four distinct scenarios")
    values = {key: [int(row[key]) for row in rows] for key, _, _ in SERIES}
    maximum = max(max(numbers) for numbers in values.values())
    ceiling = max(1, maximum + 1)
    left, right, top, bottom = 90, 750, 155, 510
    height = bottom - top
    group = (right - left) / len(rows)
    bar_width, bar_gap = 36, 8
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="780" height="650" viewBox="0 0 780 650" role="img" aria-labelledby="chart-title chart-desc">',
        '<title id="chart-title">Synthetic demo scenarios - not data from my real project</title>',
        '<desc id="chart-desc">Grouped bars show declared candidate writable files, evaluator loaded files, and their overlap for four toy scenarios.</desc>',
        '<rect width="780" height="650" fill="#ffffff"/>',
        '<g font-family="Arial, Helvetica, sans-serif" fill="#222222">',
        '<text x="390" y="38" text-anchor="middle" font-size="24" font-weight="bold">Synthetic demo scenarios - not data from my real project</text>',
        '<text x="390" y="74" text-anchor="middle" font-size="20">Toy declarations and observed loads</text>',
    ]
    for index, (_, label, color) in enumerate(SERIES):
        x = 88 + index * 227
        parts.append(f'<rect x="{x}" y="98" width="20" height="20" fill="{color}"/>')
        parts.append(f'<text x="{x + 28}" y="115" font-size="19">{escape(label)}</text>')
    for tick in range(ceiling + 1):
        y = bottom - height * tick / ceiling
        parts.append(f'<line x1="{left}" y1="{y:.2f}" x2="{right}" y2="{y:.2f}" stroke="#dddddd"/>')
        parts.append(f'<text x="{left - 15}" y="{y + 7:.2f}" text-anchor="end" font-size="20">{tick}</text>')
    parts.extend((
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" stroke="#333333" stroke-width="2"/>',
        f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="#333333" stroke-width="2"/>',
        '<text x="28" y="335" transform="rotate(-90 28 335)" text-anchor="middle" font-size="21">Number of toy files</text>',
    ))
    for scenario_index, row in enumerate(rows):
        center = left + group * (scenario_index + .5)
        start = center - (3 * bar_width + 2 * bar_gap) / 2
        for series_index, (key, _, color) in enumerate(SERIES):
            value = values[key][scenario_index]
            x = start + series_index * (bar_width + bar_gap)
            y = bottom - height * value / ceiling
            parts.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_width}" height="{bottom - y:.2f}" fill="{color}"/>')
            parts.append(f'<text x="{x + bar_width / 2:.2f}" y="{max(top + 18, y - 9):.2f}" text-anchor="middle" font-size="21" font-weight="bold">{value}</text>')
        parts.append(f'<text x="{center:.2f}" y="540" text-anchor="middle" font-size="20">{escape(row["scenario"])}</text>')
    parts.extend((
        '<text x="420" y="580" text-anchor="middle" font-size="21">Synthetic scenario</text>',
        '<text x="390" y="621" text-anchor="middle" font-size="18">Source: results/overlap_summary.csv | Chart script: make_chart.py</text>',
        '</g>',
        '</svg>',
    ))
    SVG.write_text("\n".join(parts) + "\n", encoding="utf-8", newline="\n")
    print("Saved results/overlap_summary.svg")


if __name__ == "__main__":
    main()
