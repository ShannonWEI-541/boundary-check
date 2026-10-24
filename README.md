# boundary-check

A small demo written with AI coding tools (Codex) under my direction; I specified the design and ran the checks.

boundary-check is a Python toy that compares declared candidate-writable paths with files a cooperative toy grader opens or imports. It shows whether their intersection would allow a candidate to influence the code or data used for a provisional score.

## Why it matters

An evaluated system must not be able to change what its evaluator loads. A score is blocked when a declared writable path overlaps an observed load.

## Run it

```text
python -B demo.py
python -B -m unittest discover -s tests -v
```

Selected lines from the demo's actual output:

```text
=== clean ===
Toy provisional score: 10
shared/helper_b.py | false | true | -
checker exit: 0
Score accepted
=== overlap ===
Toy provisional score: 10
shared/helper_b.py | true | true | OVERLAP
checker exit: 1
Score blocked
```

The complete captured output is in `results/demo-output.txt`.

## How it works

- The demo creates two temporary toy folders inside this repository.
- A declaration lists paths the candidate is assumed able to write.
- Python audit events record existing toy files opened or imported by the cooperative grader.
- The checker compares normalized relative paths and blocks the provisional score on overlap.

## Chart

The chart compares candidate writable files, evaluator loaded files, and their overlap across four scenarios.
All chart data comes from synthetic toy sandboxes, not a real project.
Regenerate with `python -B make_chart_data.py` and `python -B make_chart.py`.

## Limits

- Writability is declared; the tool does not inspect real ACL permissions.
- It covers a toy sandbox and cooperative Python code only.
- Tested on Windows 10 (build 19044) with Python 3.14.7.
- This is not a security tool or proof of evaluator isolation.

## Not included

My private research project, evaluation data, and all real paths and file names are intentionally excluded.
