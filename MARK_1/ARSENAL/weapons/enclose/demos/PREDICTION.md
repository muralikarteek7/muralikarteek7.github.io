# ENCLOSE — killer-demo PREDICTIONS (committed BEFORE running)

Box discipline: these verdicts are written down *first*. `run_demo.py` then runs the real gate and
asserts prediction == actual. A demo that confirms a prediction it could have written after the fact
proves nothing.

| # | problem | claim | PREDICTED verdict | why |
|---|---------|-------|-------------------|-----|
| 1 | ∫₀¹ 4/(1+x²) dx (= π) | [3.14, 3.15] | **ACCEPT** | rigorous enclosure E ⊆ claim |
| 2 | ∫₀¹ 4/(1+x²) dx (= π) | [3.0, 3.1] (fabricated) | **REJECT** | claim disjoint from E (π provably outside) |
| 3 | ∫₀¹ 4/(1+x²) dx (= π) | [3.1415, 3.1416] (true but tight) | **ABSTAIN** | true, but E (N=2000 rect rule) wider than claim → not independently provable |
| 4 | ∫₀¹ e^(−x²) dx (= 0.74682…, NON-elementary / erf) | [0.74, 0.75] | **ACCEPT** | E ⊆ claim — certifies a value with NO elementary closed form (where SYMBOLICA's symbolic leg struggles) |
| 5 | ∫₀¹ e^(−x²) dx | [0.80, 0.81] (fabricated) | **REJECT** | claim disjoint from E |
| 6 | unique root of x²−2 in box (= √2) | box [1.4, 1.45], unique=True | **ACCEPT** | Krawczyk K(X) ⊂ int(X) → existence + uniqueness |
| 7 | unique root of x²−2 in box | box [1.6, 1.7], unique=True (fabricated) | **REJECT** | no root there; Krawczyk fails → uniqueness NOT proven |
| 8 | unique root of x²−2 in box | box [1.0, 2.0] | **ABSTAIN** | f'(X)=2·[1,2]=[2,4] OK, but K(X) ⊄ int(X) at this width → REJECT (not ABSTAIN)… see note |

**Note on #8:** a wide box where Krawczyk is inconclusive returns REJECT ("uniqueness not proven for this
box"), NOT ABSTAIN — ABSTAIN is reserved for *inapplicable* (f'∋0) / malformed. Predicted: **REJECT**.

**The headline ENCLOSE claim being demonstrated:** the gate ACCEPTs a true enclosure, **REJECTs a
fabricated one (it can FAIL)**, ABSTAINs honestly when it cannot independently prove a tight true claim,
and certifies a non-elementary integral (erf) by containment proof — categorically sharper than
multi-method *agreement*. κ=1 under mpmath.iv's software directed rounding; certifies the computed
quantity, not the model (κ=0 boundary).
