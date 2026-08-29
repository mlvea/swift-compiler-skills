# Ballot schemas

Sitting experts return the expert object. The chair returns the chair
object. No other keys required.

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

- `in_scope: abstain` ⇒ `verdict: abstain`, empty blockers.
- `block` requires a named invariant and evidence.
- `approve` with empty evidence is invalid; cite the files read.
- Do not comment on domains you were not seated for.

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
