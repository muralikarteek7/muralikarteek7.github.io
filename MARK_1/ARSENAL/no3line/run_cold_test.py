#!/usr/bin/env python3
"""Run the method's ROUTED weapons on no-3-in-line, validate vs the 2k ceiling.
Weapons: (A) algebraic single-parabola floor; (B) W-EVOLVE = randomized greedy + restarts.
Every reported set is certified by the FROZEN verify_no3line.py (is_valid)."""
import random, math
from verify_no3line import is_valid, score

def reduced_dir(dx, dy):
    g = math.gcd(abs(dx), abs(dy))
    dx, dy = dx//g, dy//g
    if dx < 0 or (dx == 0 and dy < 0): dx, dy = -dx, -dy  # normalize sign
    return (dx, dy)

def addable(p, chosen, dirs_by_point):
    # p addable iff no two chosen points share a direction from p (=> collinear through p)
    seen = set()
    for q in chosen:
        d = reduced_dir(q[0]-p[0], q[1]-p[1])
        if d in seen: return False
        seen.add(d)
    return True

def greedy(k, order):
    chosen = []
    for p in order:
        if addable(p, chosen, None):
            chosen.append(p)
    return chosen

def w_evolve(k, restarts):
    cells = [(x,y) for x in range(k) for y in range(k)]
    best = []
    for r in range(restarts):
        order = cells[:]; random.shuffle(order)
        c = greedy(k, order)
        if len(c) > len(best): best = c
    return best

def algebraic_parabola(p):
    # {(x, x^2 mod p)} on the p x p grid — classic; predict ~p points, no 3 collinear
    return [(x, (x*x) % p) for x in range(p)]

if __name__ == "__main__":
    random.seed(7)
    lines = []
    lines.append("### Ceiling check")
    lines.append("- Elementary ceiling = 2k (>=3 in a row would be collinear). [free, as predicted]\n")

    lines.append("### (P1) Algebraic single-parabola floor")
    for p in [7, 11, 13]:
        pts = algebraic_parabola(p)
        v, reason = is_valid(pts, p)
        lines.append(f"- k=p={p}: parabola size={len(pts)} valid={v} ({reason})  vs ceiling 2k={2*p}  -> ~k floor: {'YES' if v and len(pts)==p else 'NO'}")
    lines.append("")

    lines.append("### (P2/P3) W-EVOLVE (randomized greedy + restarts), certified by frozen verifier")
    lines.append("| k | 2k ceiling | W-EVOLVE best | reached 2k? | valid |")
    lines.append("|---|---|---|---|---|")
    summary = []
    for k in [5, 7, 10, 12, 16, 20]:
        rr = 4000 if k <= 12 else 1500
        best = w_evolve(k, rr)
        v, reason = is_valid(best, k)
        reached = (len(best) == 2*k)
        lines.append(f"| {k} | {2*k} | {len(best)} | {'✅' if reached else '❌ (-%d)'%(2*k-len(best))} | {v} |")
        summary.append((k, 2*k, len(best), reached, v))
        assert v, f"INVALID set at k={k}: {reason}"  # frozen verifier must pass

    # verdict on predictions
    small_reached = all(r for (k,c,n,r,v) in summary if k <= 10)
    large_plateau = any((not r) for (k,c,n,r,v) in summary if k >= 16)
    lines.append("")
    lines.append("### Verdict vs committed predictions")
    lines.append(f"- P1 (algebra ≈ k, half the ceiling): see parabola rows.")
    lines.append(f"- P2 (W-EVOLVE reaches 2k for small k≤10): **{'HELD' if small_reached else 'FAILED'}**")
    lines.append(f"- P3 (greedy plateaus below 2k as k grows): **{'HELD' if large_plateau else 'NOT OBSERVED'}**")

    out = "\n".join(lines)
    print(out)
    # append to the cold-test doc (machine-written results section)
    with open("COLD_TEST_2026-06-10.md", "a") as f:
        f.write("\n" + out + "\n")

# ---- Follow-up: is P2's failure a ROUTING error or a weak-v0-weapon error? ----
# Stronger instance of the SAME routed class: ILS (greedy -> perturb -> re-greedy), certified.
def ils(k, iters):
    cells = [(x,y) for x in range(k) for y in range(k)]
    order = cells[:]; random.shuffle(order)
    best = greedy(k, order)
    cur = best[:]
    for _ in range(iters):
        # perturb: drop ~15% random points, re-greedy from the survivors + shuffled rest
        keep = [p for p in cur if random.random() > 0.15]
        rest = [p for p in cells if p not in set(keep)]; random.shuffle(rest)
        c = greedy_from(k, keep, rest)
        if len(c) >= len(cur): cur = c
        if len(c) > len(best): best = c
    return best

def greedy_from(k, keep, rest):
    chosen = list(keep)
    for p in rest:
        if addable(p, chosen, None): chosen.append(p)
    return chosen

if __name__ == "__main__":
    random.seed(11)
    fu = ["\n### Follow-up: stronger instance of the routed weapon (ILS), certified"]
    fu.append("| k | 2k | greedy-v0 | ILS | ILS reaches 2k? |")
    fu.append("|---|---|---|---|---|")
    for k in [10, 12, 16]:
        g = w_evolve(k, 2000); 
        b = ils(k, 3000)
        vg,_ = is_valid(g,k); vb,reason = is_valid(b,k); assert vb, reason
        fu.append(f"| {k} | {2*k} | {len(g)} | {len(b)} | {'✅' if len(b)==2*k else '❌ (-%d)'%(2*k-len(b))} |")
    out = "\n".join(fu); print(out)
    with open("COLD_TEST_2026-06-10.md","a") as f: f.write("\n"+out+"\n")
