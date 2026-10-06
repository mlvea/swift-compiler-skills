# Ballot schemas

A sitting expert returns the expert object.
The chair returns the chair object.
No other keys are required.

## Expert ballot

```
{
  "domain": "<id>",
  "in_scope": "in" | "abstain",
  "confidence": "high" | "medium" | "low",
  "verdict": "approve" | "request-changes" | "block" | "abstain",
  "blockers": ["<must-fix invariant or layer error>"],
  "concerns": ["<should-fix>"],
  "questions": ["<unresolved, blocks confidence>"],
  "evolution": "none" | "needs-pitch" | "needs-proposal",
  "evidence": ["<path:line | SE-NNNN | forum URL>"]
}
```

Rules:

- `in_scope: abstain` means `verdict: abstain` and empty blockers.
- `block` requires a named invariant from this seat.
  Take it from `Protects` or from `Reject unless`.
  Or cite an official doc path that the brief lists.
  Add evidence.
- `approve` with empty evidence is invalid.
  Cite the files that you read.
- Do not comment on a domain that did not seat you.
- Apply the rules fail-closed.
  If a named invariant is violated, do not use `approve`.
  If the artifact cites no exception from that same official doc, use `block`.
  Do not put that violation only in a concern.

## Chair verdict

```
{
  "chair": "<id>",
  "seated": ["<id>", "..."],
  "verdict": "approve" | "request-changes" | "block",
  "evolution": "none" | "needs-pitch" | "needs-proposal",
  "must_address": ["<from chair blockers + unrebutted adjacent>"],
  "may_defer": ["<adjacent concerns>"],
  "rebuttals": ["<adjacent blocker → why it does not apply>"],
  "rationale": "<one short paragraph, domain ids, SE numbers, paths>"
}
```
