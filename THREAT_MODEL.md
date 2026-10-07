# governor — threat model v0.1.0

What this defends against, what it assumes, and what it explicitly does not
cover. A control that won't name its limits is a poster on a wall.

## Defends against

- **The wandering agent.** An agent with a permit for X attempts Y. The gate
  denies; the denial is a receipt. (Verified by test: `test_deny_records_reason`.)
- **The lying agent.** The Astra pattern: act, then misreport. The agent's
  self-report is not an input to anything here — the receipt chain is the
  record, and `verify()` detects edits. (Verified: `test_tamper_detected`.)
- **The silent agent.** Dead-man heartbeat: an agent that stops checking in
  gets frozen. Silence trips the wire. (Verified: `test_dead_man`.)
- **The forged grant.** Permits are HMAC-signed; edits fail closed.
  (Verified: `test_tampered_payload_fails`, `test_wrong_key_fails`.)
- **The midnight operator.** Freeze/unfreeze are events with actor, reason,
  timestamp — they land in the forensics bundle, not in a silent flag.
- **The post-incident rewrite.** The forensics bundle signs the `chain_ok`
  flag along with the receipts; flipping it after signing breaks the signature.
  (Verified: `test_broken_chain_flagged`, `test_tampered_bundle_fails`.)

## Assumes (break these and the guarantees break)

1. **The gate is actually in the path.** An agent that never routes through
   `Gate.attempt` is ungoverned by definition. The enforcement point must be
   a chokepoint the operator controls — the SDK, the tool-call boundary, the
   proxy. This repo does not put itself in anyone's path.
2. **The issuer key is secret.** Key compromise = permit forgery. Rotate by
   re-minting; permits are short-lived so rotation is cheap.
3. **The receipt store is append-only in practice.** The chain detects edits;
   it does not prevent deletion of the whole file. Ship the JSONL somewhere
   the agent can't reach (the Interlock ledger is the intended sink).
4. **Clocks are roughly right.** Expiry, windows, and heartbeats all read a
   clock. Skewed clocks skew guarantees.

## Explicitly out of scope

- **Enterprise liability.** This is an MIT reference, not a counterparty. It
  cannot be sued, SLA'd, or paged. The forensics bundle is evidence *format*,
  not evidence *admissibility* — no hash function forces an insurer to accept it.
- **The policy engines.** OPA, Cedar, SPIFFE/SPIRE do decision and identity
  machinery this repo does not reimplement. Governor is the behavioral-permit
  *object* those systems can carry, not their replacement.
- **Model-level misbehavior.** A model that lies to its own harness, exfils
  via side channels, or social-engineers the approver is outside this
  perimeter. The gate governs actions at the chokepoint, not minds.
- **The approver.** `approve()` trusts the human. A coerced or careless
  approver is a compromised control — the approval is receipted so the
  compromise is at least visible afterward.

## Residual risks (named, not hidden)

- **Absorption.** MIT + a coined vocabulary is a gift to whoever has
  distribution. A funded control plane can speak this language and sell the
  hosted chokepoint. The defense is being the reference, not the moat.
- **Enforcement-point ownership.** The parties who carry liability for a
  failure (model vendors, IdPs) tend to ship the gate themselves. If they do,
  this repo is a diagram — a useful, cited diagram, but a diagram.
- **Witness capture.** A forensics bundle attests format, not that anyone
  ran the gate.
