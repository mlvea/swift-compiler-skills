# macros (conditional)

The scope is freestanding macros, attached macros, macro expansion, and TypeCheckMacros.
Sit only on a **primary** file hit.
The hits are `lib/Macros/`, `TypeCheckMacros*`, and `test/Macros/`.

An ASTGen or SwiftSyntax parse bridge with no macro attribute is `parser-diagnostics`.
The SwiftSyntax package is a sibling checkout (`knowledge-base/sibling-repos.md`).

## Protects

- Macro expansion must produce syntax that the parser already accepts.
  Do not give macros a private grammar.
- Expansion is a compiler request.
  Do not add a process-global macro cache without a fingerprint of the plugin and the source.
- A macro that changes the user-visible language surface is evolution.
  This rule holds even when the implementation is a stdlib macro.

## Plan review

- Does `-typecheck` without expansion already fail?
  If it does, the bug is Sema or parse, not the plugin.
- A plugin crash and an expanded AST that Sema rejects are different layers.

## PR review

- Put tests in `test/Macros/` with the existing plugin and lit style.
- Use an ASTGen round-trip when the expansion must match the C++ parse.
  The `parser-diagnostics` seat is adjacent.

## Reject unless

- A new attached role, a new freestanding role, or implicit expansion of unannotated code needs evolution-gate.md.
- Do not special-case one stdlib macro in `CSSimplify` or in `TypeCheckMacros`.
  The seats are `type-system` and this seat.

## Evolution

The macro system shipped in SE-0382, SE-0389, and SE-0397.
A new language-facing macro or role needs a pitch.
A bug fix in the expansion of an accepted macro is `none`.

## Forum

An expansion bug is a compiler defect.
"Could a macro do this instead of language syntax?" is usually a pitch.
It is not a Sema patch.

## Abstain

Abstain when the change has no macro attribute, no plugin, no `TypeCheckMacros`, and no `test/Macros/` change.
A diff that touches only the SwiftSyntax package belongs in the `swift-syntax` sibling.
