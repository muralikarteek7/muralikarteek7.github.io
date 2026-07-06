#!/usr/bin/env python3
"""CTF-SOLVE verifier (kappa=1) — does a submitted flag validate?

Exact, non-judgmental: the submitted flag equals the challenge's committed flag
(compared constant-time to avoid a timing side-channel), or matches its committed
SHA-256 hash. A self-reported "I solved it" is never trusted — only the byte-exact
match against the committed checker counts.
"""
import hmac
import hashlib


def _consteq(a, b):
    return hmac.compare_digest(str(a).encode(), str(b).encode())


def verify_flag(submitted, *, expected=None, expected_sha256=None, fmt=None):
    """Validate a submitted CTF flag against a committed answer.

    Provide exactly one of expected (the literal flag) or expected_sha256 (its hash).
    `fmt`: optional expected wrapper regex-free prefix/suffix check, e.g. ('FLAG{', '}').
    """
    submitted = "" if submitted is None else str(submitted)
    result = {"mode": "CTF-SOLVE", "kappa": 1, "submitted_len": len(submitted)}

    if fmt is not None:
        pre, suf = fmt
        if not (submitted.startswith(pre) and submitted.endswith(suf)):
            result.update({"valid": False, "verdict": "WRONG_FORMAT"})
            return result

    if expected is not None:
        ok = _consteq(submitted, expected)
    elif expected_sha256 is not None:
        ok = _consteq(hashlib.sha256(submitted.encode()).hexdigest(),
                      str(expected_sha256).lower())
    else:
        result.update({"valid": False, "verdict": "NO_COMMITTED_ANSWER",
                       "note": "checker misconfigured: provide expected or expected_sha256"})
        return result

    result.update({"valid": bool(ok),
                   "verdict": "FLAG_VALID" if ok else "FLAG_INVALID",
                   "method": "constant-time exact" + (" hash" if expected_sha256 else "")})
    return result


if __name__ == "__main__":
    FLAG = "FLAG{x0r_15_n0t_crypt0}"
    import hashlib as _h
    digest = _h.sha256(FLAG.encode()).hexdigest()
    assert verify_flag(FLAG, expected=FLAG)["valid"] is True
    assert verify_flag("FLAG{wrong}", expected=FLAG)["valid"] is False
    assert verify_flag(FLAG, expected_sha256=digest)["valid"] is True
    assert verify_flag("not a flag", expected=FLAG, fmt=("FLAG{", "}"))["verdict"] == "WRONG_FORMAT"
    assert verify_flag("anything")["verdict"] == "NO_COMMITTED_ANSWER"
    print("flag_verify smoke: PASS (exact flag valid; wrong flag invalid; hash path works; "
          "format + misconfig handled)")
