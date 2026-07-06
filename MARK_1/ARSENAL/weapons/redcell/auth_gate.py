#!/usr/bin/env python3
"""REDCELL authorization gate — the centerpiece. FAILS CLOSED.

Encodes the operating security policy as a deterministic gate that runs BEFORE any
security logic. The default is REFUSE: a task proceeds only if it presents an explicit,
recognized authorization_context AND requests nothing in an out-of-scope category.

Policy (from system security guidance, see GROUNDING.md G1):
  ASSIST:  authorized security testing, defensive security, CTF, education.
  REFUSE:  destructive techniques, DoS, mass targeting, supply-chain compromise,
           detection-evasion for malicious purposes; any unauthorized/real-world target.
  Dual-use work REQUIRES a clear authorization context; absent it -> REFUSE.

Cardinal property (tested): the gate cannot be made to ALLOW by omission, by an unknown
context, by a malformed request, or by an in-scope-looking wrapper around an out-of-scope
action. Out-of-scope category beats any asserted context.
"""

# recognized authorization contexts (the ONLY values that can permit a task)
ALLOWED_CONTEXTS = {"ctf", "owned_system", "scoped_engagement", "sandbox_research", "education"}

# out-of-scope categories — refused REGARDLESS of any asserted authorization context.
# canonical key -> human description.
REFUSED_CATEGORIES = {
    "dos": "denial-of-service / availability attacks",
    "mass_targeting": "mass / indiscriminate targeting",
    "supply_chain": "supply-chain compromise",
    "malware_deployment": "malware built for deployment",
    "malicious_evasion": "detection-evasion intended for malicious use",
    "unauthorized_real_target": "an unauthorized or real-world third-party target",
}

# alias -> canonical key (audit fix D2: the blocklist was exact-match only, so
# 'ddos' / 'denial_of_service' / 'supply chain' / 'mass targeting' etc. slipped
# through as uncategorized). Spaces and hyphens are folded to underscores before
# lookup, so 'supply chain' and 'supply-chain' both resolve to 'supply_chain'.
_CATEGORY_ALIASES = {
    "ddos": "dos", "denial_of_service": "dos", "denial": "dos", "availability_attack": "dos",
    "mass_target": "mass_targeting", "indiscriminate": "mass_targeting", "spray": "mass_targeting",
    "botnet": "mass_targeting",
    "supplychain": "supply_chain", "dependency_compromise": "supply_chain",
    "malware": "malware_deployment", "ransomware": "malware_deployment", "dropper": "malware_deployment",
    "implant": "malware_deployment", "c2": "malware_deployment", "rootkit": "malware_deployment",
    "evasion": "malicious_evasion", "edr_evasion": "malicious_evasion", "av_evasion": "malicious_evasion",
    "antiforensics": "malicious_evasion", "anti_forensics": "malicious_evasion",
    "exfiltration": "unauthorized_real_target", "lateral_movement": "unauthorized_real_target",
    "unauthorized": "unauthorized_real_target", "real_target": "unauthorized_real_target",
}


def _norm(s):
    return str(s).strip().lower() if s is not None else ""


def _category_key(cat_raw):
    """Fold spaces/hyphens to underscores and resolve aliases -> a canonical refused
    key, or None if not a recognized refused category. (audit fix D2)"""
    import re as _re
    norm = _re.sub(r"[\s\-]+", "_", _norm(cat_raw))
    if norm in REFUSED_CATEGORIES:
        return norm
    return _CATEGORY_ALIASES.get(norm)


def authorize(task):
    """Classify a task BEFORE any security logic runs.

    task: dict with (at minimum):
      authorization_context : one of ALLOWED_CONTEXTS (REQUIRED; else REFUSE)
      scope                 : str, required & non-empty when context == 'scoped_engagement'
      requested_category    : optional declared category; if in REFUSED_CATEGORIES -> REFUSE
      target_is_owned_or_sandbox : bool; if explicitly False -> REFUSE (real target)
      mode                  : the REDCELL mode requested (ctf_solve / patch_validate / vuln_repro)

    Returns {allowed: bool, decision: 'ALLOW'|'REFUSE', reason, ...}. Default REFUSE.
    """
    if not isinstance(task, dict):
        return {"allowed": False, "decision": "REFUSE",
                "reason": "malformed task (not a structured request) -> fail closed"}

    ctx = _norm(task.get("authorization_context"))

    # 1. explicit, recognized context REQUIRED (missing/unknown -> fail closed)
    if ctx == "":
        return {"allowed": False, "decision": "REFUSE",
                "reason": "no authorization_context provided -> refuse by default (the gate fails closed)"}
    if ctx not in ALLOWED_CONTEXTS:
        return {"allowed": False, "decision": "REFUSE",
                "reason": f"unrecognized authorization_context '{task.get('authorization_context')}' "
                          f"-> fail closed. Allowed: {sorted(ALLOWED_CONTEXTS)}"}

    # 2. out-of-scope CATEGORY beats any asserted context (check BEFORE allowing).
    #    Type-confusion guard (audit fix D2): a non-string category (list/dict/number)
    #    fails closed rather than stringifying past the blocklist.
    cat_raw = task.get("requested_category")
    if cat_raw is not None and not isinstance(cat_raw, str):
        return {"allowed": False, "decision": "REFUSE",
                "reason": "requested_category must be a string -> fail closed on type confusion"}
    cat_key = _category_key(cat_raw)
    if cat_key is not None:
        return {"allowed": False, "decision": "REFUSE",
                "reason": f"requested action is out of scope: {REFUSED_CATEGORIES[cat_key]} "
                          f"-- refused regardless of the asserted '{ctx}' context (policy, non-waivable)"}

    # 3. a real / non-owned target is never permitted. (audit fix D1: was `owned is
    #    False`, an identity test that let an ABSENT key / None / 0 / "false" bypass.
    #    Now require an EXPLICIT boolean True -- fail closed on anything else.)
    owned = task.get("target_is_owned_or_sandbox")
    if owned is not True:
        return {"allowed": False, "decision": "REFUSE",
                "reason": "target_is_owned_or_sandbox must be explicitly True (owned/sandboxed); "
                          "absent / None / 0 / 'false' / a live third-party target -> refuse (fail closed)"}

    # 4. scoped_engagement requires an explicit non-empty scope
    if ctx == "scoped_engagement" and _norm(task.get("scope")) == "":
        return {"allowed": False, "decision": "REFUSE",
                "reason": "scoped_engagement requires an explicit non-empty 'scope' -> fail closed"}

    # 5. mode must be one of the three sandboxed/defensive modes
    mode = _norm(task.get("mode"))
    if mode not in {"ctf_solve", "patch_validate", "vuln_repro"}:
        return {"allowed": False, "decision": "REFUSE",
                "reason": f"unknown or missing mode '{task.get('mode')}' "
                          "(allowed: ctf_solve, patch_validate, vuln_repro) -> fail closed"}

    return {"allowed": True, "decision": "ALLOW",
            "authorization_context": ctx, "mode": mode,
            "reason": f"authorized: context='{ctx}', mode='{mode}', target owned/sandboxed, "
                      "no out-of-scope category requested",
            "note": "ALLOW permits ONLY a sandboxed, owned-target, defensive/authorized task. "
                    "The artifact is a verification (flag/patch/detection), not a deployable weapon."}


if __name__ == "__main__":
    # quick demonstration of the default-refuse behaviour
    examples = [
        {"label": "authorized CTF", "task": {"authorization_context": "ctf", "mode": "ctf_solve",
                                             "target_is_owned_or_sandbox": True}},
        {"label": "no context", "task": {"mode": "ctf_solve"}},
        {"label": "out-of-scope DoS w/ ctf wrapper",
         "task": {"authorization_context": "ctf", "mode": "ctf_solve", "requested_category": "dos"}},
        {"label": "real target", "task": {"authorization_context": "scoped_engagement",
                                          "scope": "acme.com", "mode": "vuln_repro",
                                          "target_is_owned_or_sandbox": False}},
    ]
    for e in examples:
        d = authorize(e["task"])
        print(f"{e['label']:32s} -> {d['decision']:7s} | {d['reason']}")
