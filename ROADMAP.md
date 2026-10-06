# governor — roadmap

## v0.1.0 (this release) — the reference

The complete action-governor primitive: permits, gate, receipt chain,
kill-switch, forensics bundle, the subpoena-week replay, 27 tests, CI.
Stdlib only. The point of v0.1 is that the object exists and its semantics
are exact — not that anyone deploys it.

## Next, in ROI order

1. **The r campaign.** The portfolio's return signal is ~0 everywhere; this
   repo is the designated r-engine. SI-vocabulary launch post, the
   subpoena-week replay as the demo, Threads/X distribution. Target: real
   conversation (issues, forks), not enterprise logos.
2. **Interlock sink.** Ship receipts to the Interlock ledger instead of a
   local JSONL — closes threat-model assumption #3 and makes the stack story
   ("Permit spends, Governor does, Interlock proves") literally true.
3. **Permit bridge.** One object for money *and* behavior: a permit whose
   capabilities carry both amount ceilings and action scopes. (Permit stays
   untouched until its Nov 12 hackathon deadline — the bridge lands after.)
4. **Second contributor.** An external hand on the repo (the Utkarsh pattern)
   — moves momentum's collaboration leg and, more importantly, proves the
   object is legible to someone who didn't write it.
5. **Witnessed incident drill.** A third party runs the subpoena-week replay
   against their own agent harness and attests the refusal events. This is
   the outside witness the rank test needs.

## Falsifier

If 30 days pass with r still 0 and no external conversation, the category
pick was wrong: park the repo, keep the code, file the lesson. A reference
nobody references is a diary entry.
