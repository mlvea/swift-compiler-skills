#!/usr/bin/env python3
"""Deterministic expert-panel seating from changed files + optional text.

Reads knowledge-base/expert-panel/seats.json. Prints JSON:
  {chair, seated, scores, reasons, unmatched_files}

Conditional domains sit only on a primary hit.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import sys
from pathlib import Path


def repo_root() -> Path:
    here = Path(__file__).resolve()
    # swift-expert-panel/scripts/seat.py -> repo root
    return here.parents[2]


def load_seats(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


def glob_match(path: str, pattern: str) -> bool:
    path = path.lstrip("./")
    pattern = pattern.lstrip("./")
    if pattern.endswith("/"):
        return path == pattern[:-1] or path.startswith(pattern)
    if "*" in pattern or "?" in pattern or "[" in pattern:
        if fnmatch.fnmatch(path, pattern):
            return True
        # directory-style prefix: lib/Sema/CS* also matches via basename rules
        return fnmatch.fnmatch(os.path.basename(path), os.path.basename(pattern)) and (
            os.path.dirname(path).startswith(os.path.dirname(pattern))
            if os.path.dirname(pattern)
            else True
        )
    return path == pattern or path.startswith(pattern.rstrip("/") + "/")


def specificity(pattern: str) -> int:
    # Longer, more literal patterns win.
    wild = pattern.count("*") + pattern.count("?")
    return len(pattern) * 4 - wild * 8


def keyword_hits(text: str, keywords: list[str]) -> list[str]:
    if not text:
        return []
    low = text.lower()
    hits = []
    for kw in keywords:
        if kw.lower() in low:
            hits.append(kw)
    return hits


def seat(files: list[str], text: str, stage: str | None, table: dict) -> dict:
    domains = table["domains"]
    by_id = {d["id"]: d for d in domains}
    primary_w = table.get("primary_weight", 3)
    adj_w = table.get("adjacent_weight", 1)
    kw_w = table.get("keyword_weight", 1)
    st_w = table.get("stage_weight", 1)
    max_seated = table.get("max_seated", 4)

    scores = {d["id"]: 0 for d in domains}
    reasons: dict[str, list[str]] = {d["id"]: [] for d in domains}
    primary_files: dict[str, list[str]] = {d["id"]: [] for d in domains}
    unmatched: list[str] = []

    for f in files:
        f = f.strip().lstrip("./")
        if not f:
            continue
        best = None
        best_spec = -10**9
        for d in domains:
            for pat in d.get("primary", []):
                if glob_match(f, pat):
                    spec = specificity(pat)
                    if spec >= best_spec:
                        best_spec = spec
                        best = d["id"]
        if best:
            scores[best] += primary_w
            primary_files[best].append(f)
            reasons[best].append(f"primary:{f}")
        else:
            any_adj = False
            for d in domains:
                for pat in d.get("adjacent", []):
                    if glob_match(f, pat):
                        scores[d["id"]] += adj_w
                        reasons[d["id"]].append(f"adjacent:{f}")
                        any_adj = True
                        break
            if not any_adj:
                unmatched.append(f)

    if text:
        for d in domains:
            hits = keyword_hits(text, d.get("keywords", []))
            if hits:
                scores[d["id"]] += kw_w * min(len(hits), 3)
                reasons[d["id"]].append("keywords:" + ",".join(hits[:5]))

    # Stage is a bonus for domains that already matched files/keywords,
    # not a reason to sit every domain that shares a pipeline stage.
    if stage:
        sl = stage.lower()
        for d in domains:
            if scores[d["id"]] <= 0:
                continue
            if sl in [s.lower() for s in d.get("stages", [])]:
                scores[d["id"]] += st_w
                reasons[d["id"]].append(f"stage:{stage}")

    def is_conditional_blocked(did: str) -> bool:
        d = by_id[did]
        return d.get("kind") == "conditional" and not primary_files[did]

    eligible = []
    for d in domains:
        did = d["id"]
        if is_conditional_blocked(did):
            continue
        if scores[did] > 0:
            eligible.append(did)

    if not eligible:
        # Fall back to stage-matched core domains, else type-system.
        for d in domains:
            if d.get("kind") == "core" and stage and stage.lower() in [
                s.lower() for s in d.get("stages", [])
            ]:
                eligible.append(d["id"])
                reasons[d["id"]].append("fallback-stage")
                break
        if not eligible:
            eligible = ["type-system"]
            reasons["type-system"].append("fallback-default")

    eligible.sort(key=lambda i: (-scores[i], i))
    chair = eligible[0]

    seated = [chair]
    neighbors = by_id.get(chair, {}).get("neighbors", [])
    rest = [i for i in eligible if i != chair]
    rest.sort(key=lambda i: (0 if i in neighbors else 1, -scores[i], i))
    for i in rest:
        if len(seated) >= max_seated:
            break
        seated.append(i)

    # If only one domain hit files/keywords, add one neighbor so the usual
    # cross-layer objection can still be raised (Sema vs SILGen, IRGen vs
    # runtime). Prefer a neighbor that lists this stage; else first core
    # neighbor. Conditional neighbors still need a primary hit.
    if len(seated) == 1:
        sl = (stage or "").lower()
        picked = None
        if sl:
            for n in neighbors:
                d = by_id.get(n)
                if not d or is_conditional_blocked(n):
                    continue
                if sl in [s.lower() for s in d.get("stages", [])]:
                    picked = (n, f"neighbor-stage:{stage}")
                    break
        if picked is None:
            for n in neighbors:
                d = by_id.get(n)
                if not d or is_conditional_blocked(n):
                    continue
                if d.get("kind") == "core":
                    picked = (n, "neighbor-core")
                    break
        if picked:
            n, why = picked
            seated.append(n)
            reasons[n].append(why)
            if st_w and why.startswith("neighbor-stage"):
                scores[n] += st_w

    return {
        "chair": chair,
        "seated": seated,
        "scores": {i: scores[i] for i in seated},
        "all_scores": {k: v for k, v in scores.items() if v > 0},
        "reasons": {i: reasons[i] for i in seated},
        "unmatched_files": unmatched,
        "briefs": {
            i: f"knowledge-base/expert-panel/domains/{i}.md" for i in seated
        },
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--seats",
        default=str(repo_root() / "knowledge-base/expert-panel/seats.json"),
    )
    p.add_argument("--stage", default="")
    p.add_argument(
        "--text-file",
        default="",
        help="Optional plan/PR body whose keywords influence seating",
    )
    p.add_argument(
        "--text",
        default="",
        help="Optional plan/PR body as a string (alternative to --text-file)",
    )
    p.add_argument(
        "files",
        nargs="*",
        help="Changed paths relative to the swift checkout",
    )
    args = p.parse_args()

    files = list(args.files)
    if not sys.stdin.isatty() and not files:
        files.extend(line.strip() for line in sys.stdin if line.strip())

    text = args.text or ""
    if args.text_file:
        text = Path(args.text_file).read_text(errors="replace")

    table = load_seats(Path(args.seats))
    result = seat(files, text, args.stage or None, table)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
