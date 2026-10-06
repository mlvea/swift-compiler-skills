#!/usr/bin/env python3
"""Create issues/explainers/<N>/ under the case-notes checkout.

wiki_checkout is optional. Pass --wiki, or set it in paths.json to a
real directory. An empty value or the example placeholder does not
write into the current directory.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


def skills_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_paths(path: Path) -> dict:
    if not path.is_file():
        print(
            "new_explainer: missing paths.json. Copy paths.example.json"
            " to paths.json, or pass --wiki.",
            file=sys.stderr,
        )
        raise SystemExit(1)
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def wiki_dir(table: dict) -> tuple[Path, str]:
    raw = str(table.get("wiki_checkout") or "").strip()
    rel = str(table.get("explainers_rel") or "issues/explainers")
    if not raw or "/path/to" in raw or raw in {".", ".."}:
        print(
            "new_explainer: wiki_checkout is unset or still the example"
            " placeholder. Pass --wiki DIR, or set wiki_checkout to a"
            " real directory. Refusing to write into the current directory.",
            file=sys.stderr,
        )
        raise SystemExit(1)
    return Path(raw), rel


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--issue", required=True, help="GitHub issue number")
    ap.add_argument(
        "--wiki",
        default="",
        help="Case-notes directory. Tests pass a temporary directory.",
    )
    ap.add_argument(
        "--paths",
        default="",
        help="paths JSON. Default: references/paths.json. Tests pass a file.",
    )
    args = ap.parse_args()
    n = str(args.issue).lstrip("#")
    if not n.isdigit():
        print("issue must be a number", file=sys.stderr)
        return 2

    if args.wiki:
        raw_wiki = str(args.wiki).strip()
        if raw_wiki in {".", ".."} or "/path/to" in raw_wiki:
            print(
                "new_explainer: --wiki must be a real directory, not the"
                " current directory or the example placeholder.",
                file=sys.stderr,
            )
            return 1
        wiki = Path(raw_wiki)
        rel = "issues/explainers"
    else:
        path = (
            Path(args.paths)
            if args.paths
            else skills_root()
            / "swift-local-build-test"
            / "references"
            / "paths.json"
        )
        wiki, rel = wiki_dir(load_paths(path))
    dest = wiki / rel / n
    dest.mkdir(parents=True, exist_ok=True)

    refs = skills_root() / "swift-issue-explainer" / "references"
    css_src = refs / "explainer.css"
    shell = refs / "shell.html"
    shutil.copy2(css_src, dest / "explainer.css")
    index = dest / "index.html"
    if not index.exists():
        page = shell.read_text(encoding="utf-8")
        page = page.replace("swiftlang/swift#N", f"swiftlang/swift#{n}")
        index.write_text(page, encoding="utf-8")

    print(str(dest / "index.html"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
