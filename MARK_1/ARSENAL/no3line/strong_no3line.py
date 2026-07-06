#!/usr/bin/env python3
"""STRONG weapon: exact CP-SAT for no-3-in-line. Reaches the optimum the weak ILS could not.
Removes the 'weak weapon' confound and settles L2 on this arena. Certified by frozen verifier."""
import sys, math, time
from ortools.sat.python import cp_model
from verify_no3line import is_valid

def lines_of(k):
    pts=[(x,y) for x in range(k) for y in range(k)]
    idx={p:i for i,p in enumerate(pts)}
    seen=set(); lines=[]
    for i in range(len(pts)):
        for j in range(i+1,len(pts)):
            a,b=pts[i],pts[j]
            dx,dy=b[0]-a[0],b[1]-a[1]
            g=math.gcd(abs(dx),abs(dy)); dx,dy=dx//g,dy//g
            if dx<0 or (dx==0 and dy<0): dx,dy=-dx,-dy
            # canonical line: anchor = walk back from a to grid edge
            ax,ay=a
            while 0<=ax-dx<k and 0<=ay-dy<k: ax,ay=ax-dx,ay-dy
            key=(ax,ay,dx,dy)
            if key in seen: continue
            seen.add(key)
            line=[]; cx,cy=ax,ay
            while 0<=cx<k and 0<=cy<k:
                line.append(idx[(cx,cy)]); cx,cy=cx+dx,cy+dy
            if len(line)>=3: lines.append(line)
    return pts,lines

def solve(k, tlimit=60):
    pts,lines=lines_of(k)
    m=cp_model.CpModel()
    x=[m.NewBoolVar(f"x{i}") for i in range(len(pts))]
    for L in lines: m.Add(sum(x[i] for i in L)<=2)
    m.Maximize(sum(x))
    s=cp_model.CpSolver(); s.parameters.max_time_in_seconds=tlimit; s.parameters.num_search_workers=8
    t0=time.time(); st=s.Solve(m)
    chosen=[pts[i] for i in range(len(pts)) if s.Value(x[i])==1]
    v,r=is_valid(chosen,k)
    opt = s.StatusName(st)=="OPTIMAL"
    print(f"k={k:2d}: CP-SAT size={len(chosen)} (2k={2*k}) status={s.StatusName(st)} "
          f"proven_opt={opt} valid={v} t={time.time()-t0:.1f}s")
    return len(chosen),2*k,opt,v

if __name__=="__main__":
    print("STRONG weapon (exact CP-SAT) vs the weak-ILS plateau (which stalled at 2k-1):")
    for k in [10,12,16,20]:
        solve(k, tlimit=120 if k<=16 else 200)
