#!/usr/bin/env python3
"""test_router.py — machine verification of router + weapon_draw + weapon_gate.

Includes the spec-mandated cap-set replay assertions (BOX_ARMOR_WEAPONS §6 'Validation')
and the §7 pilot: (a) 112 emits only with re-verified coordinates; (b) a fabricated
'n=7 = 240 optimal' claim with no qualifying object is VETOED.
Run: python3 test_router.py  -> exits 0 only if ALL pass.
"""
import json, os, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.join(_HERE, "benchmarks", "math"))

from router import (TaskSignature, signature_from_text, route, RunRecord,
                    saturation_tripwire, TRIPWIRE_CONFIG, classify, known_status_lookup)
from weapon_draw import draw, ladder
from weapon_gate import gate, EMIT, VETO, ABSTAIN, BUG

FAILURES = []

def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAILURES.append(name)

# ---------------------------------------------------------------------------
# GATE 1 — intake classification
# ---------------------------------------------------------------------------
# cap-set n=6 replay: a KNOWN-RESULT task must route GROUND-FIRST with search BLOCKED
sig6 = signature_from_text("Find a maximum cap set in AG(6,3); the proven maximum is 112.",
                           known_status="KNOWN")
r6 = route(sig6)
check("n=6 routes KNOWN_RESULT_REPRODUCTION", r6.problem_class == "KNOWN_RESULT_REPRODUCTION", str(r6))
check("n=6 search is BLOCKED behind structure-fetch", r6.search_blocked is True)
check("n=6 gate is GROUND_FIRST", r6.gate.startswith("GROUND_FIRST"))

# the drawn weapon for the KNOWN class must be a T0 grounding weapon, BEFORE any search weapon
w6 = draw("KNOWN_RESULT_REPRODUCTION")
check("KNOWN class draws a T0 weapon first", w6 is not None and w6["cost_tier"] == "T0", str(w6 and w6["name"]))
lad = [w["name"] for w in ladder("KNOWN_RESULT_REPRODUCTION")]
check("ladder puts fetch/structure before solver",
      lad.index("W8_retrieval_grounded_structure_fetch") < lad.index("W2_exact_combinatorial_solver"))

# n=7 is OPEN: search/derive must be the legitimate first move (NOT ground-first-blocked)
sig7 = signature_from_text("Find the largest cap set in AG(7,3); the maximum is open, best known LB 236.",
                           known_status="OPEN")
r7 = route(sig7)
check("n=7 routes OPEN_FRONTIER_DISCOVERY", r7.problem_class == "OPEN_FRONTIER_DISCOVERY", str(r7))
check("n=7 search NOT blocked", r7.search_blocked is False)

# Sidon known-k task must also route ground-first (out-of-sample arena, same rule)
sigS = signature_from_text("Construct an optimal Golomb ruler with 12 marks (proven optimal length 85).",
                           known_status="KNOWN")
rS = route(sigS)
check("Sidon k=12 routes KNOWN_RESULT_REPRODUCTION", rS.problem_class == "KNOWN_RESULT_REPRODUCTION")

# judgment-only task: PURE_ARMOR, weapon=NONE, auditable
rj = route(TaskSignature(judgment_only=True))
check("judgment-only routes PURE_ARMOR", rj.problem_class == "JUDGMENT_ONLY" and "weapon=NONE" in rj.gate)
check("judgment-only draws NO weapon", draw("JUDGMENT_ONLY") is None)

# ---------------------------------------------------------------------------
# GATE 2 — saturation tripwire on the HISTORICAL cap-set ladder (the replay)
# ---------------------------------------------------------------------------
# the actual 2026-06-09 history: greedy 80, ILS 88, exact CP-SAT 89 — three families
# clustered well under known bound 112. Tripwire MUST fire before more heavy spend.
history = [RunRecord("greedy", 80, 5, True),
           RunRecord("ILS", 88, 120, True),
           RunRecord("exact_cpsat", 89, 700, True)]
fired, reason = saturation_tripwire(history, known_bound=112)
check("tripwire fires at the historical 80/88/89 cluster (<112)", fired, reason)

# self-certified maximality (the 90 = 45x{0,1} product, provably maximal) must fire alone
fired2, reason2 = saturation_tripwire([RunRecord("product", 90, 10, True, self_certified_max=True)],
                                      known_bound=112)
check("tripwire fires on self-certified maximality", fired2, reason2)

# compute-without-gain hard stop: 3 long runs, no improvement
fired3, _ = saturation_tripwire([RunRecord("exact", 89, 750, False),
                                 RunRecord("exact_warm", 89, 1500, False),
                                 RunRecord("LNS", 85, 800, False)], known_bound=112)
check("tripwire fires on compute-without-gain hard stop", fired3)

# control: healthy early search (one cheap improving family) must NOT fire
fired4, _ = saturation_tripwire([RunRecord("greedy", 64, 1, True)], known_bound=112)
check("tripwire does NOT fire on healthy early search", not fired4)

# control: families clustered but AT the bound (target reached) must NOT fire
fired5, _ = saturation_tripwire([RunRecord("a", 112, 5, True), RunRecord("b", 112, 5, False),
                                 RunRecord("c", 110, 5, False)], known_bound=112)
check("tripwire does NOT fire when the bound is reached", not fired5)

# constants are config, not hard-code
check("tripwire constants live in a CONFIG dict", isinstance(TRIPWIRE_CONFIG, dict)
      and "K_FAMILIES" in TRIPWIRE_CONFIG)

# out-of-sample tripwire scenarios (audit D4 — NOT the cap-set episode)
# NOTE: these reduce tautology but the constants remain n-of-1 PROVISIONAL; the tripwire
# is EXCLUDED from the promotion claim (prereg amendment v2 #5).
f_oos1, _ = saturation_tripwire([RunRecord("sa", 50, 20, True), RunRecord("tabu", 51, 30, False)],
                                known_bound=100)
check("OOS: two families clustered at half the bound -> fires", f_oos1)
f_oos2, _ = saturation_tripwire([RunRecord("sa", 60, 20, True), RunRecord("tabu", 90, 30, True)],
                                known_bound=100)
check("OOS: two families FAR apart (60 vs 90) -> does NOT fire", not f_oos2)
f_oos3, _ = saturation_tripwire([RunRecord("a", 99, 5, True), RunRecord("b", 95, 5, False)],
                                known_bound=100)
check("OOS: cluster within 5% just below bound -> fires", f_oos3)

# ---------------------------------------------------------------------------
# AUTONOMOUS classification (audit D2 — no oracle injection)
# ---------------------------------------------------------------------------
ra6, st6, peg6 = classify("find a maximum cap set in AG(6,3)", arena="capset", param=6)
check("classify() resolves n=6 KNOWN from the grounded table (no oracle)",
      st6 == "KNOWN" and peg6 == 112 and ra6.problem_class == "KNOWN_RESULT_REPRODUCTION")
ra7, st7, peg7 = classify("find a maximum cap set in AG(7,3)", arena="capset", param=7)
check("classify() resolves n=7 OPEN despite regex matching 'cap set'",
      st7 == "OPEN" and ra7.problem_class == "OPEN_FRONTIER_DISCOVERY" and not ra7.search_blocked)
raS, stS, pegS = classify("construct a shortest Golomb ruler with 12 marks",
                          arena="sidon", param=12, fetched_pegs={10: 55, 12: 85, 14: 127})
check("classify() resolves Sidon k=12 KNOWN from FETCHED pegs", stS == "KNOWN" and pegS == 85
      and raS.problem_class == "KNOWN_RESULT_REPRODUCTION")
raU, stU, _ = classify("construct a shortest Golomb ruler with 30 marks",
                       arena="sidon", param=30, fetched_pegs={10: 55, 12: 85, 14: 127})
check("classify() with NO peg (k=30) does NOT fetch-gate on a regex hunch",
      stU == "UNKNOWN" and not raU.search_blocked)

# G2.1 regression: the regex must NOT fire inside ordinary words (the J4 'prOGRamming' defect)
for probe in ("the Python programming language", "a faster sorting algorithm",
              "the ogre in the story", "an optimally boring afternoon"):
    rp, sp, _ = classify(f"Which of these two summaries of {probe} is more accurate, A or B?")
    check(f"judgment probe routes JUDGMENT_ONLY: '{probe[:30]}...'",
          rp.problem_class == "JUDGMENT_ONLY", f"got {rp.problem_class}")
rg, _, _ = classify("find the optimal Golomb ruler OGR(12)")
check("legitimate OGR/Golomb text still matches the known-object regex",
      rg.problem_class != "JUDGMENT_ONLY")

# ---------------------------------------------------------------------------
# weapon_gate pilots (§7)
# ---------------------------------------------------------------------------
# pilot (a): the real 112 object emits as HONEST REPRODUCTION after independent re-verify
pts112 = json.load(open(os.path.join(_HERE, "benchmarks", "math", "cap_n6_size112.json")))["6"]
g_a = gate("capset", pts112, self_report={"size": 112, "optimal": True},
           producer="build_112_pathA", known={"status": "KNOWN", "max": 112})
check("pilot(a): verified 112 EMITs", g_a["verdict"] == EMIT, g_a.get("label"))
check("pilot(a): labeled honest REPRODUCTION (not a solve)", "REPRODUCTION" in g_a["label"])

# pilot (b): fabricated 'n=7 = 240 optimal' with NO object -> ABSTAIN (claimed number never emitted)
g_b1 = gate("capset", None, self_report={"size": 240, "optimal": True}, claims_optimal=True,
            producer="fabricator", known={"status": "OPEN", "lb": 236})
check("pilot(b1): no-object 240 claim -> ABSTAIN, number discarded", g_b1["verdict"] == ABSTAIN)

# pilot (b2): 'optimal' claimed on OPEN n=7 with an object that does NOT beat LB -> HARD VETO
pts224 = json.load(open(os.path.join(_HERE, "benchmarks", "math", "cap_n7_size224.json")))["7"]
g_b2 = gate("capset", pts224, claims_optimal=True, producer="overclaimer",
            known={"status": "OPEN", "lb": 236})
check("pilot(b2): 'optimal' on OPEN with 224<=236 -> VETO", g_b2["verdict"] == VETO, g_b2.get("label"))

# the same 224 object WITHOUT an optimality claim is an honest witness -> EMIT
g_b3 = gate("capset", pts224, producer="derive_mode", known={"status": "OPEN", "lb": 236})
check("224 without optimality claim EMITs as witness", g_b3["verdict"] == EMIT)
check("224 label contains no record claim", "no record" in g_b3["label"] or "witness" in g_b3["label"])

# invalid object (3 collinear points) -> VETO regardless of claims
bad = [(0,0,0,0,0,0), (0,0,0,0,0,1), (0,0,0,0,0,2)]
g_bad = gate("capset", bad, producer="fabricator", known={"status": "KNOWN", "max": 112})
check("invalid object -> VETO", g_bad["verdict"] == VETO)

# beats_optimal_IMPOSSIBLE: a 'valid 113' would be a BUG flag — simulate with a stub verifier
g_bug = gate("capset", [[0]*6]*113,
             verifier_fn=lambda obj: {"valid": True, "size": 113, "reason": "stubbed"},
             producer="buggy", known={"status": "KNOWN", "max": 112})
check("verified > proven optimum -> BUG flag, not a win", g_bug["verdict"] == BUG)

# Sidon gate sanity: Mian-Chowla k=10 is valid but sub-optimal -> EMIT without optimality
from arena2_sidon_verify import mian_chowla_greedy
mc10 = mian_chowla_greedy(10)
g_s = gate("sidon", mc10, producer="mian_chowla",
           known={"status": "KNOWN", "max": 55, "direction": "min"})
check("Sidon valid sub-optimal ruler EMITs honestly", g_s["verdict"] == EMIT
      and "no optimality claim" in g_s["label"], g_s.get("label"))

# Sidon trap: claiming a length-120 'optimal' k=14 ruler that is actually invalid/better-than-proven
g_strap = gate("sidon", list(range(14)),  # 0..13 is NOT a Sidon set (repeated diffs)
               claims_optimal=True, producer="fabricator",
               known={"status": "KNOWN", "max": 127, "direction": "min"})
check("Sidon invalid trap -> VETO", g_strap["verdict"] == VETO)

# audit D6: Sidon BUG path — a 'valid' ruler SHORTER than the proven optimum is a bug, not a win
g_sbug = gate("sidon", list(range(14)),
              verifier_fn=lambda obj: {"valid": True, "length": 120, "size": 14, "reason": "stubbed"},
              producer="buggy", known={"status": "KNOWN", "max": 127, "direction": "min"})
check("Sidon valid-but-beats-proven-optimum -> BUG flag", g_sbug["verdict"] == BUG)

# audit D5: optimality claimed with NO known-status consult -> VETO (was silent EMIT)
g_noknown = gate("capset", pts224, claims_optimal=True, producer="overclaimer", known=None)
check("claims_optimal with known=None -> VETO", g_noknown["verdict"] == VETO)

print()
if FAILURES:
    print(f"RESULT: {len(FAILURES)} FAILURES: {FAILURES}")
    sys.exit(1)
print("RESULT: ALL TESTS PASS")
