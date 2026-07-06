#!/usr/bin/env python3
"""equip.py — Mark 1 EQUIP phase: the pre-battle loadout selector.

WHERE IT SITS:  ...put on Mark 1 (load catalog) -> [ EQUIP: choose style + loadout ] -> kappa-gate (draw within loadout) -> fight.

The catalog (all 12 weapons + 8 kit) is LOADED at /mark1. EQUIP is the deliberate ritual that,
ONCE per battle, reads the task, picks a STYLE, and equips only that loadout — so the kappa-gate
then draws weapons from a curated rack instead of the whole armory. Deterministic (no LLM) so it
is unit-testable, exactly like router.py.

ARMOR boundary: EQUIP decides WHAT TO CARRY. It does not produce or verify any object — that is the
kappa-gate + weapons. The under-suit (ARMOR+LADDER+SHOES+VAULT+TRIAGE) is always on and not chosen.
"""
from __future__ import annotations
import json, re, sys
from dataclasses import dataclass, field
from pathlib import Path

LOADOUTS_PATH = Path(__file__).with_name("LOADOUTS.json")

# If >=2 styles land within this fraction of the top score, it's a multi-front battle -> WARLORD.
AMBIGUITY_BAND = 0.34
# Below this absolute top score, no style clearly fits -> default to SAGE (armor-only judgment).
MIN_CONFIDENCE = 1.0


@dataclass
class Loadout:
    style: str
    score: float
    weapons: list
    kit: list
    mode: str
    posture: str
    tagline: str
    matched: list = field(default_factory=list)


def _load_registry(path: Path = LOADOUTS_PATH) -> dict:
    return json.loads(path.read_text())


def _score_style(text: str, triggers: list) -> tuple[float, list]:
    """Word-boundary keyword match (router.py G2.1 lesson: bare substrings misroute).
    Multi-word triggers are matched as phrases. Score = number of distinct triggers hit."""
    t = text.lower()
    hits = []
    for kw in triggers:
        kw = kw.lower()
        if " " in kw:
            if kw in t:
                hits.append(kw)
        else:
            if re.search(r"\b" + re.escape(kw) + r"\b", t):
                hits.append(kw)
    return float(len(hits)), hits


def equip(battle_text: str, registry: dict | None = None) -> dict:
    """The equip ritual. Returns a dict: chosen style(s), the loadout(s), and a declaration."""
    reg = registry or _load_registry()
    styles = reg["styles"]

    scored = []
    for name, spec in styles.items():
        s, hits = _score_style(battle_text, spec.get("triggers", []))
        scored.append(Loadout(
            style=name, score=s, weapons=spec["weapons"], kit=spec["kit"],
            mode=spec["mode"], posture=spec["posture"], tagline=spec["tagline"], matched=hits,
        ))
    scored.sort(key=lambda l: l.score, reverse=True)
    top = scored[0]

    # No clear fit -> SAGE (armor-only). Never force a weapon onto a judgment task.
    if top.score < MIN_CONFIDENCE:
        sage = next(l for l in scored if l.style == "SAGE")
        return _result([sage], reg, warlord=False, reason="no clear weapon-fit -> armor-only SAGE")

    # Multi-front: other styles within the ambiguity band of the top (and actually scoring).
    band = top.score * (1 - AMBIGUITY_BAND)
    contenders = [l for l in scored if l.score >= band and l.score >= MIN_CONFIDENCE]
    if len(contenders) >= 2:
        contenders = contenders[:3]  # audit fix: cap the union at the top 3 fronts
        return _result(contenders, reg, warlord=True,
                       reason="multi-front: " + ", ".join(c.style for c in contenders))
    return _result([top], reg, warlord=False, reason=f"single dominant style: {top.style}")


def _result(loadouts: list, reg: dict, warlord: bool, reason: str) -> dict:
    always = reg["always_equipped"]
    weapons = sorted({w for l in loadouts for w in l.weapons})
    kit = {k for l in loadouts for k in l.kit} | set(always["kit"])
    if warlord:  # BOOTSTRAP is the router-failure meta-tool, reachable only via WARLORD
        kit |= set(reg["WARLORD"].get("meta_kit", []))
    kit = sorted(kit)
    return {
        "warlord": warlord,
        "styles": [l.style for l in loadouts],
        "reason": reason,
        "weapons_equipped": weapons,
        "kit_equipped": kit,
        "modes": [l.mode for l in loadouts],
        "postures": [l.posture for l in loadouts],
        "under_suit": always["kit"] + ["ARMOR", "LADDER"],
        "declaration": _declare(loadouts, weapons, kit, warlord),
        "_scores": {l.style: l.score for l in loadouts},
    }


def _declare(loadouts: list, weapons: list, kit: list, warlord: bool) -> str:
    names = " + ".join(l.style for l in loadouts)
    head = f"WARLORD ({names}) — multi-front, convening the Helmet" if warlord else f"{names} style"
    w = ", ".join(weapons) if weapons else "none (armor-only)"
    return (f"⚔️  EQUIPPED: {head}\n"
            f"    weapons: {w}\n"
            f"    kit:     {', '.join(kit)}\n"
            f"    under-suit always on: ARMOR · LADDER · SHOES · VAULT · TRIAGE")


if __name__ == "__main__":
    battle = " ".join(sys.argv[1:]) or "advise me on whether to migrate the database"
    r = equip(battle)
    print(r["declaration"])
    print(f"\n    reason: {r['reason']}")
    print(f"    scores: {r['_scores']}")
