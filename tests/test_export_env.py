"""export-env.py derives $SUFFIX and reads paths.json."""
from __future__ import annotations

import importlib.util
import json
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "swift-local-build-test" / "scripts" / "export-env.py"
LIVE = ROOT / "swift-local-build-test/references/paths.json"


def load_mod():
    spec = importlib.util.spec_from_file_location("export_env", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class SuffixTests(unittest.TestCase):
    def setUp(self):
        self.mod = load_mod()

    def test_derives_known_products(self):
        cases = {
            "/b/swift-macosx-arm64": "macosx-arm64",
            "/b/swift-macosx-x86_64": "macosx-x86_64",
            "/b/swift-linux-x86_64": "linux-x86_64",
            "/b/swift-linux-aarch64": "linux-aarch64",
        }
        for build, suffix in cases.items():
            self.assertEqual(self.mod.platform_suffix(build), suffix)
            self.assertEqual(
                self.mod.lit_site_cfg(build),
                str(Path(build) / f"test-{suffix}" / "lit.site.cfg"),
            )

    def test_override_wins(self):
        self.assertEqual(
            self.mod.platform_suffix("/b/swift-macosx-arm64", "linux-x86_64"),
            "linux-x86_64",
        )

    def test_unknown_directory_uses_the_host(self):
        self.assertEqual(
            self.mod.platform_suffix("/b/not-a-swift-product"),
            self.mod.host_platform_suffix(),
        )


class ScriptTests(unittest.TestCase):
    def test_linux_build_exports_linux_cfg(self):
        data = {
            "build_swift": "/b/swift-linux-x86_64",
            "build_llvm": "/b/llvm-linux-x86_64",
            "swift_checkout": "/src/swift",
            "wiki_checkout": "/src/case-notes",
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "paths.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            out = subprocess.check_output(
                [sys.executable, str(SCRIPT), "--paths", str(path)],
                text=True,
            )
        vals = {}
        for line in out.splitlines():
            self.assertTrue(line.startswith("export "), line)
            key, raw = line[len("export ") :].split("=", 1)
            vals[key] = raw
        self.assertEqual(vals["SUFFIX"], "linux-x86_64")
        self.assertEqual(
            vals["CFG"],
            shlex.quote("/b/swift-linux-x86_64/test-linux-x86_64/lit.site.cfg"),
        )

    def test_missing_wiki_is_omitted(self):
        data = {
            "build_swift": "/b/swift-linux-x86_64",
            "build_llvm": "/b/llvm-linux-x86_64",
            "swift_checkout": "/src/swift",
        }
        mod = load_mod()
        exports = mod.exports_from(data)
        self.assertNotIn("WIKI", exports)

    def test_empty_wiki_is_omitted(self):
        data = {
            "build_swift": "/b/swift-linux-x86_64",
            "build_llvm": "/b/llvm-linux-x86_64",
            "swift_checkout": "/src/swift",
            "wiki_checkout": "",
        }
        mod = load_mod()
        self.assertNotIn("WIKI", mod.exports_from(data))

    def test_placeholder_paths_are_refused(self):
        data = {
            "build_swift": "/path/to/swift-project/build/swift-macosx-arm64",
            "build_llvm": "/path/to/swift-project/build/llvm-macosx-arm64",
            "swift_checkout": "/path/to/swift-project/swift",
            "wiki_checkout": "",
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "paths.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "--paths", str(path)],
                text=True,
                capture_output=True,
            )
        self.assertEqual(proc.returncode, 1)
        self.assertIn("placeholder", proc.stderr)
        self.assertNotIn("export B=", proc.stdout)

    def test_missing_file_names_the_example(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--paths", "/tmp/no-such-paths.json"],
            text=True,
            capture_output=True,
        )
        self.assertEqual(proc.returncode, 1)
        self.assertIn("paths.example.json", proc.stderr)

    @unittest.skipUnless(LIVE.is_file(), "paths.json is local and gitignored")
    def test_live_paths_match(self):
        mod = load_mod()
        data = json.loads(LIVE.read_text(encoding="utf-8"))
        out = subprocess.check_output([sys.executable, str(SCRIPT)], text=True)
        vals = {}
        for line in out.splitlines():
            key, raw = line[len("export ") :].split("=", 1)
            vals[key] = raw
        expect = mod.exports_from(data)
        for key, value in expect.items():
            self.assertEqual(vals[key], shlex.quote(value))


if __name__ == "__main__":
    unittest.main()
