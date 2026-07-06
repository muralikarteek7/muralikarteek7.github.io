// SCHOLAR · research.workflow.js — reusable, parameterized Mark research engine.
// Generalized from the operator's rohini_research_workflow.js + the 2026 validation refinements.
// Drive it with the intake contract via `args` (see MARK_1/ARSENAL/SCHOLAR/INTAKE_AND_RUBRICS.md §A):
//   { topic, reviewType, domainProfile:'stem'|'humanities', sourceOfTruth, question, conceptBlocks,
//     databases, offlineLibrary, inclusion, audience, donePredicate, outputPath,
//     seats?:[{key,role,charter}], maxSeats? }
// Run:  Workflow({ scriptPath: ".../research.workflow.js", args: <intake contract> })
export const meta = {
  name: 'mark1-research',
  description: 'Mark 1 Research mode engine: auditable search (offline+online, mandatory citation chaining) -> charter-driven seats sized to distinct sub-domains (diversity>count) -> consolidate + structured gap analysis -> adaptive cross-model + retrieval verify-or-ABSTAIN -> one-pen write -> provenance/argument/de-AI review. Honesty rails non-waivable.',
  phases: [
    { title: 'Plan',        detail: 'declare review type + design the charter seats sized to the topic' },
    { title: 'Recon',       detail: 'offline library + online; concept-block string + backward+forward citation chaining' },
    { title: 'Seats',       detail: 'N charter-driven domain experts produce sourced findings with load-bearing tags' },
    { title: 'Consolidate', detail: 'merge load-bearing claims + structured gap analysis (4-way taxonomy)' },
    { title: 'Verify',      detail: 'adversarial cross-model + retrieval-gated; abstain when unresolved' },
    { title: 'Write',       detail: 'single pen; respect the verification ledger; AI-use disclosure' },
    { title: 'Review',      detail: 'provenance + argument + de-AI (surgical, content frozen)' },
  ],
}

const A = args || {};
const TOPIC = A.topic || A.question || 'the requested topic';
const PROFILE = A.domainProfile === 'humanities' ? 'humanities' : 'stem';
const REVIEW_TYPE = A.reviewType || 'rapid/narrative';
const OUT = A.outputPath || '/tmp/mark1_research_survey.md';
// default 3-5; extend only for genuinely DISTINCT sub-domains. Seats past ~9-10 regress if homogeneous
// (diversity>count, verified). Hard ceiling 15 for a genuinely broad survey.
const MAX_SEATS = Math.max(3, Math.min(A.maxSeats || 8, 15));
const LIB = A.offlineLibrary || '/Users/varunesh/Desktop/Books_Folder';

const BRIEF = `RESEARCH RUN (Mark 1 Research mode). TOPIC: ${TOPIC}
REVIEW TYPE: ${REVIEW_TYPE} (declare which corners are cut; a Mark run is realistically rapid/narrative, NOT
systematic — never imply exhaustiveness you did not perform; rapid reviews have NO validated reporting guideline).
DOMAIN PROFILE: ${PROFILE} ${PROFILE === 'humanities'
  ? '— HUMANITIES/history-of-science: split PRIMARY vs SECONDARY sources, appraise by provenance/edition/context (NOT RoB/GRADE); discovery = HSTM/JSTOR/HathiTrust/Internet-Archive/subject-bibliographies + citation chaining + the offline library; synthesis = META-NARRATIVE/RAMESES paradigm-tracing, NOT pooled effects; never force a PRISMA diagram onto a historiographic essay.'
  : '— STEM-empirical: concept-block search, GRADE-style certainty for empirical claims, inclusion/exclusion predicate frozen.'}
SOURCE OF TRUTH: ${A.sourceOfTruth || '(others\' published work — synthesis)'}.
ANTI-CASCADE: no agent treats another agent\'s text as fact unless it traces to a real source.
HONESTY: never fabricate a citation/number/DOI/quote; ABSTAIN on the unresolved; an LLM may rank/second-check but
is NEVER the sole includer/excluder or sole synthesis source (human-in-the-loop, disclosed).`;

const FINDING_SCHEMA = { type:'object', additionalProperties:false,
  required:['seat','summary','claims','best_sources'],
  properties:{ seat:{type:'string'}, summary:{type:'string'},
    claims:{type:'array', items:{type:'object', additionalProperties:false,
      required:['claim','support','load_bearing'],
      properties:{ claim:{type:'string'}, support:{type:'string'}, load_bearing:{type:'boolean'} }}},
    best_sources:{type:'array', items:{type:'string'}} } };

// ---- PLAN: declare review type + design the seats sized to the topic's distinct sub-domains ----
phase('Plan');
const PLAN_SCHEMA = { type:'object', additionalProperties:false,
  required:['seats','search_concept_blocks','notes'],
  properties:{
    seats:{type:'array', description:`one charter per GENUINELY DISTINCT sub-domain; ${MAX_SEATS} max; default 3-5, extend only for real breadth`,
      items:{type:'object', additionalProperties:false, required:['key','role','charter'],
        properties:{ key:{type:'string'}, role:{type:'string'}, charter:{type:'string'} }}},
    search_concept_blocks:{type:'array', items:{type:'string'}},
    notes:{type:'string'} } };
const plan = A.seats && A.seats.length
  ? { seats: A.seats.slice(0, MAX_SEATS), search_concept_blocks: A.conceptBlocks || [], notes: 'seats supplied by intake' }
  : await agent(
    `You are the LEAD designing a research team for a literature survey. ${BRIEF}
Decompose the topic into its GENUINELY DISTINCT sub-domains and emit one charter per sub-domain (a real survey of a
broad topic may need 8-15; a narrow one needs 3-5). TEAM-SIZING RULE: the lever is DIVERSITY of angle, not count —
do NOT pad with redundant seats; each seat must own a distinct evidence channel. Also give the search concept
blocks (controlled-vocab UNION free-text) for the recon string.`,
    { label:'plan:seats', phase:'Plan', schema:PLAN_SCHEMA });
const SEATS = (plan.seats || []).slice(0, MAX_SEATS);
log(`Plan: ${REVIEW_TYPE} ${PROFILE} review; ${SEATS.length} charter seats designed.`);

// ---- RECON: offline library + online; concept blocks + MANDATORY citation chaining ----
phase('Recon');
const RECON_SCHEMA = { type:'object', additionalProperties:false,
  required:['search_string','summaries','landmark_sources','gap_notes'],
  properties:{ search_string:{type:'string', description:'one full concept-block search string, verbatim (PRISMA-S)'},
    summaries:{type:'array', items:{type:'object', additionalProperties:false, required:['ref','what','relevance'],
      properties:{ ref:{type:'string'}, what:{type:'string'}, relevance:{type:'string'} }}},
    landmark_sources:{type:'array', items:{type:'object', additionalProperties:false, required:['cite','why'],
      properties:{ cite:{type:'string'}, why:{type:'string'} }}},
    gap_notes:{type:'string'} } };
const [offline, online] = (await parallel([
  () => agent(`You are the OFFLINE LIBRARIAN. ${BRIEF}
Scan the offline library ${LIB} (ls|grep filenames by the concept blocks ${JSON.stringify(plan.search_concept_blocks||[])};
pdftotext/grep and Read the top ~10-15 hits). Return summaries ONLY for sources you actually opened; be honest when
relevance is name-inferred. Also propose part of the verbatim search string.`,
    { label:'recon:offline', phase:'Recon', schema:RECON_SCHEMA }),
  () => agent(`You are the ONLINE CARTOGRAPHER. ${BRIEF}
Use WebSearch/WebFetch with a concept-block string, then DO MANDATORY backward + forward citation chaining from the
strongest hits to saturation (keyword-only recall is insufficient). Do NOT cite an expected snowballing yield
percentage — chaining is mandatory but its real-world exclusive yield varies widely (~2.5-42.7%); never state it as
"~50%". Return the verbatim search string, summaries for pages you actually fetched, landmark sources, and gaps.
Flag non-scholarly sources.`,
    { label:'recon:online', phase:'Recon', schema:RECON_SCHEMA }),
])).filter(Boolean);
const reconDigest = JSON.stringify({ offline, online }).slice(0, 12000);
log(`Recon: ${(offline?.summaries?.length||0)+(online?.summaries?.length||0)} sources scanned + citation chaining.`);

// ---- SEATS ----
phase('Seats');
const findings = (await parallel(SEATS.map((m) => () => agent(
  `You are the ${m.role}, one seat of a ${SEATS.length}-member research team. ${BRIEF}
RECON DIGEST (reuse; don't re-derive): ${reconDigest}
YOUR CHARTER: ${m.charter}
Pull on BOTH the offline library and online for YOUR charter. Every claim carries its support (source + value/
passage); tag the central, contestable ones load_bearing:true. Prefer scholarly sources; flag where a figure differs
from what you can confirm. Do NOT treat other seats' text as fact unless it traces to a source.`,
  { label:`seat:${m.key}`, phase:'Seats', schema:FINDING_SCHEMA }))) ).filter(Boolean);
log(`Seats: ${findings.length}/${SEATS.length} reported.`);

// ---- CONSOLIDATE + GAP ANALYSIS ----
phase('Consolidate');
const loadBearing = findings.flatMap((f) => (f?.claims||[]).filter(c=>c.load_bearing).map(c=>({...c, seat:f.seat})));
const CONS_SCHEMA = { type:'object', additionalProperties:false, required:['claims','gaps'],
  properties:{
    claims:{type:'array', description:'deduped load-bearing claims to verify (aim 8-14)',
      items:{type:'object', additionalProperties:false, required:['id','claim','claimed_support','risk'],
        properties:{ id:{type:'string'}, claim:{type:'string'}, claimed_support:{type:'string'},
          risk:{type:'string', enum:['number','date','attribution','identification','translation','provenance','other']} }}},
    gaps:{type:'array', description:'structured gap analysis',
      items:{type:'object', additionalProperties:false, required:['gap','type','next_claim'],
        properties:{ gap:{type:'string'},
          type:{type:'string', enum:['empirical-void','contradiction','methodological','under-theorized']},
          next_claim:{type:'string', description:'a FALSIFIABLE next-step claim (never "more research needed")'} }}} } };
const cons = await agent(
  `You are the AGGREGATOR. Merge these load-bearing claims (dedupe, drop trivially-true), keep 8-14 that genuinely
need adversarial verification. ALSO emit a STRUCTURED GAP ANALYSIS (taxonomy: empirical-void/contradiction/
methodological/under-theorized), each gap tied to a FALSIFIABLE next claim.
${JSON.stringify(loadBearing, null, 1).slice(0, 14000)}`,
  { label:'consolidate', phase:'Consolidate', schema:CONS_SCHEMA });
const toVerify = (cons?.claims||[]).slice(0, 14);
log(`Consolidated ${toVerify.length} claims + ${(cons?.gaps||[]).length} structured gaps.`);

// ---- VERIFY (adversarial cross-model + retrieval; abstain) ----
phase('Verify');
const VERDICT_SCHEMA = { type:'object', additionalProperties:false,
  required:['id','verdict','confidence','evidence','note'],
  properties:{ id:{type:'string'},
    verdict:{type:'string', enum:['supported','partially-supported','disputed','refuted','abstain']},
    confidence:{type:'string', enum:['high','medium','low']},
    evidence:{type:'string'}, note:{type:'string'} } };
const verdicts = (await pipeline(toVerify,
  (c) => agent(
    `You are an ADVERSARIAL verifier (a DIFFERENT model than the writer; try to REFUTE, not confirm). Default to a
lower verdict when uncertain; a confident-but-unverifiable claim is 'disputed' or 'abstain', never 'supported'.
CLAIM [${c.id}, risk=${c.risk}]: ${c.claim}
CLAIMED SUPPORT: ${c.claimed_support}
ACTUALLY FETCH grounding (WebSearch/WebFetch and/or grep+Read the offline library) — a fact wrong in all priors is
caught only by RETRIEVAL. If a number/date conflicts, mark disputed/refuted with the conflicting value. Cite what
you consulted.`,
    { label:`verify:${c.id}`, phase:'Verify', schema:VERDICT_SCHEMA }).then(v=>({...c, ...v})),
)).filter(Boolean);
const supported = verdicts.filter(v=>v.verdict==='supported'||v.verdict==='partially-supported');
const flagged = verdicts.filter(v=>['disputed','refuted','abstain'].includes(v.verdict));
log(`Verify: ${supported.length} supported, ${flagged.length} flagged/abstained.`);

// ---- WRITE (one pen, respect the ledger) ----
phase('Write');
const WRITE_SCHEMA = { type:'object', additionalProperties:false,
  required:['written','word_count','section_titles'],
  properties:{ written:{type:'boolean'}, word_count:{type:'number'}, section_titles:{type:'array', items:{type:'string'}} } };
const writeRes = await agent(
  `You are the SINGLE PEN writing a scholarly ${REVIEW_TYPE} survey of ${TOPIC} for ${A.audience||'historians of science + domain experts'}.
${BRIEF}
INPUTS (use; do not invent beyond them): seats=${JSON.stringify(findings).slice(0,16000)}
SUPPORTED (assert plainly)=${JSON.stringify(supported).slice(0,5000)}
FLAGGED (HEDGE/attribute/mark disputed — NEVER assert as settled)=${JSON.stringify(flagged).slice(0,5000)}
GAPS=${JSON.stringify(cons?.gaps||[]).slice(0,3000)}
Use review-type-matched appraisal language (GRADE/SANRA). Single human voice (vary sentence length, no list-itis,
no boilerplate). End with a "Verification status & limits" note (supported vs flagged) + a one-line AI-use
disclosure. WRITE the survey to ${OUT} (use your Write tool). Return a summary.`,
  { label:'writer', phase:'Write', schema:WRITE_SCHEMA });
log(`Draft written (${writeRes?.word_count||'?'} words). Reviewing...`);

// ---- REVIEW (provenance + argument + de-AI) ----
phase('Review');
const REVIEW_SCHEMA = { type:'object', additionalProperties:false, required:['lane','blocking_defects'],
  properties:{ lane:{type:'string'}, blocking_defects:{type:'array', items:{type:'object', additionalProperties:false,
    required:['where','problem','fix'], properties:{ where:{type:'string'}, problem:{type:'string'}, fix:{type:'string'} }}} } };
const reviews = (await parallel([
  () => agent(`PROVENANCE checker (cross-model). Read ${OUT}. Every load-bearing number/date/citation must trace to
the ledger/a real source; flag any FLAGGED claim asserted as settled: ${JSON.stringify(flagged).slice(0,4000)}.
Flag fabricated-looking citations. Return blocking defects with exact fixes.`,
    { label:'review:provenance', phase:'Review', schema:REVIEW_SCHEMA }),
  () => agent(`ARGUMENT checker. Read ${OUT}. Find overclaims, non-sequiturs, places a disputed point is stated too
strongly, hedges that were dropped. Concrete fixes.`,
    { label:'review:argument', phase:'Review', schema:REVIEW_SCHEMA }),
  () => agent(`DE-AI/STYLE checker (surgical, content FROZEN). Read ${OUT}. Flag AI-tells (list-itis, boilerplate,
uniform sentence length, robotic transitions, >40-word sentences, 3+ near-equal-length sentences). Mark what to
re-voice; CHANGE NO FACTS. Note: a detector is not a gate.`,
    { label:'review:deai', phase:'Review', schema:REVIEW_SCHEMA }),
])).filter(Boolean);
const defects = reviews.flatMap(r => (r?.blocking_defects||[]).map(d=>({lane:r.lane, ...d})));
if (defects.length) {
  await agent(`You are the SAME single pen. Read ${OUT} and apply these review findings with surgical, diff-gated
edits — fix the defects and de-AI the prose, but CHANGE NO FACTS/numbers and keep every hedge on flagged claims.
Overwrite ${OUT}. DEFECTS: ${JSON.stringify(defects, null, 1).slice(0,9000)}`,
    { label:'revise', phase:'Review', schema:WRITE_SCHEMA });
  log(`Revision applied (${defects.length} defects).`);
}

return {
  output: OUT, review_type: REVIEW_TYPE, profile: PROFILE,
  seats: SEATS.map(s=>s.key), search_strings: [offline?.search_string, online?.search_string].filter(Boolean),
  verification_ledger: verdicts.map(v=>({id:v.id, verdict:v.verdict, confidence:v.confidence, note:v.note})),
  supported: supported.length, flagged: flagged.length, gaps: cons?.gaps || [],
};
