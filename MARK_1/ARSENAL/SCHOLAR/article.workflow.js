// SCHOLAR · article.workflow.js — reusable, parameterized Mark article engine.
// Generalized from the operator's article_workflow.js + the 2026 validation refinements.
// Drive it with the intake contract via `args` (see MARK_1/ARSENAL/SCHOLAR/INTAKE_AND_RUBRICS.md §B):
//   { deliverableType:'journal-paper'|'review-synthesis'|'book-chapter'|'thesis-chapter', venue, venueSpec,
//     styleAnchorPath, styleSample, sourceOfTruth, length, componentBudget, domainProfile:'stem'|'humanities',
//     citationSource, ownerWritingRules:[...], outputPath, verifyCmd?, reviewLenses?:[...] }
// Run:  Workflow({ scriptPath: ".../article.workflow.js", args: <intake contract> })
export const meta = {
  name: 'mark1-article',
  description: 'Mark 1 Article mode engine: Freeze (frozen skeleton + MEASURED style-sheet + venue spec + compliance slots) -> Components (eqns/tables/refs, NO fabricated DOIs) -> one-pen Draft -> retrieval-gated cross-model Verify -> Review loop -> surgical DIFF-GATED de-AI + style-mimic (content FROZEN) -> venue-reviewer gate -> numeric-diff proof. Honesty rails non-waivable.',
  phases: [
    { title: 'Freeze',     detail: 'frozen skeleton + measured style-sheet + venue spec + empty-required compliance slots' },
    { title: 'Components', detail: 'equations + display items + references (no fabricated DOIs)' },
    { title: 'Draft',      detail: 'one-pen draft from the frozen skeleton + components' },
    { title: 'Verify',     detail: 'retrieval-gated cross-model domain lenses (numeric/provenance/argument/domain)' },
    { title: 'Review',     detail: 'reviewer synthesis -> single-hand revision; loop to clean' },
    { title: 'DeAI',       detail: 'surgical diff-gated de-AI + style-mimic, content FROZEN; venue-reviewer gate' },
  ],
}

const A = args || {};
const TYPE = A.deliverableType || 'journal-paper';
const VENUE = A.venue || '(unspecified venue — house style)';
const PROFILE = A.domainProfile === 'humanities' ? 'humanities' : 'stem';
const OUT = A.outputPath || '/tmp/mark1_article.md';
const RULES = (A.ownerWritingRules || []).join(' | ') || '(none captured — ask the operator)';
const STRUCT = {
  'journal-paper':'IMRaD (empirical) / Problem-Approach-Evaluation-Related-work (method); one spine, one claim, tight; reporting checklist if applicable',
  'review-synthesis':'bound by the matching standard (PRISMA 2020+S / PRISMA-ScR / SANRA / RAMESES per the declared review type); GAP ANALYSIS section required; humanities: primary-vs-secondary, no forced PRISMA diagram',
  'book-chapter':'thematic/argumentative (NOT IMRaD): framing -> organized synthesis of sub-themes -> author positioning -> implications; narrative cohesion + citation breadth; follow the editor spec',
  'thesis-chapter':'self-contained mini-IMRaD/argument-chapter with explicit bridges to prior/next chapters + the central thesis claim; fuller methods/limitations (examiners reward demonstrated rigor + reflexivity)',
}[TYPE] || 'follow the venue author guide';

const TRUTH = `SOURCE OF TRUTH (ground EVERY fact here — do NOT invent verses, numbers, citations, DOIs, or dates):
${A.sourceOfTruth || '(operator must supply — until then every claim is FLAGGED for human verification)'}.
A claim not traceable to the source of truth is FLAGGED, never asserted. Citations: ${A.citationSource || 'operator-supplied; NO fabricated DOIs — omit a field rather than invent it'}.
OWNER WRITING RULES (apply every one, or it is a defect): ${RULES}.`;

const STYLE = `STYLE: deliverable=${TYPE}; venue=${VENUE}; structure=${STRUCT}.
House style governs structure/format/terminology/claim-hedging; the ANCHOR voice governs only sentence rhythm and
word choice WITHIN house constraints. Style anchor: ${A.styleAnchorPath || '(none — house style; declare LOW-CONFIDENCE)'}.
${A.styleSample ? 'A real sample was supplied — MEASURE a style-sheet from it (sentence-length variance/CV, function-word fingerprint, signature constructions, a never-does-this list).' : 'NO sample supplied — the style-sheet is LOW-CONFIDENCE / a guess; flag it and do not claim faithful voice mimicry.'}
Scope fidelity to scholarly register; do NOT clone a recognizable living author onto novel claims without consent + disclosure.`;

const ART = { type:'object', additionalProperties:false, required:['file_written','summary','for_the_writer'],
  properties:{ file_written:{type:'boolean'}, summary:{type:'string'}, for_the_writer:{type:'string'} } };
const DEFECT = { type:'object', additionalProperties:false, required:['lane','verdict','defects','load_bearing_unbacked'],
  properties:{ lane:{type:'string'}, verdict:{type:'string', enum:['clean','minor-issues','blocking-issues','abstain']},
    defects:{type:'array', items:{type:'object', additionalProperties:false,
      required:['where','severity','problem','fix','grounding'],
      properties:{ where:{type:'string'}, severity:{type:'string', enum:['blocking','serious','minor']},
        problem:{type:'string'}, fix:{type:'string'}, grounding:{type:'string', description:'source/row consulted (retrieval-gate)'} }}},
    load_bearing_unbacked:{type:'array', items:{type:'string'}, description:'load-bearing claims with NO fetched source backing (the worst fabrication risk)'} } };

// ---- FREEZE: skeleton + measured style-sheet + venue spec + compliance slots ----
phase('Freeze');
const SKELETON = { type:'object', additionalProperties:false, required:['title','thesis','sections','display_items','compliance_slots'],
  properties:{ title:{type:'string'}, thesis:{type:'string'},
    sections:{type:'array', items:{type:'object', additionalProperties:false, required:['n','heading','purpose','consequence'],
      properties:{ n:{type:'string'}, heading:{type:'string'}, purpose:{type:'string'},
        consequence:{type:'string', enum:['catastrophic','serious','cosmetic']} }}},
    display_items:{type:'array', items:{type:'object', additionalProperties:false, required:['kind','label','content'],
      properties:{ kind:{type:'string', enum:['table','figure','equation-block']}, label:{type:'string'}, content:{type:'string'} }}},
    compliance_slots:{type:'array', items:{type:'string'}, description:'empty-required: CRediT, Data/Code Availability, Competing Interests, AI-use disclosure'} } };
const skeleton = await agent(
  `You are the CONTENT DESIGNER. Read the source of truth and (if given) the style anchor, then FREEZE the article
spine for a ${TYPE} on ${VENUE}. ${TRUTH} ${STYLE}
Design the skeleton (answer-first thesis; C-C-C at section + paragraph scale; structure per ${STRUCT}); mark each
section's consequence; specify display items; and create empty-required COMPLIANCE SLOTS (CRediT, Data/Code
Availability, Competing Interests, AI-use disclosure). Return the frozen skeleton.`,
  { label:'designer:skeleton', phase:'Freeze', schema:SKELETON });
const styleSheet = await agent(
  `You are the WRITING-MIMIC analyst. ${STYLE}
${A.styleSample ? `Internalise this sample and MEASURE a concrete style-sheet (sentence-length mean+variance/CV, function-word fingerprint, how formulas/verses are introduced, the register, a never-does-this list).\nSAMPLE:\n${String(A.styleSample).slice(0,6000)}` : 'No sample — emit a neutral house-style sheet and DECLARE it low-confidence.'}
Return 6-10 imitable rules with a tiny before/after each + how the writer should use it.`,
  { label:'style:sheet', phase:'Freeze', schema:ART });
log(`Freeze: "${skeleton.title}" — ${skeleton.sections.length} sections; style-sheet ${A.styleSample?'measured':'low-confidence'}.`);

// ---- COMPONENTS ----
phase('Components');
const components = (await parallel([
  () => agent(`You are the COMPONENTS writer (equations/derivations if any). Using the frozen skeleton + ${TRUTH},
write the equation blocks the article needs, each with a one-line basis; define symbols once; pull constants from
the source of truth (do NOT invent). Return guidance for the writer.`, { label:'comp:equations', phase:'Components', schema:ART }),
  () => agent(`You are the DISPLAY-ITEMS maker (tables/figures). Using the frozen skeleton + ${TRUTH}, produce the
tables/figures; every cell carries a real source-of-truth value; tag uncertain cells. Return guidance.`, { label:'comp:display', phase:'Components', schema:ART }),
  () => agent(`You are the REFERENCE adder. Build the reference list of REAL sources actually used (from the source
of truth + library). Correct keys. ${'NO fabricated DOIs — omit a field rather than invent; flag any entry not fully confirmed.'} Return a key list + flags.`, { label:'comp:refs', phase:'Components', schema:ART }),
])).filter(Boolean);
log('Components: equations, display items, references prepared.');

// ---- DRAFT (one pen) ----
phase('Draft');
await agent(
  `You are the CONTENT WRITER — the SINGLE PEN. Write the WHOLE ${TYPE} to ${OUT}. Integrate ALL of: the FROZEN
skeleton (follow its sections + thesis; do not re-architect), the style-sheet (voice), the components
(equations/displays/refs — place per the skeleton). ${TRUTH} ${STYLE}
Mark every load-bearing number with unit + source + confidence; if a fact is not backed, write it hedged with a
"% TODO-VERIFY" rather than asserting. Fill the compliance slots; add the AI-use disclosure. WRITE the draft to
${OUT} (Write tool). Return a summary + section list.`,
  { label:'writer:draft', phase:'Draft', schema:ART });
log(`Draft v1 written to ${OUT}.`);

// ---- VERIFY -> REVIEW -> REVISE (<=2 rounds) ----
let verdict = 'revise';
for (let round = 1; round <= 2 && verdict !== 'publishable'; round++) {
  phase('Verify');
  const lenses = (A.reviewLenses && A.reviewLenses.length) ? A.reviewLenses
    : ['numeric/provenance: every number/citation traces to the source of truth; no fabricated DOI',
       'argument/hedging: every load-bearing claim carries grounds+warrant+limitation; certainty matches evidence; no overclaim',
       PROFILE==='humanities' ? 'sources: primary-vs-secondary handled right; translations word-anchored; provenance/edition correct'
                              : 'domain: methods/units/derivations sound and grounded'];
  const checks = (await parallel(lenses.map((lens,i) => () => agent(
    `You are a VERIFIER (cross-model ≠ the writer), lens: ${lens}. Read the draft ${OUT}. RETRIEVAL-GATE: open the
source of truth and compare; do not reason from memory. ${TRUTH} Return structured defects (severity + exact
location + concrete fix + the grounding you consulted). Verifiers do NOT edit.`,
    { label:`verify:lens${i+1}:r${round}`, phase:'Verify', schema:DEFECT }))) ).filter(Boolean);
  phase('Review');
  const REVIEW = { type:'object', additionalProperties:false, required:['verdict','revision_list'],
    properties:{ verdict:{type:'string', enum:['publishable','revise','major-revise']},
      revision_list:{type:'array', items:{type:'object', additionalProperties:false, required:['priority','instruction'],
        properties:{ priority:{type:'string', enum:['must','should','nice']}, instruction:{type:'string'} }}} } };
  const review = await agent(
    `You are the REVIEWER (a ${VENUE} referee). Given specialist reports on ${OUT}: ${JSON.stringify(checks).slice(0,9000)}
Read the draft yourself; synthesize a prioritized REVISION LIST (must/should/nice). Any load-bearing claim left
unbacked is a blocking defect. Verdict 'publishable' only if no blocking defects remain.`,
    { label:`review:r${round}`, phase:'Review', schema:REVIEW });
  verdict = review.verdict;
  log(`Review r${round}: ${verdict} — ${review.revision_list.filter(r=>r.priority==='must').length} must-fix.`);
  if (verdict !== 'publishable') {
    const musts = review.revision_list.filter(r => r.priority !== 'nice');
    await agent(`You are the SINGLE PEN. Apply this revision list to ${OUT} IN PLACE (single hand; keep it
compilable/clean). Fix every 'must'; re-ground flagged claims against the source of truth; if still unbackable,
hedge + "% TODO-VERIFY". Introduce NO new unsupported claims. List: ${JSON.stringify(musts).slice(0,9000)}`,
      { label:`writer:revise-r${round}`, phase:'Review', schema:ART });
  }
}

// ---- DE-AI (surgical, diff-gated, content FROZEN) + venue-reviewer gate ----
phase('DeAI');
const aiflags = await agent(
  `You are the DE-AI checker. Read ${OUT}. Flag AI-tells (uniform sentence length, list-itis, hollow connectives,
hedge-stacking, em-dash tics, robotic parallelism, generic topic sentences) with SPECIFIC locations + the tell.
Propose NO meaning changes — only what to re-voice toward the measured style-sheet. A detector is NOT a gate.`,
  { label:'deai:flags', phase:'DeAI', schema:DEFECT });
await agent(
  `You are the SINGLE PEN. Apply surgical, DIFF-GATED de-AI edits to ${OUT}: re-voice the flagged passages toward
the style-sheet, but CHANGE NO fact/number/citation/quote/section and do NOT strip a necessary hedge. Prove
content-invariance (numbers/citations unchanged). Flags: ${JSON.stringify(aiflags.defects||[]).slice(0,8000)}.
Overwrite ${OUT}.`,
  { label:'deai:apply', phase:'DeAI', schema:ART });
const GATE = { type:'object', additionalProperties:false, required:['worthy','blocking','disclosure_present'],
  properties:{ worthy:{type:'boolean'}, blocking:{type:'array', items:{type:'string'}}, disclosure_present:{type:'boolean'} } };
const gate = await agent(
  `You are the ${VENUE} REVIEWER (final gate). Read ${OUT}. Is it human-authored-quality, rigorous, properly hedged,
content intact, with the AI-use disclosure present and NO AI-detector used as a gate? Return worthy=true only if you
would forward it with no language blockers; list any blockers. Also confirm: no fabricated DOI, every load-bearing
number has a source or a VERIFY-IT-YOURSELF flag.`,
  { label:'gate:venue', phase:'DeAI', schema:GATE });
log(`Venue gate: worthy=${gate.worthy}${gate.blocking?.length?' — '+gate.blocking.join('; '):''}`);

return { output: OUT, deliverable_type: TYPE, venue: VENUE, profile: PROFILE,
  task1_verdict: verdict, venue_worthy: gate.worthy, disclosure_present: gate.disclosure_present,
  note: `${TYPE} drafted (one-pen) + cross-model verified + surgical de-AI on the Mark Article engine. ${A.verifyCmd?'Run venue verify cmd: '+A.verifyCmd:''}` };
