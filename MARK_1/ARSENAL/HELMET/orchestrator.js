export const meta = {
  name: 'helmet-university-mode',
  description: 'University-Mode orchestrator: Provost triages each problem, routes to a department, department executes (machine-checked), an independent model peer-reviews. Tests 3 problems across the kappa-spectrum.',
  phases: [
    { title: 'Provost', detail: 'triage each problem -> deterministic routing plan (provost.py)' },
    { title: 'Department', detail: 'route to dept; execute with machine checks (sonnet generator)' },
    { title: 'PeerReview', detail: 'independent model (haiku != generator) re-verifies each deliverable' },
  ],
}

const ROOT = '/Users/varunesh/Desktop/AI_agents'
const H = ROOT + '/Expanding_Frontiers/HELMET'

const PROBLEMS = [
  { id: 'A', kind: 'kappa1-construct',
    prompt: 'Construct a Sidon set (a B2 set: all pairwise sums a+b distinct) of size 8 contained in the integers {1,...,35}, and certify it. State whether 8 is the maximum achievable in that range.' },
  { id: 'B', kind: 'mediumkappa-empirical',
    prompt: 'A paper reports, for a single 1-7 Likert item answered by N=18 participants, a mean of 3.94. A second paper reports a mean of 5.19 for N=28 on the same kind of item. Run a forensic consistency (GRIM) check on each and report what you can certify.' },
  { id: 'C', kind: 'kappa0-judgment',
    prompt: 'Should a mid-sized European country adopt a nationally mandated four-day (32-hour) work week? Give the answer.' },
]

const INTAKE_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['problem','domains','task_type','kappa','known_vs_open','has_data','stakes','triviality','proxy_only_scorer','deterministic_plan'],
  properties: {
    problem: { type: 'string' },
    domains: { type: 'array', items: { type: 'string' } },
    task_type: { type: 'string' },
    kappa: { type: 'number' },
    known_vs_open: { type: 'string' },
    has_data: { type: 'boolean' },
    stakes: { type: 'string' },
    triviality: { type: 'string' },
    proxy_only_scorer: { type: 'boolean' },
    deterministic_plan: {
      type: 'object', additionalProperties: true,
      required: ['scale','convened_departments','peer_review_required','must_end_in_abstention_if_unverifiable'],
      properties: {
        scale: { type: 'string' },
        convened_departments: { type: 'array' },
        peer_review_required: { type: 'boolean' },
        must_end_in_abstention_if_unverifiable: { type: 'boolean' },
      },
    },
  },
}

const DELIV_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['department','what_was_done','machine_check','machine_check_output','claim','claim_status','abstained','honest_ceiling'],
  properties: {
    department: { type: 'string' },
    what_was_done: { type: 'string' },
    machine_check: { type: 'string', description: 'the exact command/verifier run, or "none (kappa=0)"' },
    machine_check_output: { type: 'string', description: 'the actual output observed when running it' },
    claim: { type: 'string' },
    claim_status: { type: 'string', enum: ['verified','reproduced','grounded','abstained'] },
    abstained: { type: 'boolean' },
    honest_ceiling: { type: 'string' },
  },
}

const REVIEW_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['independently_reproduced','reproduction_method','overclaims_found','abstention_correct','verdict','notes'],
  properties: {
    independently_reproduced: { type: 'string', enum: ['yes','no','n/a'] },
    reproduction_method: { type: 'string' },
    overclaims_found: { type: 'array', items: { type: 'string' } },
    abstention_correct: { type: 'string', enum: ['yes','no','n/a'] },
    verdict: { type: 'string', enum: ['CONFIRM','CONFIRM_WITH_CAVEATS','REJECT'] },
    notes: { type: 'string' },
  },
}

const results = await pipeline(
  PROBLEMS,

  // STAGE 1 — PROVOST (triage). Emits the intake descriptor AND runs the deterministic
  // provost.py to get the canonical machine-checked routing plan.
  (p) => agent(
    `You are the PROVOST of University Mode (the HELMET orchestrator). Triage this problem and produce a structured intake.\n\n` +
    `PROBLEM (id ${p.id}): ${p.prompt}\n\n` +
    `The department registry is ${H}/registry.json (read it). Department keys: MATH_TCS, STATS, QUANT_PSYCH, SOCIAL_SCI, CS_ENG, NAT_SCI, ECON_FIN, HUMANITIES_LAW_POLICY.\n` +
    `Decide: domains (department keys), task_type (construct|prove|analyze|measure|design|decide|explain|forecast), kappa (0..1: does a cheap EXACT non-gameable verifier exist for the load-bearing claim?), known_vs_open, has_data, stakes (low|medium|high), triviality (oneliner|bounded|substantial), proxy_only_scorer.\n\n` +
    `THEN write your intake (those fields) to ${H}/tests/runs/intake_${p.id}.json and run:  python3 ${H}/provost.py ${H}/tests/runs/intake_${p.id}.json\n` +
    `Capture the deterministic routing plan it prints. Return the intake fields plus deterministic_plan = the JSON the script printed (at least scale, convened_departments, peer_review_required, must_end_in_abstention_if_unverifiable).\n` +
    `Be honest about kappa: a normative 'should' question has kappa=0; a pairwise-sum check is kappa=1; a GRIM arithmetic check is kappa=1.`,
    { label: `provost:${p.id}`, phase: 'Provost', schema: INTAKE_SCHEMA }
  ).then(intake => ({ p, intake })),

  // STAGE 2 — DEPARTMENT (execute). Sonnet generator. MUST execute machine checks for kappa>0,
  // and MUST ground+abstain for kappa=0 (no fabricated certainty).
  ({ p, intake }) => agent(
    `You are the lead PI of the convened department for University Mode. Execute the R&D deliverable.\n\n` +
    `PROBLEM (id ${p.id}): ${p.prompt}\n\n` +
    `PROVOST ROUTING (machine-checked): scale=${intake.deterministic_plan.scale}; departments=${JSON.stringify(intake.deterministic_plan.convened_departments.map(d=>d.department||d))}; kappa=${intake.kappa}; must_abstain_if_unverifiable=${intake.deterministic_plan.must_end_in_abstention_if_unverifiable}.\n\n` +
    `NON-NEGOTIABLE RULES:\n` +
    `- If kappa>0 (a checkable object/arithmetic): PRODUCE the object, then WRITE AND RUN a verifier script (python3) that re-checks it FROM SCRATCH. Put the verifier under ${H}/tests/runs/ and report its ACTUAL output. Do NOT vote on what you can execute.\n` +
    `- For a KNOWN target, label the result a REPRODUCTION (source + that it is a known small/extremal object), NEVER a record or open-problem solve.\n` +
    `- For a forensic (GRIM) check: report the EXACT arithmetic; label INCONSISTENCY != FRAUD; report the inconsistency and STOP — never accuse.\n` +
    `- If kappa=0 (judgment/normative): GROUND the empirical sub-claims (fetch real sources via WebSearch/WebFetch where load-bearing, or flag unverified) and ABSTAIN on the normative verdict — frame it as value-dependent. Do NOT fabricate a confident yes/no.\n` +
    `- State the honest ceiling: the Helmet is organized, not smarter; it cannot exceed the model's ceiling.\n\n` +
    `Return the deliverable per schema: what you did, the exact machine_check command (or 'none (kappa=0)'), its actual output, the claim, claim_status (verified|reproduced|grounded|abstained), abstained (bool), honest_ceiling.`,
    { label: `dept:${p.id}`, phase: 'Department', model: 'sonnet', schema: DELIV_SCHEMA }
  ).then(deliverable => ({ p, intake, deliverable })),

  // STAGE 3 — PEER REVIEW (independent, model != generator). Haiku re-verifies.
  ({ p, intake, deliverable }) => agent(
    `You are the PEER-REVIEW committee for University Mode. You are a DIFFERENT model than the department that produced this (independence is the point). Adversarially audit the deliverable.\n\n` +
    `PROBLEM (id ${p.id}): ${p.prompt}\n` +
    `DEPARTMENT DELIVERABLE: ${JSON.stringify(deliverable)}\n\n` +
    `Your job:\n` +
    `- If a machine check is claimed (kappa>0): INDEPENDENTLY reproduce it. Write your OWN check (do not reuse their script) and RUN it via python3. For the Sidon set: extract their set and verify all C(8,2) pairwise sums are distinct yourself. For GRIM: recompute mean*N yourself and check integrality. Report independently_reproduced=yes/no and your method.\n` +
    `- Hunt for OVERCLAIMS: a reproduction sold as a record? an open problem claimed solved? a kappa=0 verdict fabricated as certainty? an accusation of fraud where only inconsistency is shown? List every one found (empty list if none).\n` +
    `- For a kappa=0 task: confirm the deliverable ABSTAINED on the normative verdict (abstention_correct=yes) rather than inventing certainty; if it fabricated a confident verdict, abstention_correct=no.\n` +
    `- verdict: CONFIRM / CONFIRM_WITH_CAVEATS / REJECT.\n` +
    `Be skeptical and specific. Default to flagging if uncertain.`,
    { label: `review:${p.id}`, phase: 'PeerReview', model: 'haiku', schema: REVIEW_SCHEMA }
  ).then(review => ({ id: p.id, kind: p.kind, intake, deliverable, review }))
)

return { results: results.filter(Boolean) }
