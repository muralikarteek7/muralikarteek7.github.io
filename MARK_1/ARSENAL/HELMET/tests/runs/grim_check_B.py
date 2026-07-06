"""
GRIM (Granularity-Related Inconsistency of Means) Forensic Check
Problem B: Two Likert-scale means on a 1-7 scale
  - Paper 1: mean = 3.94, N = 18
  - Paper 2: mean = 5.19, N = 28

GRIM logic:
For a single integer-valued item (Likert), each response is an integer.
The sum of N integer responses is also an integer.
Therefore: mean * N must be an integer (or very close to one, within floating-point error).
If (mean * N) is NOT close to an integer, the mean is INCONSISTENT with N responses on
an integer-valued scale — a GRIM inconsistency.

NOTE: GRIM inconsistency is a mathematical impossibility — it flags means that cannot
arise from any set of integer responses with the stated N. It does NOT prove fraud.
"""

from fractions import Fraction
import math

def grim_check(mean_reported: float, N: int, scale_min: int, scale_max: int,
               decimal_places: int, label: str):
    """
    Check GRIM consistency for a single-item Likert mean.

    Returns whether the mean is CONSISTENT or INCONSISTENT.

    Key logic:
    - The true sum S = mean * N must be an integer.
    - We check whether mean * N rounds to an integer such that
      rounding that integer back to `decimal_places` gives back the reported mean.
    - We enumerate all integer sums S_cand in [N*scale_min, N*scale_max] and check
      if any produces a rounded mean matching the reported mean.
    """
    print(f"\n{'='*60}")
    print(f"GRIM check: {label}")
    print(f"  Reported mean : {mean_reported}")
    print(f"  N             : {N}")
    print(f"  Scale         : {scale_min}–{scale_max} (integer responses)")
    print(f"  Decimal places: {decimal_places}")
    print(f"{'='*60}")

    # Raw product
    raw_product = mean_reported * N
    print(f"\n  mean * N = {mean_reported} * {N} = {raw_product:.10f}")

    # Feasible integer sums: N * scale_min <= S <= N * scale_max
    S_min = N * scale_min
    S_max = N * scale_max
    print(f"  Feasible sum range: [{S_min}, {S_max}]")

    # Find candidate integer sums whose rounded mean matches the reported mean
    consistent = False
    matching_sums = []

    rounding_factor = 10 ** decimal_places

    for S_cand in range(S_min, S_max + 1):
        candidate_mean = S_cand / N
        # Round to the stated number of decimal places
        candidate_mean_rounded = round(candidate_mean, decimal_places)
        if abs(candidate_mean_rounded - mean_reported) < 1e-9:
            matching_sums.append(S_cand)
            consistent = True

    if consistent:
        print(f"\n  RESULT: CONSISTENT")
        print(f"  Matching integer sums: {matching_sums}")
        for S in matching_sums:
            print(f"    S={S} → mean={S/N:.{decimal_places}f}")
    else:
        print(f"\n  RESULT: GRIM INCONSISTENCY DETECTED")
        print(f"  No integer sum S in [{S_min}, {S_max}] produces a rounded mean of {mean_reported}")
        # Show nearest integer to mean*N for context
        nearest = round(raw_product)
        nearest_mean = nearest / N
        print(f"  Nearest integer sum: {nearest} → mean = {nearest_mean:.{decimal_places+2}f} "
              f"(rounds to {round(nearest_mean, decimal_places)})")
        print(f"  NOTE: INCONSISTENCY ≠ FRAUD. It means the reported mean is arithmetically")
        print(f"        impossible given integer responses and this N. It may indicate")
        print(f"        rounding, transcription error, or other reporting issue.")

    return consistent, matching_sums


def main():
    print("GRIM FORENSIC CHECK — Problem B")
    print("Scale: 1–7 Likert (single item, integer responses)")
    print()

    # Paper 1: mean=3.94, N=18
    c1, s1 = grim_check(
        mean_reported=3.94,
        N=18,
        scale_min=1,
        scale_max=7,
        decimal_places=2,
        label="Paper 1 (mean=3.94, N=18)"
    )

    # Paper 2: mean=5.19, N=28
    c2, s2 = grim_check(
        mean_reported=5.19,
        N=28,
        scale_min=1,
        scale_max=7,
        decimal_places=2,
        label="Paper 2 (mean=5.19, N=28)"
    )

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"  Paper 1 (mean=3.94, N=18): {'CONSISTENT' if c1 else 'GRIM INCONSISTENCY'}")
    print(f"  Paper 2 (mean=5.19, N=28): {'CONSISTENT' if c2 else 'GRIM INCONSISTENCY'}")
    print()

    # Show the arithmetic explicitly for transparency
    print("ARITHMETIC DETAIL:")
    print(f"  Paper 1: 3.94 × 18 = {3.94 * 18:.10f}  → nearest integer = {round(3.94*18)}")
    print(f"           {round(3.94*18)}/18 = {round(3.94*18)/18:.10f} → rounds to {round(round(3.94*18)/18, 2)}")
    print()
    print(f"  Paper 2: 5.19 × 28 = {5.19 * 28:.10f}  → nearest integer = {round(5.19*28)}")
    print(f"           {round(5.19*28)}/28 = {round(5.19*28)/28:.10f} → rounds to {round(round(5.19*28)/28, 2)}")


if __name__ == "__main__":
    main()
