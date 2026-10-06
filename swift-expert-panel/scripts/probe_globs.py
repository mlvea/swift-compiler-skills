#!/usr/bin/env python3
"""Fail if seats.json globs or official docs are missing from a swift checkout.

  python3 swift-expert-panel/scripts/probe_globs.py
  python3 swift-expert-panel/scripts/probe_globs.py --checkout /path/to/swift

The default reads swift_checkout and siblings from paths.json.
--checkout skips sibling checks, so a sparse swiftlang/swift clone
is enough. The weekly workflow uses that form.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def glob_exists(checkout: Path, pattern: str) -> bool:
    pattern = pattern.lstrip("./")
    wild = any(char in pattern for char in "*?[")
    if wild:
        return any(checkout.glob(pattern.rstrip("/")))
    if pattern.endswith("/"):
        return (checkout / pattern[:-1]).is_dir()
    path = checkout / pattern
    return path.is_file() or path.is_dir()


def main() -> int:
    root = repo_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--checkout",
        type=Path,
        help="swift checkout. Skips sibling-repo checks.",
    )
    parser.add_argument("--paths", type=Path)
    args = parser.parse_args()

    siblings: dict = {}
    if args.checkout:
        checkout = args.checkout
    else:
        path = args.paths or (
            root / "swift-local-build-test/references/paths.json"
        )
        if not path.is_file():
            example = root / "swift-local-build-test/references/paths.example.json"
            print(
                f"probe_globs: missing {path}. Copy {example} to paths.json,"
                " or pass --checkout.",
                file=sys.stderr,
            )
            return 2
        paths = load_json(path)
        checkout = Path(paths["swift_checkout"])
        siblings = paths.get("siblings") or {}

    if not checkout.is_dir():
        print(f"missing swift checkout: {checkout}", file=sys.stderr)
        return 2

    seats = load_json(root / "knowledge-base/expert-panel/seats.json")
    missing = []
    for domain in seats["domains"]:
        for kind in ("primary", "adjacent"):
            for pattern in domain.get(kind, []):
                if not glob_exists(checkout, pattern):
                    missing.append(f"{domain['id']}.{kind}: {pattern}")
    docs_index = root / "knowledge-base/expert-panel/official-docs.md"
    if docs_index.is_file():
        for line in docs_index.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("- `docs/") and line.endswith("`"):
                rel = line[3:-1]
                if not (checkout / rel).is_file():
                    missing.append(f"official-doc: {rel}")
    for name, sibling in siblings.items():
        if not Path(sibling).is_dir():
            missing.append(f"sibling:{name}: {sibling}")
    if missing:
        print("missing on", checkout)
        for item in missing:
            print(" ", item)
        return 1
    count = sum(
        len(domain.get("primary", [])) + len(domain.get("adjacent", []))
        for domain in seats["domains"]
    )
    tail = "siblings skipped" if args.checkout else "siblings present"
    print(f"OK {count} globs under {checkout}; {tail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
