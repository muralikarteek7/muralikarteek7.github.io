#!/usr/bin/env python3
"""weapon_draw.py — registry-backed weapon selector (v4 design: BOX_ARMOR_WEAPONS §3/§5).

Given a problem class (from router.route), return the cheapest registered weapon that
fires on it. Escalation is by marginal E=Q/B (DRAW-BY-MARGIN), encoded here as the
cost-tier ordering T0 < T1 < T2 < T3: the selector returns the lowest-tier match and
the caller escalates only if the bar is not cleared.

This module makes NO claims about results — it only selects. Every selected weapon's
output must pass weapon_gate.py before emission.
"""
import json, os

TIER_ORDER = {"T0": 0, "T1": 1, "T2": 2, "T3": 3}
REGISTRY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "WEAPON_REGISTRY.json")

# problem class -> weapon names eligible to fire on it (from each weapon's trigger/problem_class)
CLASS_TO_WEAPONS = {
    "KNOWN_RESULT_REPRODUCTION": ["W8_retrieval_grounded_structure_fetch",
                                   "W1_literature_grounded_structured_construction",
                                   "W2_exact_combinatorial_solver"],
    "OPEN_FRONTIER_DISCOVERY":   ["W3_metaheuristic_search",
                                   "W2_exact_combinatorial_solver",
                                   "W4_evolutionary_program_search"],
    "CHECKABLE_COMPUTATION":     ["W7_exact_symbolic_numerics",
                                   "W2_exact_combinatorial_solver"],
    "FETCHABLE_FACT":            ["W8_retrieval_grounded_structure_fetch"],
    "JUDGMENT_ONLY":             [],   # PURE_ARMOR: weapon=NONE, panel+abstention
}

def load_registry(path=REGISTRY_PATH):
    with open(path) as f:
        reg = json.load(f)
    by_name = {w["name"]: w for w in reg["weapons"]}
    return reg, by_name

def draw(problem_class, exclude=(), path=REGISTRY_PATH):
    """Return the cheapest eligible weapon entry for problem_class, or None (PURE_ARMOR).

    exclude: weapon names already tried/blocked (e.g. by the saturation tripwire) —
    the caller escalates by re-drawing with the failed weapon excluded.
    """
    _, by_name = load_registry(path)
    eligible = [by_name[n] for n in CLASS_TO_WEAPONS.get(problem_class, ())
                if n in by_name and n not in exclude]
    if not eligible:
        return None
    return min(eligible, key=lambda w: TIER_ORDER[w["cost_tier"]])

def ladder(problem_class, path=REGISTRY_PATH):
    """Full escalation ladder (cheapest first) for a problem class."""
    _, by_name = load_registry(path)
    elig = [by_name[n] for n in CLASS_TO_WEAPONS.get(problem_class, ()) if n in by_name]
    return sorted(elig, key=lambda w: TIER_ORDER[w["cost_tier"]])

if __name__ == "__main__":
    import sys
    pc = sys.argv[1] if len(sys.argv) > 1 else "KNOWN_RESULT_REPRODUCTION"
    w = draw(pc)
    print(json.dumps({"problem_class": pc,
                      "drawn": w["name"] if w else "NONE (PURE_ARMOR)",
                      "tier": w["cost_tier"] if w else None,
                      "ladder": [x["name"] for x in ladder(pc)]}, indent=2))
