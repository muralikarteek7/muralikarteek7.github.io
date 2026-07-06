# CONTAMINATED first-run artifacts — DO NOT use as a result

These are from the FIRST A/B pass, which is VOID (see ../RESULT.md). Two contamination
vectors: (1) orchestrator-authored fix-hints in the repair prompts; (2) answer-key leakage —
tool-enabled Haiku provers read `reference_proofs.lean` off disk. They produced a FALSE +25pp.
Kept only as an audit trail of the caught false positive. The valid result is the CLEAN re-run
(../clean_*.json, ../RESULT.md): repair − best-of-3 = 0pp.
