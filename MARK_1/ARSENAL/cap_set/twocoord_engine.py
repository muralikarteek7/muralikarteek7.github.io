#!/usr/bin/env python3
"""2-COORDINATE representation check: slice F_3^7 by coords (0,1) into a 3x3 grid of F_3^5 cells.
Cap iff each cell-cap in F_3^5 AND every AG(2,3) line of cells is transversal-free.
Baseline = product (4-cap in AG(2,3) x 45-cap each = 180). We build it, verify, and try structured
extension. Honest grounding: 180 < 236 -> this representation STARTS BEHIND the 1-coord C-F. All gate-certified."""
import itertools, json
from capset_verify import is_capset
from verified_caps_45_90 import CAP45
D45=[tuple(p) for p in CAP45]
F5=list(itertools.product(range(3),repeat=5))
F2=list(itertools.product(range(3),repeat=2))

def add5(a,b): return tuple((a[i]+b[i])%3 for i in range(5))
def is_ag2_line(c1,c2,c3):  # 3 distinct cells summing to 0 mod 3
    return len({c1,c2,c3})==3 and all((c1[k]+c2[k]+c3[k])%3==0 for k in range(2))

def assemble(cells):  # cells: dict (i,j)->list of F_3^5 points
    pts=[]
    for (i,j),S in cells.items():
        for s in S: pts.append((i,j)+s)
    return pts

# baseline: a 4-cap in AG(2,3)
fourcap=[(0,0),(1,0),(0,1),(1,1)]
# confirm it's a cap (no 3 summing to 0)
assert not any(is_ag2_line(a,b,c) for a,b,c in itertools.combinations(fourcap,3)), "not a 4-cap"
cells={c:D45 for c in fourcap}
prod=assemble(cells)
v,r=is_capset(prod)
print(f"2-coord PRODUCT (4 cells x 45): size={len(prod)} valid={v} ({r})   [vs 1-coord C-F = 236]")

# structured extension: try adding each remaining cell with CAP45 + a translate t, keep if F_3^7 stays a cap
import random
rng=random.Random(0)
best=len(prod); best_cells=dict(cells)
improved=True
while improved:
    improved=False
    for c in F2:
        if c in best_cells: continue
        for _ in range(40):
            t=rng.choice(F5)
            trial=dict(best_cells); trial[c]=[add5(s,t) for s in D45]
            pts=assemble(trial)
            v,_=is_capset(pts)
            if v and len(pts)>best:
                best=len(pts); best_cells=trial; improved=True
                print(f"  + cell {c} (translate {t}) -> total {best}")
                break
print(f"\nbest 2-coord construction (product+greedy translate-extension): {best}  (vs 236)")
v,r=is_capset(assemble(best_cells)); print(f"  certify: valid={v} ({r})")
print(f"  VERDICT: 2-coord product/extension reaches {best} {'>' if best>236 else '<='} 236 -> "
      + ("BEATS 236 (audit!)" if best>236 else "below 236; this representation is NOT near a breakthrough (starts at 180)."))
