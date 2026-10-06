# Writing

- Do not put a home-directory path in the README, in `docs/`, in the
  knowledge base, or in an entry skill file. A path that starts with
  `/Users/` or `/home/` is a home-directory path.
- Keep machine paths in `swift-local-build-test/references/paths.json`.
  That file is gitignored. Copy `paths.example.json`.
- In every other file, name the checkout `swiftlang/swift`, or use
  `$B`, `$LIT`, and `$FE`.
- Do not use a U+2014 dash or a U+2013 dash. Use a period, a comma, a
  colon, or a hyphen.
- Do not use the filler words in `scripts/check-doc-prose.py`.
- Run `python3 scripts/check_repo.py` on the whole tree.
