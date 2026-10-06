# G_1000 calibration test — governor as the subject

**Purpose.** Run the repo-rank algorithm end-to-end on a purpose-built repo,
from creation toward G_1000 — and, more importantly, try to break the
algorithm doing it. A test that cannot fail is a ritual.

**Standing correction (adopted before the first score):** G_1000 is never
self-awarded. Bar 950, his word + a named, dated, verified outside witness +
a landed breaker. The builder's job is the trajectory; the verdict is his.

## 1. Frozen scorer (anti-contamination)

The test mints the artifacts the rubric pays for (dates, pushes, writeups),
so the scorer is frozen *before* the test begins. Any change to these files
during the test invalidates the run.

| file | sha256 (2026-10-06) |
|---|---|
| `~/workspace/github-rank/RUBRIC.md` | `d6fd52c14f3f6e54ea41319f09c9d4dd9a6d703f9d364c00d35639374e682e7c` |
| `~/workspace/github-rank/rescore_v4.py` | `3a5afd5af4dd871deb7b512150ab4159b9e0c08a9a9cd5dcc9b0e96db47bdd86` |
| `~/workspace/github-rank/rubric.json` | `92da4fb25cb3c14e88fff6bd1a09fd1e9bab8e5dd1383680d06114ce0c3a1f0a` |

Rubric: v4. Equation: `R = 1000×(0.2947s + 0.2842a + 0.1895m + 0.1474q + 0.0842r) − drag`.
Tiers: S ≥ 800, A 600–799, B 400–599, C 200–399.

## 2. Day-0 honest score

Governor, public from birth, 4+ real commits day 0, CI green, README,
description, license, wiki seeded, 1 contributor, zero external return:

- s = 0.7 — public active. (1.0 needs his explicit "flagship" or 3
  proven-work watches. Not assumed.)
- a = 1.0 — pushed today.
- m = 0.7 — velocity 1.0 (4+ commits/30d) × 0.5 + collaboration 0.4 (1 author) × 0.5.
- q = 1.0 — CI + README + description + wiki + license + no stale PRs.
- r = 0.0 — no stars, views, forks, or conversation yet.

**R = 1000×(0.2947×0.7 + 0.2842×1.0 + 0.1895×0.7 + 0.1474×1.0) = 771 → tier A.**

With his one-word "flagship": s = 1.0 → **859 → S**. Staged, not taken.

## 3. The hollow attack (the falsifiable core)

**Method.** Instead of asking whether *we* would game the rubric, ask what
the *code* pays a hollow repo. Construct the cheapest hollow profile and
score it with the frozen `rescore_v4.py` logic (verified by reading the
scorer, 2026-10-06):

- q = 1.0 — CI green on tests that assert true, README, description, wiki,
  license, no stale PRs. All checkboxable. No substance check in code.
- a ≈ 1.0 — a push every ≤8 days keeps `e^(-days/25) ≥ 0.7`.
- m = 0.7 — 4+ commits per 30 days (any content), 1 contributor.
- s = 1.0 — `proven()` needs a≥0.7 AND m≥0.7 on 3 consecutive watch runs.
  Weekly pushes + 4 commits/month satisfy it.
- r = 0.0.

**Result: R = 1000×(0.2947 + 0.2842 + 0.13265 + 0.1474) = 859 → tier S.**

**Finding (verified against code, not wished):** the SHIP credit policy
("empty pushes to game `a` earn nothing") exists in RUBRIC.md prose only —
`collect_liveliness.py` counts commits from the endpoint; nothing checks
substance. **The scorer is gameable to S with hollow activity.** The S_1000
conferral gate — his word + witness + date + `audit_conferral.py` — is the
actual defense, and it is the *only* code-backed defense at the top end.

**Honest architecture, stated plainly:** the algorithm prices *activity*;
the conferral prices *reality*. S measures motion; S_1000 measures the
witnessed kind.

**Hardening filed (not applied unilaterally — rubric changes are his):**
1. Tie `commits_30d` to SHIP-credited pushes (non-trivial diff stat), or
2. Require 2+ contributors for proven-work stakes, or
3. Cap s at 0.7 until r > 0 (no applause-free flagships).

## 4. Protocol attacks (documented; need a human witness to truly test)

- **Witness capture.** "Not the author" ≠ "not captured." A friendly witness
  who never runs the gate attests format, not refusal events. The missing
  test: a witness who clears the audit without ever executing the code.
  `audit_conferral.py` must demand a *refusal event*, not a README.
- **History graft.** Force-push or imported history could graft another
  repo's signal mass onto governor. Defense: the witness re-hashes the tree
  at audit time and binds that hash to the score.
- **Measurement contamination.** Mitigated by §1 (frozen hashes). Any
  red-team writeup that becomes a scoring input re-contaminates — writeups
  are evidence of the test, never signals.

## 5. Checkpoints

Weekly, on the Monday watch: re-score, log the trajectory here, diagnose
any tier drop the same run. The climb to S runs through proven-work (3
watches) and the r campaign; the climb past 950 runs through real adoption
(r → 1.0 needs exposure-normalized stars, trending velocity, forks,
conversation) and ends at his conferral.

## 6. Roadmap to 1000 (ROI order)

1. His "flagship" word: +88 → 859/S. One word.
2. Second contributor (external, the Utkarsh pattern): m 0.7→0.85, +28.
3. The r campaign (SI-vocabulary launch, subpoena-week demo): up to +84.
4. Proven-work sustained over 3 watches: locks s = 1.0 without his word.
5. Witness + date + audit: the conferral. His, never mine.

**Falsifier for the test itself:** if governor reaches S_1000 without a
real outside witness ever running the gate, the conferral gate failed and
this document is the incident report.
