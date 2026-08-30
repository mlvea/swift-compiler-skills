# macros (conditional)

Freestanding/attached macros, macro expansion, TypeCheckMacros.
Sit only on a **primary** file hit (`lib/Macros/`, `TypeCheckMacros*`,
`test/Macros/`). ASTGen/SwiftSyntax parse bridge without a macro
attribute is `parser-diagnostics`. The SwiftSyntax *package* is a
sibling checkout (`knowledge-base/sibling-repos.md`).

## Protects

- Macro expansion must produce syntax the parser already accepts.
  Do not give macros a private grammar.
- Expansion is a compiler request. No process-global macro cache
  without a fingerprint of the plugin + source.
- A macro that changes user-visible language surface is evolution,
  even if implemented as a stdlib macro.

## Plan review

- Does `-typecheck` without expansion already fail? Then Sema/parse,
  not the plugin.
- Plugin crash vs expanded AST that Sema rejects: different layers.

## PR review

- Tests in `test/Macros/` with the existing plugin/lit style.
- ASTGen round-trip when the expansion must match C++ parse
  (`parser-diagnostics` adjacent).

## Reject unless

- New attached/freestanding roles or implicit expansion of unannotated
  code → evolution gate.
- Do not special-case one stdlib macro in `CSSimplify` /
  `TypeCheckMacros` (`type-system` / this seat).

## Evolution

Macro *system* shipped via SE-0382/0389/0397. New language-facing
macros or roles need a pitch. Bugfixes in expansion of an accepted
macro are `none`.

## Forum

Expansion bugs are compiler defects. "Could a macro do this instead of
language syntax?" is commonly a pitch, not a Sema patch.

## Abstain

No macro attribute, plugin, `TypeCheckMacros`, or `test/Macros/` change.
SwiftSyntax-package-only diffs belong in the `swift-syntax` sibling.
