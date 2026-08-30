#!/usr/bin/env python3
"""Fail if D_test / D_sel IDs leak into training sinks, or if splits overlap.

  python3 swift-expert-panel/scripts/check_split.py
"""
from __future__ import annotations

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


def main() -> int:
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

    sinks = [
        root / "knowledge-base/expert-panel/scorecard-corpus.json",
        root / "knowledge-base/expert-panel/scorecard.md",
        root / "knowledge-base/resolved-issue-patterns.md",
        root / "docs/validation.md",
        root / "optimization/edit-log.md",
    ]
    for sink in sinks:
        text = sink.read_text(errors="replace")
        leaked = ids_in_text(text) & d_test
        if leaked:
            print(f"D_test ids in training sink {sink.relative_to(root)}: {sorted(leaked)}")
            fail = 1
        sel_in_scorecard = set()
        if sink.name.startswith("scorecard"):
            sel_in_scorecard = ids_in_text(text) & d_sel
            if sel_in_scorecard:
                print(f"D_sel ids in scorecard {sink.name}: {sorted(sel_in_scorecard)}")
                fail = 1
    print(
        f"D_tr={len(d_tr)} D_sel={len(d_sel)} D_test={len(d_test)}"
        + (" OK" if fail == 0 else " FAIL")
    )
    return fail


if __name__ == "__main__":
    sys.exit(main())
