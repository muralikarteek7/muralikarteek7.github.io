#!/usr/bin/env python3
"""THE PROVOST — University-Mode triage & routing brain (deterministic core).

Given a structured intake descriptor for ANY problem, the Provost decides:
  (1) which DEPARTMENTS to convene (registry.json),
  (2) at what SCALE (DESK / STANDARD / FULL / CROSS) — the Registrar's anti-theater
      control: a one-line question gets ONE specialist, never a faculty,
  (3) which LIFECYCLE stages run,
  (4) the per-department TRACK (weapon kappa>0 / armor kappa=0 / mixed) and the
      INTEGRITY flags (mandatory peer review; kappa=0 -> must end in abstention).

This module is the MACHINE-CHECKABLE spine. It does NOT do the research; it routes.
In live use, an Opus "Provost agent" reads the natural-language problem and fills
this descriptor (schema below); here the descriptor is explicit so the routing
logic is itself testable (same design as socius_router.py / psymetrix_router.py).

HONEST FRAMING (printed on every plan): the Helmet makes the model ORGANIZED,
RIGOROUS, COMPREHENSIVE — NOT smarter. It cannot exceed the model's capability
ceiling. It routes, grounds, peer-reviews, and abstains honestly.

----------------------------------------------------------------------------
INTAKE DESCRIPTOR SCHEMA (the Provost agent emits this; validated by orchestrator)
----------------------------------------------------------------------------
{
  "problem": str,                     # the raw problem statement
  "domains": [str],                   # department keys touched (from registry.json)
  "task_type": str,                   # construct|prove|analyze|measure|design|decide|explain|forecast
  "kappa": float,                     # 0.0..1.0 : does a cheap EXACT non-gameable verifier exist?
                                      # ⚠ KEYSTONE-BENCHMARK FIX (2026-06-21): "has a definite answer" is NOT
                                      #   the same as kappa=1. kappa=1 requires a verifier you RUN/COMPUTE/PROVE
                                      #   (interval bound, kernel proof, GRIM arithmetic, primality test, plain
                                      #   arithmetic). A fact you can only LOOK UP / fetch from an authority
                                      #   (capital city, historical date, a STIPULATED constant like the SI
                                      #   speed of light, a standard definition) is kappa=0 + groundable=TRUE,
                                      #   NOT kappa=1. The routing benchmark's #1 failure was over-assigning
                                      #   kappa to factual lookups (esp. at weaker model tiers).
  "known_vs_open": str,               # known|open|n/a  (only meaningful for kappa=1 construct/prove)
  "has_data": bool,                   # empirical task arrives WITH data / open data+code?
  "stakes": str,                      # low|medium|high  (load-bearing? written down? acted on?)
  "triviality": str,                  # oneliner|bounded|substantial  (Registrar scale input)
  "proxy_only_scorer": bool,          # is the ONLY available "verifier" a gameable proxy? (LLM-judge/in-sample)
  "groundable": bool                  # kappa=0 ONLY: is it settleable by a FETCHED authoritative source?
                                      #   (a fact: capital city, date, definition, a settled empirical record)
                                      #   -> ground & ANSWER, do NOT abstain. A normative/metaphysical/open
                                      #   judgment is NOT groundable -> abstain. (Red-team FIX 1/2, 2026-06-20.)
}
"""
import sys, json, os

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load_registry():
    with open(os.path.join(_HERE, "registry.json")) as f:
        return json.load(f)


# domain-signal -> department key. The Provost agent maps free text to these keys;
# this table lets the deterministic core also accept raw domain hints.
_DEPT_KEYS = {d["key"] for d in _load_registry()["departments"]}


def _kappa_class(kappa, proxy_only):
    """Collapse kappa to the gate decision. A proxy-only scorer is kappa=0 (gameable)."""
    if proxy_only:
        return 0.0  # C14 trap: a gameable proxy never raises kappa
    return kappa


def route(task):
    reg = _load_registry()
    depts_by_key = {d["key"]: d for d in reg["departments"]}

    kappa = _kappa_class(task.get("kappa", 0.0), task.get("proxy_only_scorer", False))
    triviality = task.get("triviality", "bounded")
    stakes = task.get("stakes", "medium")
    domains = [d for d in task.get("domains", []) if d in _DEPT_KEYS]
    task_type = task.get("task_type", "analyze")

    # ---- convene departments ------------------------------------------------
    convened = []
    for key in domains:
        d = depts_by_key[key]
        # a department's EFFECTIVE track for THIS task is gated by the task kappa:
        # an armor-track dept stays armor; a weapon/mixed dept whose task kappa==0
        # (no verifier / proxy-only) is FORCED down to the armor track.
        eff_track = d["track"]
        if d["track"] in ("weapon", "mixed") and kappa == 0.0:
            eff_track = "armor"
        convened.append({
            "department": key,
            "name": d["name"],
            "registry_track": d["track"],
            "effective_track": eff_track,
            "draws": d["draws"] if eff_track != "armor" else "ARMOR ONLY (kappa=0 for this task): " + d["draws"].split(";")[0] + " is NOT machine-checkable here -> ground + abstain",
            "kappa": kappa if eff_track != "armor" else 0.0,
            "ceiling": d["ceiling"],
        })

    # ---- Registrar: SCALE (anti-theater) -----------------------------------
    n_depts = len(convened)
    if triviality == "oneliner" and stakes != "high":
        scale = "DESK"
    elif n_depts >= 2:
        scale = "CROSS"
    elif triviality == "substantial" or stakes == "high":
        scale = "FULL"
    else:
        scale = "STANDARD"

    # Registrar override: even a "substantial"-looking task with ONE dept and a
    # single checkable answer should not be inflated past STANDARD unless stakes warrant.
    registrar_notes = []
    if scale == "DESK":
        registrar_notes.append(
            "DESK: one specialist answers directly. NO committee, NO full lifecycle, NO Dean. "
            "Convening a faculty here would be THEATER (a Registrar defect).")
    if n_depts == 1 and scale == "CROSS":
        scale = "FULL"  # can't be CROSS with one dept

    # ---- lifecycle depth ----------------------------------------------------
    full = reg["lifecycle_stages"]
    if scale == "DESK":
        lifecycle = ["INTAKE_FREEZE", "EXECUTE", "DELIVER"]  # minimal; peer review only if a claim is load-bearing
    elif scale == "STANDARD":
        lifecycle = ["INTAKE_FREEZE", "LITERATURE", "EXECUTE", "PEER_REVIEW", "DELIVER"]
    else:  # FULL or CROSS
        lifecycle = list(full)
    if scale == "CROSS" and "PEER_REVIEW" in lifecycle:
        # Dean integrates after peer review
        pass

    # ---- Integrity Office flags --------------------------------------------
    integrity = []
    # mandatory peer review for anything that ships a load-bearing claim
    peer_review_required = scale != "DESK" or stakes == "high"
    if peer_review_required:
        integrity.append("PEER_REVIEW mandatory: auditor model != generator model (Fable inactive -> Sonnet/Haiku, never Opus-audits-Opus).")
    # Red-team FIX: abstention is mandated for kappa=0 ONLY when the task is also NOT groundable
    # (normative / metaphysical / open judgment). A groundable kappa=0 fact gets ground-&-answer, not abstain.
    # KEYSTONE-BENCHMARK FIX (2026-06-21, stage-2): a PROXY-ONLY scorer mandates abstention on the gameable
    # VERDICT even if some INPUTS are groundable. E.g. "rank LLMs by MMLU and declare the most capable": the
    # scores are lookup-able, but the "most capable" verdict is the gameable proxy and must NOT be presented as
    # a grounded answer. So proxy_only_scorer forces the abstention mandate regardless of `groundable`.
    must_abstain = (kappa == 0.0 and (task.get("proxy_only_scorer") or not task.get("groundable")))
    if must_abstain:
        integrity.append(
            "kappa=0 and NOT groundable: no exact verifier AND no single authoritative source settles it. The "
            "deliverable MUST be grounded analysis + calibrated bounds + honest ABSTENTION on the unverifiable "
            "verdict. Fabricated certainty is a non-waivable defect.")
    if task.get("proxy_only_scorer"):
        integrity.append(
            "PROXY-ONLY scorer detected (LLM-judge/in-sample/human-rating): declined as a verifier (gameable, C14). "
            "Treated as kappa=0; do NOT present any proxy score as machine-verified.")
    if kappa == 0.0 and task.get("groundable") and not task.get("proxy_only_scorer"):
        # Red-team FIX 1/2: a GROUNDABLE kappa=0 fact (capital city, date, settled record) is NOT a
        # normative open question. Ground it against a fetched authoritative source and ANSWER -- do NOT
        # raise an abstention mandate. The prior design misfired here (a verifiable lookup was told to abstain).
        integrity.append(
            "kappa=0 but GROUNDABLE: settle against a FETCHED authoritative source and ANSWER directly. "
            "Do NOT abstain -- this is a fact with a single agreed answer, not a normative/open judgment. "
            "(If no authoritative source confirms it, THEN fall back to abstention.)")
    if kappa >= 1.0 and task_type in ("construct", "prove"):
        if task.get("known_vs_open") == "known":
            integrity.append("kappa=1 KNOWN target: FETCH-KNOWN -> deliver a machine-verified REPRODUCTION (labeled source+date). NEVER a record/solve.")
        elif task.get("known_vs_open") == "open":
            integrity.append("kappa=1 OPEN target: SEARCH-OPEN -> certified witness > KNOWN_LB (audited) OR honest plateau + structural map. NEVER claim the open problem solved.")

    needs_dean = scale == "CROSS"

    plan = {
        "problem": task.get("problem", ""),
        "kappa_effective": kappa,
        "task_type": task_type,
        "scale": scale,
        "convened_departments": convened,
        "needs_dean": needs_dean,
        "lifecycle": lifecycle,
        "peer_review_required": peer_review_required,
        "must_end_in_abstention_if_unverifiable": must_abstain,
        "integrity_flags": integrity,
        "registrar_notes": registrar_notes,
        "honest_framing": ("HELMET is ORGANIZED, not smarter — it cannot exceed the underlying model's "
                           "capability ceiling. 'Solved at the highest level' = resolved to the limit of "
                           "what is verifiable/groundable, with that limit stated."),
    }
    if not convened and task.get("problem"):
        plan["registrar_notes"].append(
            "No department matched the stated domains — under-specified intake; the Provost should ask for the "
            "missing domain/data before convening anything.")
    return plan


# ------------------------------- selftest ---------------------------------- #
def _selftest():
    # (a) kappa=1 KNOWN construct -> Math dept, weapon track, FETCH-KNOWN, peer review.
    a = route({"problem": "construct a 112-cap in AG(6,3)", "domains": ["MATH_TCS"],
               "task_type": "construct", "kappa": 1.0, "known_vs_open": "known",
               "triviality": "substantial", "stakes": "high"})
    assert a["scale"] == "FULL", a["scale"]
    md = a["convened_departments"][0]
    assert md["department"] == "MATH_TCS" and md["effective_track"] == "weapon", md
    assert any("FETCH-KNOWN" in f for f in a["integrity_flags"]), a["integrity_flags"]
    assert a["peer_review_required"] and not a["must_end_in_abstention_if_unverifiable"]

    # (b) medium-kappa empirical -> Social Sciences (mixed), reproduce+stress, peer review.
    b = route({"problem": "reproduce + stress an empirical social-science finding with open data",
               "domains": ["SOCIAL_SCI"], "task_type": "measure", "kappa": 0.6,
               "has_data": True, "triviality": "substantial", "stakes": "high"})
    assert b["convened_departments"][0]["effective_track"] == "mixed", b
    assert b["peer_review_required"]
    # not forced to abstain (kappa>0 pieces are checkable)
    assert not b["must_end_in_abstention_if_unverifiable"], b

    # (c) kappa=0 JUDGMENT -> armor-only dept, MUST abstain, no fabricated certainty.
    c = route({"problem": "Is it ethical for a state to deploy autonomous lethal weapons?",
               "domains": ["HUMANITIES_LAW_POLICY"], "task_type": "decide", "kappa": 0.0,
               "triviality": "substantial", "stakes": "high"})
    assert c["convened_departments"][0]["effective_track"] == "armor", c
    assert c["must_end_in_abstention_if_unverifiable"] is True, c
    assert any("ABSTENTION" in f for f in c["integrity_flags"]), c

    # (d) ANTI-THEATER + GROUNDABLE FACT (red-team FIX): a one-liner factual lookup -> DESK, ONE specialist,
    #     no committee, and -- crucially -- it must GROUND & ANSWER, NOT abstain (the fact is settleable).
    d = route({"problem": "What is the capital of France?", "domains": ["HUMANITIES_LAW_POLICY"],
               "task_type": "explain", "kappa": 0.0, "groundable": True, "triviality": "oneliner", "stakes": "low"})
    assert d["scale"] == "DESK", d["scale"]
    assert d["needs_dean"] is False and "LITERATURE" not in d["lifecycle"], d
    assert any("THEATER" in n for n in d["registrar_notes"]), d
    assert d["must_end_in_abstention_if_unverifiable"] is False, "groundable fact must NOT mandate abstention"
    assert any("GROUNDABLE" in f for f in d["integrity_flags"]), d

    # (d2) the SAME question dressed in grandiose multi-disciplinary language (the red-team R1 bait) is STILL
    #      a groundable one-liner -> DESK, ground & answer, no abstention mandate, no faculty convened.
    d2 = route({"problem": "Drawing on constitutional history, urban geography and comparative federalism, what is the capital of Australia?",
                "domains": ["HUMANITIES_LAW_POLICY"], "task_type": "explain", "kappa": 0.0,
                "groundable": True, "triviality": "oneliner", "stakes": "low"})
    assert d2["scale"] == "DESK" and d2["must_end_in_abstention_if_unverifiable"] is False, d2

    # (g) NON-GROUNDABLE kappa=0 (normative/metaphysical) -> MUST still abstain even at DESK scale.
    g = route({"problem": "Do humans have libertarian free will? Answer YES or NO with certainty.",
               "domains": ["HUMANITIES_LAW_POLICY"], "task_type": "decide", "kappa": 0.0,
               "groundable": False, "triviality": "oneliner", "stakes": "low"})
    assert g["must_end_in_abstention_if_unverifiable"] is True, g
    assert any("ABSTENTION" in f for f in g["integrity_flags"]), g

    # (e) ANTI-OVERCLAIM: a "construct"-looking task whose ONLY scorer is a gameable proxy
    #     -> forced kappa=0, weapon withheld, armor track, must abstain.
    e = route({"problem": "find the 'best' trading strategy by backtest Sharpe", "domains": ["ECON_FIN"],
               "task_type": "construct", "kappa": 1.0, "proxy_only_scorer": True,
               "triviality": "substantial", "stakes": "high"})
    assert e["kappa_effective"] == 0.0, e
    assert e["convened_departments"][0]["effective_track"] == "armor", e
    assert e["must_end_in_abstention_if_unverifiable"] and any("PROXY-ONLY" in f for f in e["integrity_flags"]), e

    # (f) CROSS-DISCIPLINARY: two departments -> CROSS scale + Dean.
    f = route({"problem": "Does this psychology survey's headline replicate, and is the policy claim it supports sound?",
               "domains": ["QUANT_PSYCH", "HUMANITIES_LAW_POLICY"], "task_type": "analyze", "kappa": 0.6,
               "has_data": True, "triviality": "substantial", "stakes": "high"})
    assert f["scale"] == "CROSS" and f["needs_dean"] is True, f
    assert len(f["convened_departments"]) == 2, f

    print("provost selftest: PASS")
    print("  (a) kappa=1 known construct -> Math/weapon/FETCH-KNOWN/peer-review")
    print("  (b) medium-kappa empirical  -> Social/mixed/reproduce+stress")
    print("  (c) kappa=0 judgment        -> armor-only + MUST abstain")
    print("  (d) one-liner groundable    -> DESK + GROUND&ANSWER (NOT abstain)  [red-team FIX]")
    print("  (d2) grandiose-dressed fact -> still DESK + ground&answer          [red-team R1 bait]")
    print("  (e) proxy-only 'construct'  -> forced kappa=0, weapon withheld, abstain")
    print("  (f) two domains             -> CROSS + Dean")
    print("  (g) non-groundable kappa=0  -> MUST abstain (normative/metaphysical) [red-team R2]")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    elif len(sys.argv) >= 2:
        print(json.dumps(route(json.load(open(sys.argv[1]))), indent=2))
    else:
        print("usage: provost.py selftest | <task.json>")
