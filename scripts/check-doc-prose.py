#!/usr/bin/env python3
"""Deny document writes that leak home paths or filler prose.

Reads a tool-call JSON envelope on stdin. Exit 0 with
{"decision":"allow"} or {"decision":"deny","reason":"..."}.
"""
from __future__ import annotations

import json
import re
import sys

DOC_SUFFIXES = (".md", ".svg", ".rst", ".txt", ".html")
HOME_PATH = re.compile(r"/(?:Users|home)/[A-Za-z0-9._-]+/")
EM_DASH = re.compile(r"[\u2013\u2014]")
# Filename is allowed. Bare "gate/gated/gates" in prose is not.
GATE = re.compile(r"\bgates?\b|\bgated\b", re.I)
# evolution-gate is the panel document. target/flag/feature-gated are
# compiler terms. The old journal label is still accepted.
GATE_OK = re.compile(
    r"evolution-gate|(?:target|flag|feature)-gated|\bgates?:",
    re.I,
)

FILLER = [
    (re.compile(r"\bdelve[sd]?\b", re.I), "delve"),
    (re.compile(r"\bleverage[sd]?\b", re.I), "leverage"),
    (re.compile(r"\butili[sz]e[sd]?\b", re.I), "utilize"),
    (re.compile(r"\bwhilst\b", re.I), "whilst"),
    (re.compile(r"\bamongst\b", re.I), "amongst"),
    (re.compile(r"\baforementioned\b", re.I), "aforementioned"),
    (re.compile(r"\btapestry\b", re.I), "tapestry"),
    (re.compile(r"\btestament\b", re.I), "testament"),
    (re.compile(r"\bnestled\b", re.I), "nestled"),
    (re.compile(r"\bholistic\b", re.I), "holistic"),
    (re.compile(r"\bseamless\b", re.I), "seamless"),
    (re.compile(r"\bpivotal\b", re.I), "pivotal"),
    (re.compile(r"\bfurthermore\b", re.I), "furthermore"),
    (re.compile(r"\bmoreover\b", re.I), "moreover"),
    (re.compile(r"\bin order to\b", re.I), "in order to"),
    (re.compile(r"\bit is important to note\b", re.I), "it is important to note"),
    (re.compile(r"\bat its core\b", re.I), "at its core"),
    (re.compile(r"\bdeep dive\b", re.I), "deep dive"),
]


def _path_ok_for_home(path: str) -> bool:
    p = path.replace("\\", "/")
    return p.endswith("swift-local-build-test/references/paths.json")


def _is_doc(path: str) -> bool:
    p = path.lower().replace("\\", "/")
    return p.endswith(DOC_SUFFIXES)


def _skip_file(path: str) -> bool:
    p = path.replace("\\", "/").lower()
    return p.endswith(
        ("agents.md", "prose.md", "check-doc-prose.py")
    )


def _tool_path_and_text(payload: dict) -> tuple[str, str]:
    inp = payload.get("toolInput") or payload.get("tool_input") or {}
    if not isinstance(inp, dict):
        inp = {}
    path = (
        inp.get("file_path")
        or inp.get("path")
        or inp.get("target_file")
        or ""
    )
    text = (
        inp.get("new_string")
        or inp.get("content")
        or inp.get("contents")
        or inp.get("new_contents")
        or ""
    )
    if not isinstance(path, str):
        path = str(path)
    if not isinstance(text, str):
        text = str(text)
    return path, text


def _gate_hits(text: str) -> list[str]:
    hits = []
    for m in GATE.finditer(text):
        lo = max(0, m.start() - 24)
        hi = min(len(text), m.end() + 24)
        if GATE_OK.search(text[lo:hi]):
            continue
        hits.append(m.group())
    return hits


def check(path: str, text: str) -> list[str]:
    if _skip_file(path) or not _is_doc(path) or not text:
        return []
    reasons = []
    if not _path_ok_for_home(path):
        found = sorted(set(HOME_PATH.findall(text)))
        if found:
            reasons.append(
                "home-directory path "
                + ", ".join(found)
                + " in "
                + path
                + ". Name the checkout (swiftlang/swift) or use $B/$LIT/$FE from "
                "swift-local-build-test/references/paths.json."
            )
    dashes = EM_DASH.findall(text)
    if dashes:
        reasons.append(
            "em/en dash in "
            + path
            + ". Use a period, comma, colon, or hyphen."
        )
    gates = _gate_hits(text)
    if gates:
        reasons.append(
            "filler word "
            + ", ".join(sorted(set(gates)))
            + " in "
            + path
            + ". Say the actual thing (required review, check). "
            "The filename evolution-gate.md is fine."
        )
    for rx, name in FILLER:
        if rx.search(text):
            reasons.append(
                "filler word '"
                + name
                + "' in "
                + path
                + ". Write the sentence without it."
            )
    return reasons


def main() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        print(json.dumps({"decision": "allow"}))
        return 0
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        print(json.dumps({"decision": "allow"}))
        return 0
    path, text = _tool_path_and_text(payload)
    reasons = check(path, text)
    if reasons:
        print(
            json.dumps(
                {
                    "decision": "deny",
                    "reason": "Document prose: " + " ".join(reasons),
                }
            )
        )
        return 0
    print(json.dumps({"decision": "allow"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
