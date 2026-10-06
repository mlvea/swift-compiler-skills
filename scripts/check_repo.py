#!/usr/bin/env python3
"""Check this repo: prose, links, skill names, and panel briefs."""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME_OK = "swift-local-build-test/references/paths.json"
DOC_SUFFIXES = {".md", ".svg", ".rst", ".txt", ".html"}
TEXT_SUFFIXES = DOC_SUFFIXES | {
    ".py", ".json", ".yml", ".yaml", ".css", ".sh", ".rhai",
}
SKIP_DIRS = {".git", "__pycache__", ".venv", ".pytest_cache"}
HEADINGS = (
    "## Protects",
    "## Plan review",
    "## PR review",
    "## Reject unless",
    "## Evolution",
    "## Forum",
    "## Abstain",
)
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
FENCE = re.compile(r"```.*?```", re.S)


def load_prose():
    path = ROOT / "scripts" / "check-doc-prose.py"
    spec = importlib.util.spec_from_file_location("check_doc_prose", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def iter_files():
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        if path.suffix.lower() in TEXT_SUFFIXES or path.name in {"LICENSE", "AGENTS.md"}:
            yield path


def check_links(path: Path, text: str, problems: list[str]) -> None:
    if path.suffix.lower() != ".md":
        return
    visible = FENCE.sub("", text)
    for raw in LINK.findall(visible):
        target = raw.strip()
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1].strip()
        if not target:
            continue
        target = target.split()[0]
        target = target.split("#", 1)[0]
        if not target or "://" in target or target.startswith("mailto:"):
            continue
        dest = (path.parent / target).resolve()
        try:
            dest.relative_to(ROOT.resolve())
        except ValueError:
            problems.append(f"link leaves repo: {rel(path)} -> {raw}")
            continue
        if not dest.exists():
            problems.append(f"broken link: {rel(path)} -> {target}")


def check_skills(problems: list[str]) -> None:
    for skill in sorted(ROOT.glob("*/SKILL.md")):
        text = skill.read_text(encoding="utf-8")
        if not text.startswith("---"):
            problems.append(f"missing frontmatter: {rel(skill)}")
            continue
        end = text.find("\n---", 3)
        if end < 0:
            problems.append(f"unclosed frontmatter: {rel(skill)}")
            continue
        name = None
        for line in text[3:end].splitlines():
            if line.startswith("name:"):
                name = line.split(":", 1)[1].strip().strip("\"'")
        if name != skill.parent.name:
            problems.append(f"skill name {name!r} != directory {skill.parent.name}")


def check_panel(problems: list[str]) -> None:
    seats = json.loads(
        (ROOT / "knowledge-base/expert-panel/seats.json").read_text(encoding="utf-8")
    )
    ids = [d["id"] for d in seats["domains"]]
    if len(ids) != len(set(ids)):
        problems.append("duplicate domain id in seats.json")
    known = set(ids)
    briefs = {
        p.stem
        for p in (ROOT / "knowledge-base/expert-panel/domains").glob("*.md")
    }
    if known != briefs:
        problems.append(
            "seats.json and domain files differ: " + ", ".join(sorted(known ^ briefs))
        )
    for domain in seats["domains"]:
        for neighbor in domain.get("neighbors", []):
            if neighbor not in known:
                problems.append(f"{domain['id']} neighbor missing: {neighbor}")
        brief = (
            ROOT / "knowledge-base/expert-panel/domains" / f"{domain['id']}.md"
        )
        lines = [line.strip() for line in brief.read_text(encoding="utf-8").splitlines()]
        for heading in HEADINGS:
            if heading not in lines:
                problems.append(f"{rel(brief)} missing {heading}")


def main() -> int:
    prose = load_prose()
    problems: list[str] = []
    for path in iter_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeError:
            problems.append(f"not utf-8: {rel(path)}")
            continue
        name = rel(path)
        if path.suffix.lower() in DOC_SUFFIXES:
            problems.extend(prose.check(name, text))
        if path.suffix.lower() in DOC_SUFFIXES and "./Users" in text:
            problems.append("./Users path in " + name)
        if name != HOME_OK:
            found = sorted(set(prose.HOME_PATH.findall(text)))
            if found:
                problems.append(f"home path in {name}: {', '.join(found)}")
        check_links(path, text, problems)
    check_skills(problems)
    check_panel(problems)
    for path in ROOT.rglob("*.py"):
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except SyntaxError as exc:
            problems.append(f"python {rel(path)}:{exc.lineno}: {exc.msg}")
    if problems:
        print(f"{len(problems)} problem(s)")
        for item in problems:
            print(item)
        return 1
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
