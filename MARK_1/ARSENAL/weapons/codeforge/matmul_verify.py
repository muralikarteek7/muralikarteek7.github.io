#!/usr/bin/env python3
"""MATMUL — frozen EXACT verifier for bilinear matrix-multiplication schemes.  kappa = 1.

A scheme to multiply an (m x k) matrix A by a (k x p) matrix B using R scalar
multiplications is a rank-R decomposition of the matrix-mult tensor, given by three
integer/rational coefficient matrices:

    U  (R x m*k)   V  (R x k*p)   W  (m*p x R)
    m_r  = ( U[r] . vec(A) ) * ( V[r] . vec(B) )      r = 0..R-1   (the R products)
    C[t] = sum_r  W[t][r] * m_r                        t = 0..m*p-1

The scheme is CORRECT iff, treating every entry of A and B as an INDEPENDENT,
NON-COMMUTING symbol, the reconstructed C equals the true product A@B as a formal
polynomial identity. We verify this SYMBOLICALLY with sympy using non-commutative
symbols, so the certificate is valid for RECURSIVE application to block matrices
(Strassen's whole point), not merely for commutative scalars.

This mirrors how AlphaTensor's machine-found schemes are verified (Fawzi et al.,
Nature 610, 2022; see GROUNDING.md): a candidate is a tensor factorization and is
accepted only if the bilinear tensor equals the matrix-multiplication tensor EXACTLY.

Why this qualifies as a kappa=1 weapon verifier (non-gameable):
  * it re-derives the identity over FORMAL symbols (all A,B at once), from scratch;
  * it is independent of the producer;
  * a scheme tuned to pass specific NUMERIC test matrices but not the formal identity
    is CAUGHT (see _selftest rejects-gaming: the numeric sample-checker is fooled, the
    symbolic verifier is not);
  * the score R (#multiplications) is a STRUCTURAL property; R below the proven rank
    lower bound flags a BUG (impossible), never a "win".

Honest ceiling: it certifies the scheme computes A@B with exactly R scalar
multiplications. Whether R is a RECORD is a separate claim requiring the proven rank
lower bound from the literature (2x2 needs >=7 — Winograd 1971/Hopcroft-Kerr 1971;
see GROUNDING.md). We carry known bounds and LABEL a match a reproduction, never a
discovery. A verifier that cannot FAIL is not a verifier: see _selftest().
"""
import sys
import json
import sympy as sp

# Proven multiplicative-rank lower bounds (minimum #scalar mults), fetched (GROUNDING.md).
#   (m,k,p): rank.  2x2x2 = 7 (Strassen 1969; optimality Winograd 1971 / Hopcroft-Kerr 1971).
KNOWN_RANK = {(2, 2, 2): 7, (1, 1, 1): 1, (2, 2, 1): 2, (3, 3, 3): 23}  # 3x3<=23 (Laderman 1976; LB open)

CEILING = ("MATMUL certifies a bilinear scheme computes A@B with exactly R scalar "
           "multiplications via an EXACT non-commutative symbolic identity. It does NOT "
           "by itself prove R is a record — a match to a KNOWN_RANK is a labeled "
           "reproduction; R below a proven lower bound flags a BUG, never a discovery.")


def _shape_ok(U, V, W, m, k, p):
    R = len(U)
    if R == 0:
        return False, "empty scheme"
    if any(len(row) != m * k for row in U):
        return False, f"U rows must have length m*k={m*k}"
    if len(V) != R or any(len(row) != k * p for row in V):
        return False, f"V must be R x k*p = {R} x {k*p}"
    if len(W) != m * p or any(len(row) != R for row in W):
        return False, f"W must be m*p x R = {m*p} x {R}"
    return True, ""


def verify_bilinear_scheme(U, V, W, m, k, p):
    """EXACT symbolic verification of a bilinear matmul scheme for (m x k)*(k x p).

    Returns a verdict dict. valid=True iff the reconstructed C equals A@B as a
    NON-COMMUTATIVE polynomial identity in the entries of A and B (recursion-safe).
    """
    ok, why = _shape_ok(U, V, W, m, k, p)
    if not ok:
        return {"sub_weapon": "MATMUL", "kappa": 1, "valid": False,
                "verdict": "MALFORMED", "note": why, "ceiling_note": CEILING}
    R = len(U)

    # Non-commuting symbols for the entries of A (m x k) and B (k x p).
    A = sp.Matrix(m, k, lambda i, j: sp.Symbol(f"a_{i}_{j}", commutative=False))
    B = sp.Matrix(k, p, lambda i, j: sp.Symbol(f"b_{i}_{j}", commutative=False))
    a = [A[i, j] for i in range(m) for j in range(k)]   # vec(A), row-major
    b = [B[i, j] for i in range(k) for j in range(p)]   # vec(B), row-major

    # The R products: LEFT factor drawn from A, RIGHT factor from B (order preserved
    # so the identity holds for non-commuting block entries too).
    prods = []
    for r in range(R):
        left = sp.Add(*[sp.Rational(U[r][t]) * a[t] for t in range(m * k)])
        right = sp.Add(*[sp.Rational(V[r][t]) * b[t] for t in range(k * p)])
        prods.append(left * right)

    # Reconstruct C (m x p), row-major.
    Cvec = [sp.Add(*[sp.Rational(W[t][r]) * prods[r] for r in range(R)])
            for t in range(m * p)]

    # True product A@B, row-major.
    true_C = A * B
    true_vec = [true_C[i, j] for i in range(m) for j in range(p)]

    # Exact check: each entry difference must expand to 0 as a noncommutative poly.
    mismatches = []
    for t in range(m * p):
        if sp.expand(Cvec[t] - true_vec[t]) != 0:
            mismatches.append((t // p, t % p))

    valid = (len(mismatches) == 0)
    res = {
        "sub_weapon": "MATMUL", "kappa": 1,
        "shape": f"({m}x{k})*({k}x{p})", "num_mults": R, "naive_mults": m * k * p,
        "valid": bool(valid),
        "verdict": "VALID_BILINEAR_SCHEME" if valid else "NOT_A_VALID_SCHEME",
        "mismatched_C_entries": mismatches,
        "beats_naive": bool(valid and R < m * k * p),
        "note": (f"exact non-commutative identity holds: computes A@B with {R} "
                 f"multiplications (naive uses {m*k*p})" if valid else
                 f"identity FAILS at C entries {mismatches}"),
        "ceiling_note": CEILING,
    }
    rank = KNOWN_RANK.get((m, k, p))
    if valid and rank is not None:
        res["known_rank_bound"] = rank
        if R == rank:
            res["rank_status"] = "MATCHES_KNOWN_RANK"            # labeled reproduction
        elif R > rank:
            res["rank_status"] = "VALID_BUT_ABOVE_KNOWN_RANK"
        else:  # below a PROVEN lower bound is impossible => bug
            res["rank_status"] = "BELOW_PROVEN_RANK_=>_BUG"
            res["beats_optimal_IMPOSSIBLE"] = True
    return res


# ------------- reference schemes used by the self-test -------------
def naive_scheme(n):
    """The textbook n^3-multiplication scheme for (n x n)*(n x n), as (U,V,W)."""
    U, V, W = [], [], []
    # one product per (i,j,l): m = A[i,l]*B[l,j] contributing to C[i,j]
    index = {}
    r = 0
    for i in range(n):
        for j in range(n):
            for l in range(n):
                u = [0] * (n * n); u[i * n + l] = 1
                v = [0] * (n * n); v[l * n + j] = 1
                U.append(u); V.append(v); index[(i, j, l)] = r; r += 1
    R = r
    for i in range(n):
        for j in range(n):
            w = [0] * R
            for l in range(n):
                w[index[(i, j, l)]] = 1
            W.append(w)
    return U, V, W


def strassen_scheme():
    """Strassen's 1969 7-multiplication scheme for 2x2 (GROUNDING.md). vec row-major:
    A=[a00,a01,a10,a11], B=[b00,b01,b10,b11], C=[c00,c01,c10,c11]."""
    # M1=(a00+a11)(b00+b11) M2=(a10+a11)b00 M3=a00(b01-b11) M4=a11(b10-b00)
    # M5=(a00+a01)b11 M6=(a10-a00)(b00+b01) M7=(a01-a11)(b10+b11)
    U = [[1, 0, 0, 1], [0, 0, 1, 1], [1, 0, 0, 0], [0, 0, 0, 1],
         [1, 1, 0, 0], [-1, 0, 1, 0], [0, 1, 0, -1]]
    V = [[1, 0, 0, 1], [1, 0, 0, 0], [0, 1, 0, -1], [-1, 0, 1, 0],
         [0, 0, 0, 1], [1, 1, 0, 0], [0, 0, 1, 1]]
    # C00=M1+M4-M5+M7  C01=M3+M5  C10=M2+M4  C11=M1-M2+M3+M6
    W = [[1, 0, 0, 1, -1, 0, 1], [0, 0, 1, 0, 1, 0, 0],
         [0, 1, 0, 1, 0, 0, 0], [1, -1, 1, 0, 0, 1, 0]]
    return U, V, W


def _numeric_sample_check(U, V, W, m, k, p, samples):
    """A deliberately GAMEABLE checker: tests the scheme only on a fixed list of
    NUMERIC matrix pairs. Used by _selftest to show numeric sampling can be fooled
    while the symbolic verifier cannot."""
    R = len(U)
    for (Amat, Bmat) in samples:
        a = [Amat[i][j] for i in range(m) for j in range(k)]
        b = [Bmat[i][j] for i in range(k) for j in range(p)]
        mr = [sum(U[r][t] * a[t] for t in range(m * k)) *
              sum(V[r][t] * b[t] for t in range(k * p)) for r in range(R)]
        C = [sum(W[t][r] * mr[r] for r in range(R)) for t in range(m * p)]
        true = [sum(Amat[i][l] * Bmat[l][j] for l in range(k))
                for i in range(m) for j in range(p)]
        if C != true:
            return False
    return True


def _selftest():
    """passes-good / catches-broken / rejects-gaming."""
    # --- passes-good: Strassen 7-mult 2x2 ---
    U, V, W = strassen_scheme()
    r = verify_bilinear_scheme(U, V, W, 2, 2, 2)
    assert r["valid"] is True, r
    assert r["num_mults"] == 7 and r["beats_naive"] is True, r
    assert r["rank_status"] == "MATCHES_KNOWN_RANK", r

    # control: the naive 8-mult scheme is also valid (sanity that the verifier passes truth)
    Un, Vn, Wn = naive_scheme(2)
    rn = verify_bilinear_scheme(Un, Vn, Wn, 2, 2, 2)
    assert rn["valid"] is True and rn["num_mults"] == 8, rn

    # --- catches-broken: flip one Strassen W coefficient ---
    Wbad = [row[:] for row in W]
    Wbad[0][0] = 0  # drop M1 from C00 -> identity breaks
    rb = verify_bilinear_scheme(U, V, Wbad, 2, 2, 2)
    assert rb["valid"] is False, rb
    assert (0, 0) in [tuple(x) for x in rb["mismatched_C_entries"]], rb

    # --- rejects-gaming: a scheme tuned to NUMERIC samples but not the symbolic identity ---
    # Take naive-8 and DROP the product a01*b10 (contributes to C00). For any A,B with
    # a01==0 OR b10==0 it still matches numerically -> a numeric sample-checker is fooled;
    # the symbolic verifier CATCHES the missing term.
    Ug, Vg, Wg = naive_scheme(2)
    # find the product index whose U has a01 (index 1) and V has b10 (index 2)
    drop = next(r_ for r_ in range(len(Ug))
                if Ug[r_][1] == 1 and Vg[r_][2] == 1)
    for t in range(4):
        Wg[t][drop] = 0  # remove that product everywhere
    samples = [([[1, 0], [0, 1]], [[1, 2], [3, 4]]),   # a01=0
               ([[5, 0], [7, 8]], [[1, 0], [0, 1]])]   # a01=0
    assert _numeric_sample_check(Ug, Vg, Wg, 2, 2, 2, samples) is True, \
        "numeric sample-checker should be fooled by construction"
    rg = verify_bilinear_scheme(Ug, Vg, Wg, 2, 2, 2)
    assert rg["valid"] is False, rg  # symbolic identity catches the dropped term

    # --- malformed: wrong W shape ---
    rm = verify_bilinear_scheme(U, V, [[1, 2, 3]], 2, 2, 2)
    assert rm["verdict"] == "MALFORMED", rm

    print("MATMUL    selftest: PASS (Strassen->valid R=7, broken->caught, "
          "numeric-gaming->caught by symbolic identity, malformed->flagged)")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        _selftest()
    elif len(sys.argv) >= 2 and sys.argv[1] == "strassen":
        U, V, W = strassen_scheme()
        print(json.dumps(verify_bilinear_scheme(U, V, W, 2, 2, 2), indent=2))
    else:
        print("usage: matmul_verify.py selftest | strassen")
