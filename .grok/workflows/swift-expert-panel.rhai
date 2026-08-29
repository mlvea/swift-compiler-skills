let meta = #{
    name: "swift-expert-panel",
    description: "Seat domain experts to review a Swift compiler plan or PR, then a chair issues a weighted verdict",
    when_to_use: "Review a compiler fix plan or PR with the domain expert panel",
    phases: [
        #{ title: "Review", detail: "independent domain ballots" },
        #{ title: "Chair", detail: "weighted synthesis" },
    ],
};

let ballot_schema = #{
    "type": "object",
    "required": ["domain", "in_scope", "confidence", "verdict", "blockers", "concerns", "evolution", "evidence"],
    "properties": #{
        "domain": #{ "type": "string" },
        "in_scope": #{ "type": "string" },
        "confidence": #{ "type": "string" },
        "verdict": #{ "type": "string" },
        "blockers": #{ "type": "array", "items": #{ "type": "string" } },
        "concerns": #{ "type": "array", "items": #{ "type": "string" } },
        "questions": #{ "type": "array", "items": #{ "type": "string" } },
        "evolution": #{ "type": "string" },
        "evidence": #{ "type": "array", "items": #{ "type": "string" } },
    },
};

let chair_schema = #{
    "type": "object",
    "required": ["chair", "seated", "verdict", "evolution", "must_address", "rationale"],
    "properties": #{
        "chair": #{ "type": "string" },
        "seated": #{ "type": "array", "items": #{ "type": "string" } },
        "verdict": #{ "type": "string" },
        "evolution": #{ "type": "string" },
        "must_address": #{ "type": "array", "items": #{ "type": "string" } },
        "may_defer": #{ "type": "array", "items": #{ "type": "string" } },
        "rebuttals": #{ "type": "array", "items": #{ "type": "string" } },
        "rationale": #{ "type": "string" },
    },
};

if args == () {
    pause("verification", "Pass args: kind (plan|pr), chair, seated (array of domain ids), artifact (plan or diff text), kb_root (path to knowledge-base/expert-panel). Run seat.py first.");
}

let kind = args.kind;
let chair = args.chair;
let seated = args.seated;
let artifact = args.artifact;
let kb_root = args.kb_root;
let files = args.files;

if kind == () || chair == () || seated == () || artifact == () {
    pause("verification", "Need args.kind, args.chair, args.seated, args.artifact. Run swift-expert-panel/scripts/seat.py to get chair and seated.");
}
if kb_root == () {
    kb_root = "knowledge-base/expert-panel";
}
if files == () {
    files = "";
}

let artifact_json = json_encode(artifact);
let files_json = json_encode(files);
let kind_s = kind;
if type_of(kind) != "string" {
    kind_s = json_encode(kind);
}

phase("Review");
let jobs = [];
for d in seated {
    let prompt = "";
    prompt += "You are the '";
    prompt += d;
    prompt += "' domain reviewer on a Swift compiler review panel.\n";
    prompt += "Review kind: ";
    prompt += kind_s;
    prompt += "\nChanged files: ";
    prompt += files_json;
    prompt += "\n";
    prompt += "1. Read the domain brief at ";
    prompt += kb_root;
    prompt += "/domains/";
    prompt += d;
    prompt += ".md with read_file. Also read ";
    prompt += kb_root;
    prompt += "/evolution-gate.md and ";
    prompt += kb_root;
    prompt += "/ballot.md.\n";
    prompt += "2. Inspect the artifact (plan or diff) below using the brief's review questions. Do not answer from memory. If the artifact is too short to be a real plan/diff, still judge from what is present and lower confidence.\n";
    prompt += "3. If the change is outside this domain's charter, return in_scope=abstain and verdict=abstain with empty blockers.\n";
    prompt += "4. Otherwise return the expert ballot object from ballot.md. block requires a named invariant and evidence. approve requires evidence of files you read.\n";
    prompt += "5. Run the evolution gate on the change, not the issue title.\n";
    prompt += "ARTIFACT_JSON:\n";
    prompt += artifact_json;
    jobs.push(#{
        prompt: prompt,
        label: "expert:" + d,
        capability_mode: "read-only",
        output_schema: ballot_schema,
    });
}

let results = parallel(jobs);

let ballots = [];
let i = 0;
for r in results {
    let domain = seated[i];
    if r != () && r.success && r.output != () {
        ballots.push(r.output);
    } else {
        log("unusable ballot for " + domain);
        ballots.push(#{
            domain: domain,
            in_scope: "abstain",
            confidence: "low",
            verdict: "abstain",
            blockers: [],
            concerns: [],
            questions: ["unusable-ballot"],
            evolution: "none",
            evidence: ["unusable-ballot"],
        });
    }
    i += 1;
}

let ballots_json = json_encode(ballots);

phase("Chair");
let chair_prompt = "";
chair_prompt += "You are the chair of a Swift compiler expert panel. Your domain is '";
chair_prompt += chair;
chair_prompt += "'.\n";
chair_prompt += "Read ";
chair_prompt += kb_root;
chair_prompt += "/chair-protocol.md, ";
chair_prompt += kb_root;
chair_prompt += "/evolution-gate.md, ";
chair_prompt += kb_root;
chair_prompt += "/ballot.md, and ";
chair_prompt += kb_root;
chair_prompt += "/domains/";
chair_prompt += chair;
chair_prompt += ".md.\n";
chair_prompt += "Weighting: chair in-scope = 1.0 (your block is final); other in-scope = 0.5 (block needs a written rebuttal naming the invariant); abstain/unusable = 0 and is not approval.\n";
chair_prompt += "Seated domains: ";
chair_prompt += json_encode(seated);
chair_prompt += "\nReview kind: ";
chair_prompt += kind_s;
chair_prompt += "\nChanged files: ";
chair_prompt += files_json;
chair_prompt += "\nIndependent ballots JSON:\n";
chair_prompt += ballots_json;
chair_prompt += "\nArtifact JSON:\n";
chair_prompt += artifact_json;
chair_prompt += "\nReturn the chair verdict object from ballot.md. Re-open the artifact only if a ballot contradicts it.";

let chair_r = agent(chair_prompt, #{
    label: "chair:" + chair,
    capability_mode: "read-only",
    output_schema: chair_schema,
});

if chair_r == () || !chair_r.success || chair_r.output == () {
    complete(#{
        verdict: "block",
        chair: chair,
        seated: seated,
        ballots: ballots,
        evolution: "none",
        must_address: ["chair-agent-failed"],
        rationale: "Chair agent failed; fail closed.",
    });
}

let verdict = chair_r.output;
let report = "";
report += "# Expert panel\n\n";
report += "Chair: ";
report += chair;
report += "\nSeated: ";
report += json_encode(seated);
report += "\nVerdict: ";
report += verdict.verdict;
report += "\nEvolution: ";
report += verdict.evolution;
report += "\n\n## Rationale\n\n";
report += verdict.rationale;
report += "\n\n## Ballots\n\n";
report += ballots_json;
report += "\n";
let path = write_scratch_file("panel-verdict.md", report);
complete(#{
    path: path,
    chair: chair,
    seated: seated,
    ballots: ballots,
    verdict: verdict,
});
