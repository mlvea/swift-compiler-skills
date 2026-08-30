#!/usr/bin/env python3
"""Fail if seats.json primary/adjacent globs or official docs are missing
from the swift checkout. Living-knowledge gate.

  python3 swift-expert-panel/scripts/probe_globs.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_json(path: Path):
    with path.open() as f:
        return json.load(f)


def glob_exists(checkout: Path, pattern: str) -> bool:
    pattern = pattern.lstrip("./")
    wild = any(c in pattern for c in "*?[")
    if wild:
        return any(checkout.glob(pattern.rstrip("/")))
    if pattern.endswith("/"):
        return (checkout / pattern[:-1]).is_dir()
    p = checkout / pattern
    return p.is_file() or p.is_dir()


def main() -> int:
    root = repo_root()
    paths = load_json(root / "swift-local-build-test/references/paths.json")
    checkout = Path(paths["swift_checkout"])
    if not checkout.is_dir():
        print(f"missing swift_checkout: {checkout}", file=sys.stderr)
        return 2
    seats = load_json(root / "knowledge-base/expert-panel/seats.json")
    missing = []
    for d in seats["domains"]:
        for kind in ("primary", "adjacent"):
            for pat in d.get(kind, []):
                if not glob_exists(checkout, pat):
                    missing.append(f"{d['id']}.{kind}: {pat}")
    docs_index = root / "knowledge-base/expert-panel/official-docs.md"
    if docs_index.is_file():
        for line in docs_index.read_text().splitlines():
            line = line.strip()
            if line.startswith("- `docs/") and line.endswith("`"):
                rel = line[3:-1]
                if not (checkout / rel).is_file():
                    missing.append(f"official-doc: {rel}")
    for name, sib in (paths.get("siblings") or {}).items():
        if not Path(sib).is_dir():
            missing.append(f"sibling:{name}: {sib}")
    if missing:
        print("missing on", checkout)
        for m in missing:
            print(" ", m)
        return 1
    n = sum(len(d.get("primary", [])) + len(d.get("adjacent", [])) for d in seats["domains"])
    print(f"OK {n} globs under {checkout}; siblings present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
