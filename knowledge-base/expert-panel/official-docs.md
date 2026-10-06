# Official docs the panel must load

Paths are relative to a `swiftlang/swift` checkout.
On a local machine, that checkout is `swift_checkout` in `paths.json`.
Copy `paths.example.json`.
Briefs index the fail-closed rule.
These files are the spec.
The list has 11 paths.

`probe_globs.py --checkout` checks that these files still exist.
Push CI and pull-request CI run that check on `swiftlang/swift` `main`.
A weekly workflow runs the same check.
The weekly schedule stops after 60 days with no commit.
A later commit does not start that schedule again.
The push and pull-request job is the durable glob check.

- `docs/TypeChecker.md`
- `docs/SIL/Ownership.md`
- `docs/SIL/Types.md`
- `docs/SIL/SIL.md`
- `docs/SIL/SILFunctionConventions.md`
- `docs/SIL/SILMemoryAccess.md`
- `docs/HowToUpdateDebugInfo.md`
- `docs/LibraryEvolution.rst`
- `docs/ABI/TypeMetadata.rst`
- `docs/DebuggingTheCompiler.md`
- `docs/Driver.md`
