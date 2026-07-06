# ENCLOSE — GROUNDING

Method anchors for the ENCLOSE weapon (rigorous interval/enclosure arithmetic returning a
guaranteed enclosure `[a,b]` provably containing a numeric quantity, with a containment proof as the
verifier). Every load-bearing claim below is tied to a source that was actually fetched; quotes are
verbatim from the fetched page/PDF. Where a source could not be opened, that is stated plainly.

Fetched on 2026-06-20 via WebSearch + WebFetch (PDFs extracted locally with `pdftotext`).

---

## Anchor 1 — Fundamental Theorem / Inclusion Property of Interval Arithmetic

**Claim it supports.** ENCLOSE's interval-rectangle-rule quadrature (and any interval evaluation of
`f`) is *rigorous* because the natural interval extension `F` of `f`, evaluated on a box `X`, returns
an **outer enclosure that provably contains the true range** of `f` over `X`. This is the theorem
that makes "evaluate on the interval, trust the result contains the truth" sound.

**Grounded summary.** The correctness criterion for interval arithmetic is the *Fundamental Theorem
of Interval Arithmetic*: evaluating an expression on intervals yields an interval that contains every
pointwise result obtained from points inside the argument intervals. The result was first proved by
Moore and later dubbed the "Fundamental Theorem" by Hansen and Rall; it is the formal guarantee that
an interval extension over-approximates (never under-approximates) the true range.

**Citation — verbatim spans fetched.**
Hickey, Ju, van Emden, *Interval Arithmetic: from Principles to Implementation*
(Brandeis / Univ. of Victoria; published in *J. ACM* 48(5), 2001).
URL: https://fab.cba.mit.edu/classes/S62.12/docs/Hickey_interval.pdf

- Statement of the theorem (Section 2, "Correctness"): *"The criterion for correctness of a
  definition of interval arithmetic is that the 'Fundamental Theorem of Interval Arithmetic' hold:
  when an expression is evaluated using intervals, it yields an interval containing all results of
  pointwise evaluations based on point values that are elements of the argument intervals."*
- The inclusion property (Section 3.1, "An Inclusion Property"): *"Let `p` be the real that results
  from evaluating `E` with real values a₁,…,aₙ substituted … Let `I` be the result of evaluating `E`
  with intervals I₁,…,Iₙ substituted … where a₁ ∈ I₁,…,aₙ ∈ Iₙ. The property then requires that
  `p ∈ I`."*
- Attribution to Moore: *"Moore ([16], Theorem 3.1) was the first to prove what was independently
  dubbed by Hansen [7] and Rall [20] to be 'The Fundamental Theorem of Interval Arithmetic'."*
  ([16] is R.E. Moore, *Interval Analysis*, Prentice-Hall, 1966.)
- Consequence (Lemma 2 discussion): *"when we evaluate an expression with canonical set extensions as
  interpretation for the function symbols, we obtain a set that contains all values it should contain
  according to the inclusion property."*

Primary textbook anchor (located, not full-text fetched — cite as the origin of Theorem 3.1):
R.E. Moore, R.B. Kearfott, M.J. Cloud, *Introduction to Interval Analysis*, SIAM 2009 —
https://books.google.com/books/about/Introduction_to_Interval_Analysis.html?id=tT7ykKbqfEwC
(Moore's original 1966 *Interval Analysis* is the source of the inclusion theorem; the Hickey paper
above gives the precise modern statement and the Moore attribution.)

---

## Anchor 2 — Krawczyk Operator / Interval-Newton: Verified Root Existence + Uniqueness

**Claim it supports.** ENCLOSE can certify that a function has **exactly one** root inside a box `X`
(not merely that a numerical solver converged there). The certificate is the Krawczyk containment
test: if the Krawczyk image `K(x₀, X, F)` lands inside the *interior* of `X`, a unique root of `F` in
`X` is proven.

**Grounded summary.** The Krawczyk operator is `K(x₀,[x],F) := x₀ − C·F(x₀) + (Id − C·[dF([x])])·([x]−x₀)`.
Two theorems make it a certificate: (i) every actual zero of `F` in `[x]` lies in `K(x₀,[x],F)` — so if
`K ∩ [x] = ∅` there is **no** root; and (ii) if `K(x₀,[x],F) ⊆ int[x]`, then `F` has **exactly one**
root in `[x]`. Existence comes from the Brouwer fixed-point theorem; uniqueness from invertibility of
the interval Jacobian enclosure. (Krawczyk 1969; Moore 1977 recognized the existence/uniqueness use;
formulated in Neumaier, *Interval Methods for Systems of Equations*, and used by Rump/Kearfott.)

**Citation — verbatim spans fetched.**
Lecture notes, *Interval Krawczyk and Newton method* (Jagiellonian Univ., Zgliczyński, CAP07 course).
URL: https://ww2.ii.uj.edu.pl/~zgliczyn/cap07/krawczyk.pdf
(PDF fetched and text-extracted locally.)

- Operator definition (Section 2.2, eq. 8): *"The Krawczyk operator is given by
  `K(x₀, [x], F) := x₀ − C F(x₀) + (Id − C [dF([x])]ᴵ)([x] − x₀)`."*
- The certifying theorem (Theorem 2): *"1. If x\* ∈ [x] and F(x\*) = 0, then x\* ∈ K(x₀, [x], F).
  2. If K(x₀, [x], F) ⊂ int [x], then there exists in [x] exactly one solution of equation
  F(x) = 0."*
- Companion interval-Newton statement (Theorem 1): *"if N(x₀, X) ⊂ X, then ∃! x\* ∈ X such that
  f(x\*) = 0"* and *"if N(x₀, X) ∩ X = ∅, then f(x) ≠ 0 for all x ∈ X"* — i.e. the same
  containment-implies-uniqueness / disjoint-implies-no-root structure.

The notes credit the existence half to the **Brouwer theorem** (*"By the Brouwer theorem it follows
that P has a fixed point x\* ∈ X"*) and the uniqueness half to invertibility of the Jacobian
enclosure `[Df(X)]`. Standard textbook reference for this result: A. Neumaier, *Interval Methods for
Systems of Equations*, Cambridge Univ. Press, 1990 (located via search; not full-text fetched).

---

## Anchor 3 — Computer-Assisted Proof with Validated Numerics (Lorenz / Smale's 14th)

**Claim it supports.** Certified/validated numerics is a real discipline that produces *real
mathematical proofs*, not just confident numbers. The flagship example is Warwick Tucker's rigorous,
interval-arithmetic proof that the Lorenz attractor exists — the resolution of Smale's 14th problem.

**Grounded summary.** Tucker (1999, *C. R. Acad. Sci. Paris*; full version *Found. Comput. Math.*
2002) gave a **computer-assisted proof** that the Lorenz equations support a robust strange attractor,
combining normal-form theory with rigorous (validated) numerical ODE integration in interval
arithmetic with directed rounding. The numerical core — a rigorous ODE solver bounding the flow and
its Poincaré map — is what carries the proof's burden, and it has since been independently formalized
and machine-checked in Isabelle/HOL. This is direct evidence that interval/enclosure methods certify
theorems.

**Citations — verbatim spans.**
1. Immler, *A Verified ODE Solver and the Lorenz Attractor*, *J. Automated Reasoning* (2018), PMC
   open-access. **Fetched.** URL: https://pmc.ncbi.nlm.nih.gov/articles/PMC6044317/
   - *"Shortly after, Warwick Tucker managed to give an affirmative answer by presenting a
     computer-assisted proof."*
   - *"The proof relies on a rigorous numerical ordinary differential equation (ODE) solver."*
   - *"Tucker used the library Profil/BIAS for an implementation of the Euler method in interval
     arithmetic."*
   - Abstract: *"A rigorous numerical algorithm, formally verified with Isabelle/HOL, is used to
     certify the computations that Tucker used to prove chaos for the Lorenz attractor … Algorithms
     include low level approximation schemes based on Runge–Kutta methods and affine arithmetic."*
2. W. Tucker, *The Lorenz attractor exists*, *C. R. Acad. Sci. Paris Sér. I Math.* 328 (1999)
   1197–1202. **Bibliographic record + published abstract located via search** (paper PDF on the
   author's site failed TLS verification; Springer/ScienceDirect copies paywalled — so this is cited
   from the search-surfaced published abstract, not a fetched full text):
   - Published abstract (per search): *"proves that the Lorenz equations support a strange attractor,
     as conjectured by Edward Lorenz in 1963 … the attractor is robust, i.e., it persists under small
     perturbations of the coefficients … The proof is based on a combination of normal form theory and
     rigorous numerical computations."*
   - DOI 10.1016/S0764-4442(99)80439-X. Full version: W. Tucker, *A Rigorous ODE Solver and Smale's
     14th Problem*, *Found. Comput. Math.* 2 (2002) 53–117 (Springer page paywalled:
     https://link.springer.com/article/10.1007/s002080010018).

(Companion certified-numerics landmark: Hales' Flyspeck project, the formal proof of the Kepler
conjecture, is widely cited as the other canonical example. Mentioned for completeness; not separately
fetched here — Anchor 3's grounding rests on the Tucker/Lorenz sources above.)

---

## Anchor 4 — Proof of Containment vs. Heuristic Agreement (the honesty distinction)

**Claim it supports.** ENCLOSE's guarantee is **categorically stronger** than a sibling tool
(SYMBOLICA) reporting that several methods *agree*. Multiple-method agreement is *corroboration*: the
methods can share a blind spot and all be wrong together. An interval/ball *containment* result is a
**proof** that the true value lies in `[a,b]` — bounded error, not consensus.

**Grounded summary.** Validated / self-validating numerics is defined by the property that the
*computed* result is mathematically guaranteed to bound the true result, accounting for rounding and
all error terms — a proof of containment, not a heuristic estimate. INTLAB (Rump) states this guarantee
explicitly; Arb (Johansson) realizes it as ball arithmetic `[m ± r]` carrying a rigorous radius. By
contrast, "several independent estimates landed near the same number" is evidence, not a bound: it
gives no certificate excluding a shared systematic error.

**Citations — verbatim spans.**
1. S.M. Rump, *INTLAB — INTerval LABoratory*, Institute for Reliable Computing, TU Hamburg.
   **Fetched.** URL: https://www.tuhh.de/ti3/rump/intlab/
   - Description: *"The Matlab/Octave toolbox for Reliable Computing."*
   - The guarantee: *"Any result is proved to be true under any circumstances, in particular covering
     rounding errors and all error terms."* — this is the "proof of containment" property, the thing
     that mere agreement cannot supply.
   - Authorship/institution: Prof. S.M. Rump, Institute for Reliable Computing, TUHH ("self-validating
     methods", "verified matrix factorizations").
2. F. Johansson, *Arb: Efficient Arbitrary-Precision Midpoint-Radius Interval Arithmetic*, IEEE
   Trans. Computers (2017). **Located via search** (arXiv copy:
   https://arxiv.org/pdf/1611.02831) — Arb represents reals as balls `[m ± r]` and propagates a
   rigorous radius so each result is a *proven* enclosure; cited here as the ball-arithmetic anchor
   for the same guarantee class. (Title + role confirmed via search result; not separately
   full-text fetched.)

The distinction in one line: **corroboration (SYMBOLICA: methods agree) bounds nothing and can share a
blind spot; containment (ENCLOSE: `truth ∈ [a,b]` by interval/ball arithmetic) is a proof with a
quantified error bound.** The INTLAB phrase *"proved to be true under any circumstances … covering
rounding errors and all error terms"* is the precise wording of that stronger guarantee.

---

## Anchor 5 — mpmath Interval Context (`mpmath.iv`) and Directed/Outward Rounding

**Claim it supports.** ENCLOSE's concrete arithmetic engine (mpmath's `iv` context) gives the
inclusion guarantee in floating point: `iv.mpf` is a closed interval `[a,b]`, and the basic guarantee
is `f(v) ⊆ f̂(v)` — the interval result is guaranteed to contain the true value. Endpoints are
arbitrary-precision and the enclosure is maintained by rounding outward.

**Grounded summary.** mpmath's documentation (Fredrik Johansson and contributors) defines `iv.mpf` as
a closed interval over arbitrary-precision floating-point endpoints and states the inclusion guarantee
explicitly. The *principle* that keeps this rigorous in finite precision is outward rounding — round
the lower endpoint down (toward −∞) and the upper endpoint up (toward +∞) — which is exactly the
mechanism the Hickey paper proves sound (Anchor 1's source). The mpmath docs also carry an honest
caveat that the `iv` support is experimental.

**Citations — verbatim spans.**
1. mpmath, *Contexts* documentation (Fredrik Johansson + mpmath contributors). **Fetched.**
   URL: https://mpmath.readthedocs.io/en/latest/contexts.html (also
   https://mpmath.org/doc/current/contexts.html)
   - Interval type: *"The `iv.mpf` type represents a closed interval [a,b]; that is, the set
     {x : a ≤ x ≤ b}, where a and b are arbitrary-precision floating-point values, possibly ±∞."*
   - The guarantee: *"the basic guarantee of interval arithmetic is that f(v) ⊆ f̂(v) for any input
     interval v."* and *"any sequence of interval operations will produce an interval that contains
     what would be the result of applying the same sequence of operations to the exact number."*
   - Honest caveat (verbatim from docs): *"The support for interval arithmetic in mpmath is still
     experimental, and many functions do not yet properly support intervals."*
2. Outward-rounding mechanism — grounded in the Hickey/Ju/van Emden paper (Anchor 1's fetched PDF),
   which proves directed outward rounding preserves the enclosure:
   URL: https://fab.cba.mit.edu/classes/S62.12/docs/Hickey_interval.pdf
   - *"In interval arithmetic, rounding need not lead to error. By rounding outward, correctness is
     maintained and rounding only has the effect of including some values that would have been left
     out were the result exact."* (Section 5.3.)
   - *"…by using outward rounding, i.e., rounding right endpoints toward positive infinity and left
     endpoints toward negative infinity. It is clear that this results in a sound approximation."*

**Honesty note on Anchor 5:** the mpmath *Contexts* page states the inclusion guarantee and the
arbitrary-precision endpoint definition, but it does **not** spell out, verbatim on that page, the
per-endpoint "round lower down / upper up" rule. The outward-rounding *principle* is therefore
grounded here on the Hickey paper (a peer-reviewed primary source proving it sound), not asserted from
mpmath's page. mpmath's `iv` implements this principle internally; treat the strength of ENCLOSE's
floating-point soundness as resting on mpmath's (experimental) implementation being faithful to it.

---

## Honest ceiling

Interval / ball methods certify the **computed** quantity: given the expression actually evaluated and
correct directed (outward) rounding, the returned `[a,b]` provably contains the true value of *that
expression*. They do **not** certify the modeling step — if the integral, equation, or formula handed
to ENCLOSE is the wrong model of the real question, a perfect enclosure of the wrong thing is still
wrong. And the containment proof is only as sound as the rounding implementation underneath it: here
that is mpmath's `iv` software rounding, which the mpmath docs themselves flag as *experimental*.
ENCLOSE should therefore claim "the computed quantity is provably in `[a,b]`, conditional on mpmath.iv's
rounding being correct," never "the answer to your problem is proven" — the proof is of containment,
not of relevance, and it inherits the trust boundary of its arithmetic backend.
