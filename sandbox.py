"""Fake files only; candidate writability is declared, never inferred from ACLs."""
import json
from pathlib import Path
import tempfile


def create(scenario):
    """Return a managed temp sandbox inside this demo folder."""
    extras = {
        "clean": [],
        "overlap": ["shared/helper_b.py"],
        "synthetic_2": ["shared/helper_a.py", "shared/helper_b.py"],
        "synthetic_3": ["shared/helper_a.py", "shared/helper_b.py", "toy_rules.json"],
    }
    if scenario not in extras:
        raise ValueError("unknown scenario")
    temporary = tempfile.TemporaryDirectory(prefix="toy-", dir=Path(__file__).parent)
    root = Path(temporary.name)
    files = {
        "candidate_area/submission.txt": "FAKE SUBMISSION\n",
        "shared/__init__.py": "",
        "shared/helper_a.py": "def value():\n    return 2\n",
        "shared/helper_b.py": "def value():\n    return 3\n",
        "toy_rules.json": '{"offset": 5}',
        "toy_grader.py": (
            "import json\nfrom shared import helper_a, helper_b\n"
            "with open('toy_rules.json', encoding='utf-8') as stream:\n"
            "    config = json.load(stream)\n"
            "print('Toy provisional score:', helper_a.value() + "
            "helper_b.value() + config['offset'])\n"
        ),
    }
    for name, contents in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8")
    writable = ["candidate_area/"]
    writable.extend(extras[scenario])
    (root / "toy-declarations.json").write_text(
        json.dumps({"candidate_writable": writable}), encoding="utf-8"
    )
    return temporary
