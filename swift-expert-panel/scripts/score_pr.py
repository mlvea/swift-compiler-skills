#!/usr/bin/env python3
"""Offline seating replay for the panel scorecard.

Does not spawn ballots. Compares seat.py chair to corpus expected_chair.

  python3 swift-expert-panel/scripts/score_pr.py --corpus
  python3 swift-expert-panel/scripts/score_pr.py --stage sil-opts -- file.cpp
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def seat_cmd() -> Path:
    return Path(__file__).resolve().parent / "seat.py"


def run_seat(files: list[str], stage: str | None, text: str | None) -> dict:
    cmd = [sys.executable, str(seat_cmd())]
    if stage:
        cmd += ["--stage", stage]
    if text:
        cmd += ["--text", text]
    cmd += ["--"] + files
    out = subprocess.check_output(cmd, text=True)
    return json.loads(out)


def load_corpus() -> dict:
    path = repo_root() / "knowledge-base/expert-panel/scorecard-corpus.json"
    with path.open() as f:
        return json.load(f)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--corpus", action="store_true")
    p.add_argument("--stage")
    p.add_argument("--text")
    p.add_argument("files", nargs="*")
    args = p.parse_args()

    if args.corpus:
        data = load_corpus()
        failed = 0
        for case in data["cases"]:
            got = run_seat(case["files"], case.get("stage"), case.get("text"))
            exp = case["expected_chair"]
            ok = got["chair"] == exp
            if not ok:
                failed += 1
            print(
                f"{'OK' if ok else 'FAIL'} {case['id']} chair={got['chair']}"
                f" expected={exp} seated={got['seated']}"
            )
        print(f"{len(data['cases']) - failed}/{len(data['cases'])} chairs match")
        return 1 if failed else 0

    if not args.files:
        print("need --corpus or files", file=sys.stderr)
        return 2
    got = run_seat(args.files, args.stage, args.text)
    json.dump(got, sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
