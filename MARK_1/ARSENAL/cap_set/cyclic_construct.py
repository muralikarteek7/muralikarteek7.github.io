#!/usr/bin/env python3
"""NEW ANGLE (theory-reduced computation): impose CYCLIC symmetry on the 3 slices.
slices = S, sigma(S), sigma^2(S) for an order-3 sigma in GL(6,3). Then the 7-cap is valid iff
S is a cap AND there is no s0+sigma(s1)+sigma^2(s2)=0 with s0,s1,s2 in S. This reduces the
2187-var search to a 729-var one. |S|>=79 -> total 3|S|>=237 > 236. Greedy first; certify all."""
import json, itertools, random
from capset_verify import is_capset
random.seed(5)
ALL6=list(itertools.product(range(3),repeat=6))

def block_sigma():
    # order-3 unipotent: direct sum of three [[1,1],[0,1]] blocks (J^3=I in F_3)
    M=[[0]*6 for _ in range(6)]
    for b in range(3):
        M[2*b][2*b]=1; M[2*b][2*b+1]=1; M[2*b+1][2*b+1]=1
    return M
def matvec(M,v): return tuple(sum(M[i][j]*v[j] for j in range(6))%3 for i in range(6))
def compose(M):
    s={}; 
    for v in ALL6: s[v]=matvec(M,v)
    return s

def order_check(sig):
    return all(sig[sig[sig[v]]]==v for v in ALL6) and any(sig[v]!=v for v in ALL6)

def build_greedy(sig, order):
    # maintain S; adding s must keep: (cap) no two in S collinear w/ s; (transversal) no
    # s0+sig(s1)+sig2(s2)=0 with the three from S (s in any role).
    sig2={v:sig[sig[v]] for v in ALL6}
    # inverse maps for solving the determined third element
    inv_sig={sig[v]:v for v in ALL6}; inv_sig2={sig2[v]:v for v in ALL6}
    S=set(); Slist=[]
    def neg(p): return tuple((-x)%3 for x in p)
    def add3(a,b): return tuple((a[i]+b[i])%3 for i in range(6))
    for s in order:
        if s in S: continue
        ok=True
        # cap check: no q in S with third (=-(s+q)) in S
        for q in Slist:
            t=tuple((-(s[i]+q[i]))%3 for i in range(6))
            if t in S and t!=s and t!=q: ok=False;break
        if not ok: continue
        # transversal check: s0+sig(s1)+sig2(s2)=0. s can be s0, s1, or s2.
        # role s0=s: need no s1,s2 in S with sig(s1)+sig2(s2) = -s  => for each s1 in S, s2=inv_sig2(-s - sig(s1)); if in S -> bad
        Sp=S
        for s1 in Sp:
            need=tuple((-(s[i]+sig[s1][i]))%3 for i in range(6))  # = -s - sig(s1) ; s2 = inv_sig2(need)
            s2=inv_sig2.get(need)
            if s2 in Sp: ok=False;break
        if ok:
          # role s1=s: s0 + sig(s) + sig2(s2)=0 -> for each s2 in S, s0 = -(sig(s)+sig2(s2)); if in S bad
          for s2 in Sp:
            s0=tuple((-(sig[s][i]+sig2[s2][i]))%3 for i in range(6))
            if s0 in Sp: ok=False;break
        if ok:
          # role s2=s: s0+sig(s1)+sig2(s)=0 -> for each s1 in S, s0=-(sig(s1)+sig2(s)); if in S bad
          for s1 in Sp:
            s0=tuple((-(sig[s1][i]+sig2[s][i]))%3 for i in range(6))
            if s0 in Sp: ok=False;break
        # also self-collisions (s1=s2=s etc.) covered since we check membership in S after adding? do final verify anyway
        if ok:
            S.add(s); Slist.append(s)
    return Slist

def assemble(S,sig):
    sig2={v:sig[sig[v]] for v in ALL6}
    return [s+(0,) for s in S]+[sig[s]+(1,) for s in S]+[sig2[s]+(2,) for s in S]

if __name__=="__main__":
    M=block_sigma(); sig=compose(M)
    print("sigma order-3 unipotent:", order_check(sig))
    best=0; bestS=None
    for trial in range(60):
        order=ALL6[:]; random.shuffle(order)
        S=build_greedy(sig, order)
        if len(S)>best:
            best=len(S); bestS=S
            print(f"  trial {trial}: |S|={len(S)} -> total={3*len(S)}")
    full=assemble(bestS,sig)
    v,r=is_capset(full)
    print(f"\nbest |S|={best} -> total={3*best} (vs 224 baseline, 236 record).  CERTIFY valid={v} ({r}) size={len(full)}")
    if v and len(full)>224:
        json.dump({"7":[list(p) for p in full]},open(f"cap_n7_size{len(full)}_cyclic.json","w"))
        print(f"  >>> BEAT 224 with cyclic construction: {len(full)} (persisted) <<<")
    elif len(full)<=224:
        print("  cyclic greedy did not beat 224 here; escalate sigma choice / exact solve.")
