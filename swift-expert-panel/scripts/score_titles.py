#!/usr/bin/env python3
"""Score seat.py against area tags in merged PR titles.

Title tags are written by the PR author. The person who tuned the
globs did not write them. This report always exits 0. It is not a
CI check: a month of git history needs more than a depth-1 clone.

    python3 swift-expert-panel/scripts/score_titles.py \
        --checkout <swiftlang/swift> \
        --since 2026-09-06 --until 2026-10-06

Three cuts, all without --stage:

- every changed file
- source files only (paths that do not start with test/)
- those source files plus the PR title as keyword text

Both the source-file cut and the regression corpus's plan-time
number use the merged files. A planner only has triage's guessed
files, so both are an upper bound.

The tag map below is explicit. A title with no mapped tag is left
out. Coarse tags such as [Sema] map to one domain and will miss
when the change is narrower.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

# Lowercase tag, spaces removed, hyphens kept. Unlisted tags are ignored.
TAG_TO_DOMAIN = {
    "embedded": "embedded",
    "wasm": "embedded",
    "wasi": "embedded",
    "silgen": "silgen",
    "irgen": "irgen-abi",
    "tbdgen": "irgen-abi",
    "mangling": "irgen-abi",
    "runtime": "runtime",
    "stdlib": "stdlib",
    "concurrency": "concurrency",
    "sendable": "concurrency",
    "ownership": "ownership",
    "ossa": "ownership",
    "moveonly": "ownership",
    "siloptimizer": "sil-optimizer",
    "sil-optimizer": "sil-optimizer",
    "optimizer": "sil-optimizer",
    "typechecker": "type-system",
    "constraintsystem": "type-system",
    "sema": "type-system",
    "generics": "generics",
    "parser": "parser-diagnostics",
    "parse": "parser-diagnostics",
    "diagnostics": "parser-diagnostics",
    "diagnosticverifier": "parser-diagnostics",
    "lexer": "parser-diagnostics",
    "astgen": "parser-diagnostics",
    "sourcekit": "sourcekit-ide",
    "sourcekit-lsp": "sourcekit-ide",
    "ide": "sourcekit-ide",
    "completion": "sourcekit-ide",
    "refactoring": "sourcekit-ide",
    "clangimporter": "clang-importer",
    "cxx-interop": "clang-importer",
    "cxxinterop": "clang-importer",
    "c++interop": "clang-importer",
    "serialization": "serialization",
    "driver": "serialization",
    "library-evolution": "library-evolution",
    "libraryevolution": "library-evolution",
    "availability": "library-evolution",
    "resilience": "library-evolution",
    "debuginfo": "debug-info",
    "debug-info": "debug-info",
    "dwarf": "debug-info",
    "macros": "macros",
    "macro": "macros",
    "autodiff": "autodiff",
    "distributed": "distributed",
}

_BRACKET = re.compile(r"\[([^\[\]]+)\]")
_COLON = re.compile(r"^([^:]{1,80}):")
_PR = re.compile(r"^Merge pull request #(\d+)\b")
_RECORD = "\x1e"


def norm_tag(tag: str) -> str:
    return re.sub(r"\s+", "", tag.strip().lower())


def domain_for_title(title: str) -> str | None:
    """First mapped area tag in the title, brackets before a colon prefix."""
    tags: list[str] = []
    for match in _BRACKET.finditer(title):
        tags.append(match.group(1))
    colon = _COLON.match(title.strip())
    if colon:
        for part in colon.group(1).split(","):
            part = part.strip()
            if part:
                tags.append(part)
    for tag in tags:
        domain = TAG_TO_DOMAIN.get(norm_tag(tag))
        if domain:
            return domain
    return None


def pr_from_commit(subject: str, body: str) -> tuple[str, str] | None:
    """Return (number, title) for a GitHub merge commit."""
    match = _PR.match(subject.strip())
    if not match:
        return None
    title = ""
    for line in body.splitlines():
        line = line.strip()
        if line:
            title = line
            break
    if not title:
        return None
    return match.group(1), title


def source_paths(paths: list[str]) -> list[str]:
    return [path for path in paths if not path.startswith("test/")]


def _seat_module():
    path = Path(__file__).resolve().parent / "seat.py"
    spec = importlib.util.spec_from_file_location("seat_titles", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def chair_for(seat, table: dict, files: list[str], text: str | None) -> str:
    if not files and not text:
        return "unseated"
    got = seat.seat(files, text or "", None, table)
    return got["chair"]


def score_rows(seat, table: dict, rows: list[dict]) -> dict[str, tuple[int, int]]:
    """rows: {number, title, domain, files}. Return match counts per cut."""
    cuts = {
        "all changed files": (False, False),
        "source files only": (True, False),
        "source files plus title": (True, True),
    }
    hits = {name: 0 for name in cuts}
    for row in rows:
        files = row["files"]
        for name, (sources, use_title) in cuts.items():
            chosen = source_paths(files) if sources else list(files)
            text = row["title"] if use_title else None
            got = chair_for(seat, table, chosen, text)
            if got == row["domain"]:
                hits[name] += 1
    total = len(rows)
    return {name: (hits[name], total) for name in cuts}


def merge_commits(checkout: Path, ref: str, since: str, until: str) -> list[tuple[str, str, str]]:
    out = subprocess.check_output(
        [
            "git",
            "-C",
            str(checkout),
            "log",
            "--first-parent",
            ref,
            "--merges",
            f"--since={since}",
            f"--until={until}",
            f"--pretty=format:%H{_RECORD}%s{_RECORD}%b{_RECORD}",
        ],
        text=True,
    )
    parts = out.split(_RECORD)
    commits = []
    # Each commit is hash, subject, body. A trailing empty piece is normal.
    i = 0
    while i + 2 < len(parts):
        rev, subject, body = parts[i], parts[i + 1], parts[i + 2]
        rev = rev.strip()
        if re.fullmatch(r"[0-9a-f]{7,40}", rev):
            commits.append((rev, subject, body))
            i += 3
        else:
            i += 1
    return commits


def changed_files(checkout: Path, rev: str) -> list[str]:
    out = subprocess.check_output(
        ["git", "-C", str(checkout), "diff", "--name-only", f"{rev}^1", rev],
        text=True,
    )
    return [line.strip() for line in out.splitlines() if line.strip()]


def collect(checkout: Path, ref: str, since: str, until: str) -> tuple[list[dict], int]:
    rows = []
    merges = 0
    for rev, subject, body in merge_commits(checkout, ref, since, until):
        parsed = pr_from_commit(subject, body)
        if not parsed:
            continue
        merges += 1
        number, title = parsed
        domain = domain_for_title(title)
        if not domain:
            continue
        rows.append(
            {
                "number": number,
                "title": title,
                "domain": domain,
                "files": changed_files(checkout, rev),
                "rev": rev,
            }
        )
    return rows, merges


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--ref", default="main")
    parser.add_argument("--since", default="2026-09-06")
    parser.add_argument("--until", default="2026-10-06")
    parser.add_argument(
        "--seats",
        type=Path,
        default=Path(__file__).resolve().parents[2]
        / "knowledge-base/expert-panel/seats.json",
    )
    args = parser.parse_args(argv)
    checkout = args.checkout
    if not (checkout / ".git").exists():
        print(f"score_titles: not a git checkout: {checkout}", file=sys.stderr)
        return 2
    seat = _seat_module()
    table = json.loads(args.seats.read_text(encoding="utf-8"))
    rows, merges = collect(checkout, args.ref, args.since, args.until)
    counts = score_rows(seat, table, rows)
    print(
        f"merges {merges}; tagged {len(rows)};"
        f" {args.since}..{args.until} {args.ref}"
    )
    print(f"{'input':<32} chair matches the tag")
    for name, (ok, total) in counts.items():
        print(f"{name:<32} {ok}/{total}")
    for row in rows:
        got = chair_for(seat, table, row["files"], None)
        if got != row["domain"]:
            title = row["title"].replace("\n", " ")
            print(
                f"miss #{row['number']} tag={row['domain']}"
                f" chair={got} {title[:100]}"
            )
    print("report only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
