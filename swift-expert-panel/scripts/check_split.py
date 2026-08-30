#!/usr/bin/env python3
"""Fail if D_test IDs leak into training sinks, splits overlap, or a harvest
JSON contains a D_test id.

  python3 swift-expert-panel/scripts/check_split.py
  python3 swift-expert-panel/scripts/check_split.py --harvest data/resolved-issues-<date>/*.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_ids(path: Path) -> set[int]:
    data = json.loads(path.read_text())
    ids: set[int] = set()
    for item in data.get("items", []):
        ids.add(int(item["id"]))
        for c in item.get("cluster") or []:
            ids.add(int(c))
    return ids


def ids_in_text(text: str) -> set[int]:
    return {int(m) for m in re.findall(r"#(\d{4,6})\b", text)} | {
        int(m) for m in re.findall(r"\b(?:swift#|PR |issue )(\d{4,6})\b", text, re.I)
    }


def ids_in_json_obj(obj: object) -> set[int]:
    found: set[int] = set()

    def walk(node: object) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                if k in {"id", "number"} and isinstance(v, int) and 1000 <= v <= 999999:
                    found.add(v)
                elif k == "cluster" and isinstance(v, list):
                    for x in v:
                        if isinstance(x, int) and 1000 <= x <= 999999:
                            found.add(x)
                else:
                    walk(v)
        elif isinstance(node, list):
            for x in node:
                walk(x)

    walk(obj)
    return found


def ids_in_path(path: Path) -> set[int]:
    text = path.read_text(errors="replace")
    found = ids_in_text(text)
    if path.suffix == ".json":
        try:
            found |= ids_in_json_obj(json.loads(text))
        except json.JSONDecodeError:
            found |= {int(m) for m in re.findall(r'"(?:id|number)"\s*:\s*(\d{4,6})', text)}
    return found


def iter_repo_text(root: Path, splits: Path):
    skip_parts = {".git"}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if skip_parts & set(path.parts):
            continue
        if splits == path.parent or splits in path.parents:
            continue
        if path.suffix.lower() not in {".md", ".json", ".yml", ".yaml", ".svg"}:
            continue
        yield path


def harvest_ids(path: Path) -> set[int]:
    data = json.loads(path.read_text())
    return ids_in_json_obj(data)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--harvest",
        nargs="+",
        default=[],
        help="GitHub search JSON (or similar). Fail if any D_test id is present.",
    )
    args = p.parse_args()

    root = repo_root()
    splits = root / "optimization/splits"
    d_tr = load_ids(splits / "d_tr.json")
    d_sel = load_ids(splits / "d_sel.json")
    d_test = load_ids(splits / "d_test.json")
    fail = 0
    if d_tr & d_sel:
        print("overlap D_tr ∩ D_sel", sorted(d_tr & d_sel))
        fail = 1
    if d_tr & d_test:
        print("overlap D_tr ∩ D_test", sorted(d_tr & d_test))
        fail = 1
    if d_sel & d_test:
        print("overlap D_sel ∩ D_test", sorted(d_sel & d_test))
        fail = 1
    if len(d_test) < 30:
        print(f"D_test has {len(d_test)} ids; need ≥30 unique")
        fail = 1

    for path in iter_repo_text(root, splits):
        found = ids_in_path(path)
        leaked = found & d_test
        if leaked:
            print(f"D_test ids in {path.relative_to(root)}: {sorted(leaked)}")
            fail = 1
        if path.name.startswith("scorecard"):
            sel_hit = found & d_sel
            if sel_hit:
                print(f"D_sel ids in scorecard {path.name}: {sorted(sel_hit)}")
                fail = 1

    for raw in args.harvest:
        hpath = Path(raw)
        if not hpath.is_file():
            print(f"harvest file missing: {hpath}")
            fail = 1
            continue
        leaked = harvest_ids(hpath) & d_test
        if leaked:
            print(f"D_test ids in harvest {hpath}: {sorted(leaked)}")
            fail = 1

    print(
        f"D_tr={len(d_tr)} D_sel={len(d_sel)} D_test={len(d_test)}"
        + (" OK" if fail == 0 else " FAIL")
    )
    return fail


if __name__ == "__main__":
    sys.exit(main())
