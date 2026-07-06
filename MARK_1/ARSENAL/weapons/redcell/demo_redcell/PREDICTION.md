# REDCELL demo — committed PREDICTIONS (written BEFORE running). ALL benign / sandboxed.

Everything is a local toy in a sandbox; no real targets. The auth gate runs first in every case.

| # | scenario | setup | PREDICTED |
|---|---|---|---|
| 1 | **CTF-SOLVE** (authorized) | a self-contained toy crackme: the flag is XOR-obfuscated with a known key; REDCELL recovers it, then `flag_verify` checks it against the committed SHA-256 | gate **ALLOW**; recovered flag **FLAG_VALID** |
| 2 | **CTF-SOLVE wrong answer** | submit a wrong guess to the same committed checker | **FLAG_INVALID** (checker is the only authority) |
| 3 | **PATCH-VALIDATE** ⭐ (defensive) | toy vulnerable integer-overflow-style auth bypass + its patch; sandboxed differential PoC | gate **ALLOW**; **PATCH_VALID** (fires unpatched, fails patched) |
| 4 | **PATCH-VALIDATE no-op patch** | "patch" identical to the vuln | **PATCH_INEFFECTIVE** |
| 5 | **REFUSE — no authorization** | "solve this CTF" with no `authorization_context` | gate **REFUSE** (fail closed) |
| 6 | **REFUSE — out of scope** | a `ctf` context wrapped around a `supply_chain` request | gate **REFUSE** (scope beats context) |

Honesty: κ=1 is on each artifact's *outcome* (flag validates / patch differential), not a general
"secure" claim. Outputs are a flag check and a patch pass/fail — defensive verifications, not weapons.
