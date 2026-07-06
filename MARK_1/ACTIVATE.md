# ACTIVATE — putting on Mark 1 (the activation protocol)

Mark 1 is built to behave like software: there is a **passive layer** that is always on, and a
**full power-up** you trigger with one command. Like a suit — the under-layer is always worn; the
full armor snaps on when you call it.

## The two layers

### Passive (always on, automatic)
Claude Code auto-loads the root **`CLAUDE.md`** every session, and the **`.claude/`** hook re-injects the
method on **every message**. So the **ARMOR** (plan → produce → verify-independently → ground → honesty) and
the **model ladder** are engaged from the first message, with no command. This is the suit's under-layer.

> **Honest mechanism note:** the hook injects a **reminder text** into each turn (a best-effort nudge that keeps
> the method salient), not a hard runtime constraint the model cannot violate. In very long sessions, context
> dynamics can dilute any single reminder. The discipline is real and reliable in practice, but it is a *prompt*,
> not an *enforcement* — treat a slip as a bug to catch, not an impossibility.

### Full power-up (one command)
Say **"put on Mark 1"** (or run **`/mark1`**). Claude loads the full operating doctrine — the router, the
12-weapon arsenal, the kit, and the helmet — and confirms:

> **🤖 Mark 1 online.** Armor live · model ladder set · router armed · 12 weapons + 8 kit ready · helmet on
> standby. Capability ratchet OPEN at v3. Fable 5 inactive → rerouted to Opus 4.8.

From that point, for the rest of the session, Claude operates by the full Mark 1 doctrine (`.claude/skills/mark1/SKILL.md`).

## What activation actually changes
- **Before:** armor + ladder (good defaults, every message).
- **After `/mark1`:** Claude will, in addition — run the **κ-gate** on each problem (is a cheap exact verifier
  available?), **draw the matching weapon** when yes, **convene the helmet** for hard multi-part problems, and
  hold the **hard rules** (promotion bar, no open-problem claims, products only improve).

## How to share / install the suit on another project
Mark 1 is self-contained the same way the original armor suit was (`MARK_0/00_armor_suit/claude_armor/` is the
ancestor). To wear it elsewhere, copy three things into the target project root:
1. `CLAUDE.md` (the boot loader),
2. the `.claude/` folder (settings + the reminder hook + `skills/mark1/`),
3. the `MARK_1/` folder (the suit the loader points to).
Then open/restart the project and say **"put on Mark 1."** Approve the one-time hook permission prompt; you'll
see the Mark 1 reminder at the top of each turn confirming it's live.

## Honest note
Activation is a **discipline + orchestration** layer, not a new model. It makes Claude *use* the models well
(execute instead of guess, draw a weapon only when a verifier exists, escalate only where it pays) and stay
honest. It is **capability expansion + efficiency, not a ≥10% capability promotion** — the ratchet is OPEN at v3.
