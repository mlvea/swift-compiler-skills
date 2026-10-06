# Explainer page structure

Write as a person who just understood the bug and is now teaching it.
Define each special term at first use. Then use that term.

## Shape

1. **Kicker** (mono). Write `swiftlang/swift#N` and the triage stage.
2. **Title.** State the failure in plain language. Do not copy the GitHub title unless that title is already plain.
3. **Claim** (one italic sentence). State what goes wrong and who hits it.
4. **The program.** Show the smallest reducer. Show the code that the user wrote. Show the result that the user expected. Show the exact command that fails. Show the output of that command.
5. **The rule.** State the language rule or the compiler invariant that this program is owed. Cite an SE, the book, or a comment in the tree when you have one. Say so when the rule is unwritten.
6. **What breaks.** State the expected result, then the observed result. Quote the assert, the diagnostic, or the wrong SIL or IR.
7. **Where.** Name the pipeline stage. Then name the file and the function that this reducer enters. Then name the local fault. The fault is a check that is too weak, a path that is not taken, or a value that is already wrong. Put a pipeline schematic here when the stage is the point. Put a flow schematic here when a value, an ownership fact, or an isolation fact is the point.
8. **Why.** State the broken assumption. Say why the code believed a false fact on this reducer. Do not stop at "file X is wrong".
9. **What we intend to change.** Take this from the approved plan. State the smallest restoration of the invariant. Name the likely files. Name what will not change. Give the chair verdict in one line.
10. **Deeper** (`<details>`). Put the panel seating JSON here. List the files you opened and why. Add a related SE or forum thread. List the questions that are still open.

Do not add an essay about the Swift compiler in general.
Teach only the facts that this issue needs.
Give those facts in the order a reader needs.

## Diagrams

Add a figure only when one sentence cannot carry the claim.

- State one claim in the caption.
- Use a hairline SVG. Put labels in the monospace face of the page. Do not add decoration.
- Mark an approximation `schematic`.
- Do not use a screenshot of the IDE. Do not use a generated illustration.

## Voice

Use short sentences.
Use a concrete noun. Write `CSGen.cpp` and `emitApply`, not "the backend".
Do not use filler.

Cut a later section when it repeats an earlier section.

## Done when

Open the page in a browser before you call it done.
A colleague who does not know this bug must explain four things after one pass.
Those things are the reducer, the rule, the failing function, and the intended change.
