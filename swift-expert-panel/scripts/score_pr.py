#!/usr/bin/env python3
"""Seating replay for the panel corpora.

--corpus scores scorecard-corpus.json. That file is the regression
corpus: rules and globs were edited from its misses. Exit 1 on a
chair miss.

--sources-only scores the same corpus with source files only (no
test/ paths, no stage, no keyword text). It prints the plan-time
report and exits 0 even when chairs differ.

--heldout scores heldout-corpus.json and always exits 0. A miss is
a report. It is not a reason to edit a glob. Cases belong there
only when they were scored before any edit they motivated.

  python3 swift-expert-panel/scripts/score_pr.py --corpus
  python3 swift-expert-panel/scripts/score_pr.py --sources-only
  python3 swift-expert-panel/scripts/score_pr.py --heldout
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


def source_files(files: list[str]) -> list[str]:
    return [path for path in files if not path.startswith("test/")]


def score(cases: list[dict], sources_only: bool) -> tuple[int, int]:
    failed = 0
    for case in cases:
        files = case["files"]
        stage = case.get("stage")
        text = case.get("text")
        if sources_only:
            files = source_files(files)
            stage = None
            text = None
        got = run_seat(files, stage, text)
        exp = case["expected_chair"]
        ok = got["chair"] == exp
        if not ok:
            failed += 1
        print(
            f"{'OK' if ok else 'FAIL'} {case['id']} chair={got['chair']}"
            f" expected={exp} seated={got['seated']}"
        )
    return len(cases) - failed, len(cases)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", action="store_true")
    parser.add_argument("--heldout", action="store_true")
    parser.add_argument(
        "--heldout-file",
        type=Path,
        default=None,
        help="Score this JSON instead of heldout-corpus.json. Report only.",
    )
    parser.add_argument(
        "--sources-only",
        action="store_true",
        help="Regression corpus, source files only. Report; exit 0.",
    )
    parser.add_argument("--stage")
    parser.add_argument("--text")
    parser.add_argument("files", nargs="*")
    args = parser.parse_args()

    if args.corpus and (args.heldout or args.heldout_file):
        print("pick one of --corpus or --heldout", file=sys.stderr)
        return 2

    root = repo_root()
    if args.heldout or args.heldout_file:
        path = args.heldout_file or (
            root / "knowledge-base/expert-panel/heldout-corpus.json"
        )
        data = json.loads(path.read_text(encoding="utf-8"))
        cases = data["cases"]
        if not cases:
            print("held-out: 0 cases")
            return 0
        ok, total = score(cases, False)
        print(f"{ok}/{total} held-out chairs match (report only)")
        return 0

    if args.corpus or args.sources_only:
        data = json.loads(
            (
                root / "knowledge-base/expert-panel/scorecard-corpus.json"
            ).read_text(encoding="utf-8")
        )
        ok, total = score(data["cases"], args.sources_only)
        if args.sources_only:
            print(
                f"sources-only {ok}/{total}"
                " (plan-time report; regression check is --corpus)"
            )
            return 0
        print(f"{ok}/{total} chairs match")
        return 1 if ok != total else 0

    if not args.files:
        print("need --corpus, --sources-only, --heldout, or files", file=sys.stderr)
        return 2
    got = run_seat(args.files, args.stage, args.text)
    json.dump(got, sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
