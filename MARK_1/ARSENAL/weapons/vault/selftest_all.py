#!/usr/bin/env python3
"""VAULT frozen gate — run EVERY adversarial self-test. Exits 0 only if the verifier-
gated entry gate ACCEPTS a result with a valid verification record as a FACT, REJECTS a
record-less or present-but-EMPTY record (the in-place LEAD-promotion attack) down to a
LEAD, FLAGS stale FETCHED facts on read (high-stakes -> re-verify), NEVER returns a LEAD
in a facts query, preserves provenance round-trip, AND the router routes correctly.

Doctrine: "A gate that can't fail is not a gate." If this exits non-zero, NO VAULT
entry is trustworthy — an unverified belief could be masquerading as a fact.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vault_gate
import vault_store
import vault_router

CHECKS = [
    ("ENTRY-GATE   (accept-good / record-less->LEAD / EMPTY-record LEAD-promotion attack "
     "/ stale-FLAG / high-stakes-REVERIFY / provenance round-trip / stakes-ENUM)",
     vault_gate._selftest),
    ("STORE-CONTRACT (facts-query has NO lead leak / leads-query hypotheses-only / stale "
     "REVERIFY flag + reverify_queue / provenance survives disk)",
     vault_store._selftest),
    ("ROUTER       (machine->VERIFIED_FACT / fetched->FETCHED_FACT decays / belief->LEAD "
     "/ judgment->LEAD / empty->LEAD default)",
     vault_router._selftest),
]

if __name__ == "__main__":
    print("=" * 78)
    print("VAULT verifier-gated memory — adversarial self-tests")
    print("=" * 78)
    failures = 0
    for name, fn in CHECKS:
        try:
            fn()
        except AssertionError as e:
            print(f"  {name}\n    *** SELF-TEST FAILED (gate broken) ***  {e}")
            failures += 1
        except Exception as e:
            print(f"  {name}\n    *** ERROR ***  {type(e).__name__}: {e}")
            failures += 1
    print("=" * 78)
    if failures:
        print(f"GATE: {failures} self-test(s) failed — DO NOT TRUST any VAULT entry "
              "(an unverified belief could be masquerading as a fact).")
        sys.exit(1)
    print("GATE: only valid-record results enter as FACTS; record-less / empty-record "
          "writes demote to LEAD; stale FETCHED facts FLAG/RE-VERIFY; LEADs never appear "
          "in a facts query; provenance round-trips; router routes correctly. OK.")
    sys.exit(0)
