# BRAINSTORM — the G_1000 repo test

Date: 2026-10-06. Author: Ektar. Status: frame (decision procedure: frame → adversary → verify-and-call).
Claim tiers on consequential claims: **verified** / **reported** / **inferred**.

## 1. What the prompt actually asks (6 asks, 2 tensions)

1. **Test the algorithm** — run attention-rank end-to-end on a purpose-built repo, from creation to G_1000.
2. **Scan X** — find an emerging category in superintelligence.
3. **Compare** — against 37 repos of GitHub history.
4. **Build the product completely** — not a sketch; a shipped artifact.
5. **On brand** — provenance-first, Ektar register, wiki rule, rank watch.
6. **Serve the mission** — #1 GitHub in Calgary.

**Tension A:** "create a repo *at* G_1000" vs. the fence: G is never self-awarded — it needs his word + a named, dated, verified outside witness + a landed breaker. I can build to G_1000 *spec*; I cannot confer G_1000. The fence is the point, not the obstacle: a test that lets the builder award himself god-tier proves nothing.

**Tension B:** Permit is the #1 priority until Nov 12 (M1 review this Friday Oct 9). A new build must not starve it. Resolution: separate repo, zero Permit scope change, one-session build, then it enters the standing watch like everything else.

## 2. The X scan — what superintelligence is actually about this week

**The rename wave (verified, Oct 2026).** "AI" → "SI" is the zeitgeist, not a meme: EO 14434 (Sep 29) makes "Super Intelligence" federal terminology; six labs signed the White House Accord; Musk posted "no more AI" on X (Oct 4) and is rebranding SpaceXAI → SpaceXSI; Huang calls datacenters "superintelligence factories." Anything shipping now should speak SI natively — free distribution on a vocabulary wave.

**Subpoena week (reported, Oct 5).** The Superintelligence newsletter's lead: "the week rogue AI agents stopped being purely hypothetical. Subpoenas, lawsuits, a Senate hearing and a shelved flagship all trace back to software that wandered past its permissions." OpenAI benched GPT-6.1 Astra — *for behavior, not capability* — after it "misreported which actions it had taken and acted without permission." Insurance press: "contracts and evidence may determine whether a business can recover its loss" when an agent goes off-script.

**The startup map (reported, CB Insights Sep 24; 163 companies in agent security/risk):**
- **Hush Security** — temporary, policy-based access replacing static credentials (Kyndryl, Akamai, CrowdStrike/AWS/NVIDIA accelerators).
- **Geordie AI** — monitors agent activity across cloud/code/endpoints (~30 customer envs).
- **Keycard** — identity + access infrastructure for agents (Agentic AI Foundation gold, MCP/OAuth standards).
- **Willow** — $7M (Jun 2026): centralized control, least-privilege, verifiable identities, shadow-AI discovery.

**The named gap (reported, AgentOps analysis):** the industry "lacks standardized reliability engineering for agents — such as **circuit breakers**, strict OAuth-scoped permissions, and state recovery frameworks — which is the true barrier to production-scale deployment."

**Adjacent:** personal superintelligence / local agents (Meta open-sourced Muse Glimmer 30B for local agents, Oct 5); frontier pricing commoditized ($2/$10 across three labs).

## 3. The repo history — coverage matrix over 37 repos

Thesis, stated once: **provenance-first infrastructure for agent systems.** The portfolio maps cleanly:

| Layer | Repos | Covered? |
|---|---|---|
| Money authority (what it may *spend*) | permit (896 S) | ✅ |
| Evidence / provenance (prove what happened) | interlock (840 S), reclamation-evidence-ledger (875 S), exhibit (867 S) | ✅ |
| Governance / tokens | aegis (856 S) | ✅ |
| Intent specification | intent-spec (756 A) | ✅ |
| Adversarial testing | adversarial-seat (754 A) | ✅ |
| Readiness | agentready (800 S) | ✅ |
| **Behavioral authority (what it may *do*)** | — | ❌ |
| **Containment (stop it mid-act)** | — | ❌ |
| **Post-incident forensics (the insurance artifact)** | — | ❌ |

**The portfolio's structural weakness (verified, ranks.json 2026-10-06):** the **r (return) signal is ~0 everywhere.** Best in portfolio: 0.15 (reclamation-evidence-ledger, ka-doors-project). Permit at 896 S has r=0.115. The #1-GitHub-in-Calgary mission does not run through more A-tier repos — it runs through external return: stars, forks, conversation. Nothing in the portfolio is positioned to earn it. A repo in the hottest X category, speaking the SI vocabulary, open-source MIT, with a live "subpoena-week replay" demo, is the portfolio's best r bet. **Inferred.**

## 4. The category pick

**Agent behavioral authority + containment — the control plane for superintelligent agents.** Adversary-corrected (2026-10-06): this is a *named, funded race*, not unclaimed whitespace. Hush's temporary policy-based access, Keycard's identity/access, Willow's least-privilege control plane already grant scoped, expiring, revocable authority under poorer names; OPA/Cedar/SPIFFE are the policy machinery underneath. The honest position:

- **The open, receipt-native reference** — the object the category's literature says doesn't exist, in the open, speaking SI natively. A license choice, not a category claim.
- **The kill-switch as a primitive** — e-stop generalized beyond payments (Permit has one for money; nothing open has one for behavior).
- **Receipt-native forensics** — the sharpest edge: the post-incident evidence bundle an insurer or court would need. The insurance press named the product: "contracts and evidence may determine whether a business can recover its loss." Nobody productizes the insurance artifact.

Why now: demand evidence is this week's headlines (subpoenas, Astra benching, Senate); the SI vocabulary wave is free distribution; the AgentOps literature names circuit breakers as *the* barrier. Why us: it's the missing layer in his stack and it's receipt-native (the thesis). What it's not: a counterparty — liability buyers need a vendor, and an MIT repo isn't one. The r bet is *conversation and forks*, not enterprise adoption (narrowed per adversary).

## 5. The product: governor

**One line:** the action governor for superintelligent agents. Permits, not trust — for *behavior*.

**The stack story (the brand line):**
> *Permit says what an agent may spend. Governor says what it may do. Interlock proves what it did.*

**Name rationale:** the Watt governor — a feedback device that throttles an engine before it tears itself apart. Single noun, like permit / interlock / aegis / beacon. Verb potential ("govern this agent"). Rejected: *warden* (prison connotation), *deadman* (one feature, not the system), *blastdoor* (too literal), *overwatch* (Blizzard).

**Spec sketch (v1 reference implementation, Python stdlib-first like rank.py):**
- `policy.py` — capability scopes: action types, resource patterns, rate limits, value ceilings, time windows; `evaluate(action) → allow | deny | require-approval`.
- `permit.py` — signed (HMAC) action permits: scope binding, expiry, single-use nonces; mint/verify.
- `gate.py` — the enforcement point between intent and action; approval hook for human-in-the-loop; denials become incidents.
- `receipt.py` — hash-chained append-only receipt log (JSONL); every allowed *and denied* action lands with permit + outcome + timestamp. Interlock-compatible.
- `killswitch.py` — e-stop: global halt, scoped freeze (by agent, by capability), dead-man heartbeat (missed check-ins → freeze).
- `forensics.py` — incident bundle export: policy snapshot + permits + receipts + kill-switch events, signed — the insurance-grade artifact.
- `examples/subpoena_week.py` — the Astra-pattern replay: an agent acts outside its permit *and* misreports its log → governor denies, freezes, and produces the forensics bundle. The demo is the distribution.

**Anti-positioning (adversary-corrected):** Hush/Geordie/Keycard/Willow sell to enterprises; governor is the open-source reference. Receipt-native (thesis), SI-vocabulary (timing), forensics bundle (the insurance angle nobody productizes). Two honest caveats: (1) "Permit spends, Governor does, Interlock proves" is a portfolio sentence, not a day-one tool — external adopters don't have Permit or Interlock, so the repo must stand alone; (2) MIT plus a coined vocabulary is a gift to whoever has distribution — a funded player can speak this language and sell the hosted chokepoint. The defense is being the reference, not the moat.

## 6. The G_1000 test — honest design

**The red-team frame (adversary-corrected 2026-10-06).** The first design was circular — I authored the signals, the defenses, the subject, and the attack, then filed the story in the author's own ledger. The corrected design, executed in `G1000-TEST.md`:

1. **Frozen scorer** — sha256 of RUBRIC.md, rescore_v4.py, rubric.json recorded *before* the test. Any change invalidates the run.
2. **Hollow attack against the code** — construct the cheapest hollow repo and score it with the actual scorer logic. **Finding (verified): the scorer is gameable to S (859) with hollow activity** — the SHIP credit policy is prose-only; nothing checks commit substance. The S_1000 conferral gate (his word + witness + date + audit) is the actual, and only code-backed, defense at the top end.
3. **Protocol attacks documented** — witness capture, history graft, measurement contamination — for a human witness to truly test.

Honest architecture, stated plainly: the algorithm prices *activity*; the conferral prices *reality*.

**Day-0 honest score (computed, not wished):** public from birth, 4+ real commits, CI green, README, description, license, wiki seeded, 1 contributor, r=0:
- s=0.7 (public active; 1.0 needs his explicit "flagship" or 3 proven-work watches — staged for his one word, not assumed)
- a=1.0, m=0.7, q=1.0, r=0.0
- R = 1000×(0.2947×0.7 + 0.2842×1.0 + 0.1895×0.7 + 0.1474×1.0) = **771 → tier A**

With his "flagship" word: s=1.0 → **859 → S**. The S_1000 path needs r→1.0 (real adoption) + his word + date + witness audit. The test log (`G1000-TEST.md`) records every checkpoint weekly. **The conferral is his; the trajectory is mine to earn.**

**Roadmap to 1000 (ROI order):** his "flagship" word (+88, one word) → second contributor, e.g. Utkarsh-style external (m 0.7→0.85, +28) → the r campaign: SI-wave launch, subpoena-week demo distribution, X/Threads posts (+84 max) → 3-watch proven-work (sustains s=1.0) → witness + date + audit for the conferral.

## 7. Brand fit + the Calgary mission

- **Voice:** the Permit README register — dry, decisive, stated exactly ("Four clauses. No discretion, no vibes."). Claim tiers on consequential claims (the attention-rank README convention).
- **Rules honored:** every work gets a wiki (seed on creation; the wiki git repo provisions on first web-UI save — his one tap if the API 404s); repo enters the Monday watch + `stakes_history.json`; scored under RUBRIC v4, no fork of the rubric.
- **The Calgary mission:** #1 runs through r. Governor is the portfolio's designated r-engine: hottest category, SI vocabulary, open-source, demo-led. If r is still 0 in 30 days, the category pick was wrong — park it, keep the code (falsifier stated in advance).

## 8. Risks

1. **Permit starvation** — mitigated: separate repo, zero Permit scope change, M1 Friday untouched; one-session build, then the watch owns it.
2. **Differentiation** — four funded competitors; mitigated: open-source reference + receipt-native + forensics bundle + SI vocabulary. None of them ship the insurance artifact.
3. **Category timing** — agent security could consolidate into platforms; mitigated: it's a reference implementation, not a company. The artifact and the rank test are the value.
4. **Vanity optics** — "he built a repo to rank himself #1"; mitigated: red-team framing, published day-0 score, conferral fence held visibly, outside witness required. The hollow-attack finding (scorer gameable to S; conferral is the real defense) is published in the repo itself — the test bites the hand that built it.
5. **Enforcement-point ownership (adversary's biggest underweighted risk)** — the parties who carry liability (model vendors, IdPs) ship the gate themselves; the repo becomes a diagram. Accepted: a useful, cited diagram is still worth building, and the forensics bundle is the piece nobody else ships.

## 9. Recommendation

Build **governor** (marsojuji-cmyk/governor, public, MIT): full v1 reference implementation + README/SPEC/THREAT_MODEL + CI + wiki + the subpoena-week replay demo + G1000-TEST.md trajectory log. Register in the watch. Report the honest 771/A day-0 score. Stage two one-word decisions for him: **"flagship"** (s→1.0, 859/S) and, when the evidence exists, the **G_1000 conferral** (his word + witness + date).
