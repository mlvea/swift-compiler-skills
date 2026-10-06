#!/usr/bin/env python3
"""Print shell exports for the Swift build named in paths.json.

The script locates references/paths.json from its own file, so the
working directory does not matter. Copy references/paths.example.json
to paths.json first. paths.json is gitignored.

    eval "$(python3 swift-local-build-test/scripts/export-env.py)"

$SUFFIX is the platform name in the build directory
(swift-macosx-arm64 -> macosx-arm64). $CFG is
$B/test-$SUFFIX/lit.site.cfg. Set lit_platform only when the
directory is not named swift-<os>-<arch>.
"""
from __future__ import annotations

import argparse
import json
import platform
import re
import shlex
import sys
from pathlib import Path

# swift-macosx-arm64, swift-linux-aarch64, swift-macosx-x86_64.
_PRODUCT = re.compile(r"^swift-(.+-.+)$")


def host_platform_suffix() -> str:
    """Swift's product suffix for this host. Linux arm is aarch64."""
    machine = platform.machine().lower()
    if machine == "amd64":
        machine = "x86_64"
    system = sys.platform
    if system == "darwin":
        arch = "arm64" if machine in ("arm64", "aarch64") else machine
        return f"macosx-{arch}"
    if system.startswith("linux"):
        arch = "aarch64" if machine == "arm64" else machine
        return f"linux-{arch}"
    if system.startswith("freebsd"):
        return f"freebsd-{machine}"
    if system.startswith("win"):
        return f"windows-{machine}"
    return f"{system}-{machine}"


def platform_suffix(build_swift: str, override: str | None = None) -> str:
    if override and override.strip():
        return override.strip()
    match = _PRODUCT.match(Path(build_swift).name)
    if match:
        return match.group(1)
    return host_platform_suffix()


def lit_site_cfg(build_swift: str, override: str | None = None) -> str:
    suffix = platform_suffix(build_swift, override)
    return str(Path(build_swift) / f"test-{suffix}" / "lit.site.cfg")


# An unedited paths.example.json still contains these. Exporting them
# makes ninja and lit fail later with a path that looks almost real.
_PLACEHOLDER = "/path/to"


def _placeholder_keys(data: dict) -> list[str]:
    bad: list[str] = []

    def check(key: str, value: object) -> None:
        if isinstance(value, str) and _PLACEHOLDER in value:
            bad.append(key)

    for key, value in data.items():
        if key in ("notes", "explainers_rel", "skills_kb", "lit_platform"):
            continue
        if key == "siblings" and isinstance(value, dict):
            for name, path in value.items():
                check(f"siblings.{name}", path)
            continue
        if key == "wiki_checkout" and not str(value or "").strip():
            continue
        check(key, value)
    return bad


def exports_from(data: dict) -> dict[str, str]:
    placeholders = _placeholder_keys(data)
    if placeholders:
        joined = ", ".join(placeholders)
        raise ValueError(
            "still the paths.example.json placeholder: "
            f"{joined}. Edit paths.json. wiki_checkout may be \"\"."
        )
    for key in ("build_swift", "build_llvm", "swift_checkout"):
        if key not in data:
            raise KeyError(key)
        if not str(data[key]).strip():
            raise ValueError(f"{key} is empty. Edit paths.json.")
    build = data["build_swift"]
    llvm = data["build_llvm"]
    override = data.get("lit_platform") or None
    suffix = platform_suffix(build, override)
    out = {
        "B": build,
        "LLVM": llvm,
        "LIT": str(Path(llvm) / "bin" / "llvm-lit"),
        "FE": str(Path(build) / "bin" / "swift-frontend"),
        "SO": str(Path(build) / "bin" / "sil-opt"),
        "IDE": str(Path(build) / "bin" / "swift-ide-test"),
        "SUFFIX": suffix,
        "CFG": lit_site_cfg(build, override),
        "SWIFT": data["swift_checkout"],
    }
    wiki = str(data.get("wiki_checkout") or "").strip()
    if wiki:
        out["WIKI"] = wiki
    if data.get("build_swift_secondary"):
        out["B_SECONDARY"] = data["build_swift_secondary"]
    if data.get("toolchains_dir"):
        out["TOOLCHAINS"] = data["toolchains_dir"]
    return out


def main(argv: list[str] | None = None) -> int:
    skill = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--paths",
        type=Path,
        help="paths JSON. Default: references/paths.json next to this skill.",
    )
    args = parser.parse_args(argv)
    path = args.paths or (skill / "references" / "paths.json")
    example = skill / "references" / "paths.example.json"
    if not path.is_file():
        print(
            f"export-env: missing {path}. Copy {example} to paths.json and edit it.",
            file=sys.stderr,
        )
        return 1
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"export-env: {exc}", file=sys.stderr)
        return 1
    try:
        exports = exports_from(data)
    except KeyError as exc:
        print(f"export-env: missing key {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"export-env: {exc}", file=sys.stderr)
        return 1
    for key, value in exports.items():
        print(f"export {key}={shlex.quote(str(value))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
