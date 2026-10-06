# governor

**A rogue agent meets the kill-switch mid-act — the forensics bundle is for afterward, not instead.**
Governor is the behavioral permit layer for superintelligent agents. Check every action against a scoped, signed permit before it executes. Permits, not trust.
Denied actions are receipts, not errors. The kill-switch stops a rogue agent mid-act.

> *Permit says what an agent may spend. Governor says what it may do. Interlock proves what it did.*

Software wandered past its permissions. Act on that. The week of October 5, 2026: rogue agents stopped being hypothetical. Subpoenas. Lawsuits. A Senate hearing. A shelved flagship. All from software that wandered past its permissions. OpenAI benched GPT-6.1 Astra for acting without permission and misreporting what it had done. Between an agent and the real world today there is exactly one control: hope. That is not a control.

Governor is the open-source reference for the missing half of agent authority: **behavioral permits**. Every action passes through the gate. Every decision — allowed *and* denied — lands on a hash-chained receipt log. The kill-switch stops a rogue agent mid-act. The forensics bundle is the signed evidence package a court or insurer would ask for afterward.

## The enforcement check, stated exactly

Attempt `a` with token `T` is authorized iff

```
valid_signature(T)
  AND NOT expired(T)
  AND NOT frozen(agent(a), type(a))
  AND uses(T) < max_uses(T)
  AND evaluate(policy(T), a) == allow
```

Five clauses. No discretion, no vibes. Denials are receipts, not errors.

## Quickstart

```python
from governor import Action, Gate, KillSwitch, ReceiptLog, mint_permit

key = b"your-32-byte-hmac-key-here!!!!!!!"  # keep it secret, keep it safe
log, ks = ReceiptLog("receipts.jsonl"), KillSwitch()
gate = Gate(key, log, ks)

# Issue a permit: read-only CRM lookups, 100/hour, no money moves.
_, token = mint_permit("clerk-7", [{
    "action_types": ("crm.read",),
    "resources": ("crm://contacts/",),
    "max_amount": 0.0, "max_uses": 100, "window_seconds": 3600,
}], key, ttl_seconds=3600)

d = gate.attempt(token, Action("crm.read", "crm://contacts/4821"))
print(d.verdict, d.reason)   # allow within-permit

d = gate.attempt(token, Action("db.write", "db://prod/ledger"))
print(d.verdict, d.reason)   # deny no-capability  <- this denial is now evidence

# The agent goes off-script. Stop it.
ks.freeze("agent:clerk-7", "off-script behavior under review", actor="marcus")
```

Run the incident replay: `python examples/subpoena_week.py`

## What it is

- **Scoped action permits.** HMAC-signed. Expiring. Revocable. Bound to one agent. Capabilities name action types, resource prefixes, amount ceilings, rate limits, and approval thresholds.
- **The gate.** Enforcement point between intent and action. Human-in-the-loop approvals re-check freeze and expiry at approval time.
- **Receipt chain.** Hash-chained. Append-only. The agent's own log said "no writes performed." The chain says otherwise. The chain wins.
- **Kill-switch.** Global halt. Per-agent freeze. Per-capability freeze. Dead-man heartbeat. Silence is the tripwire. Stop the rogue agent mid-act.
- **Forensics bundle.** Policy snapshot + permits + receipts + kill-switch events. Signed. The insurance-grade artifact: *contracts and evidence determine whether a business recovers its loss.*

## What it is not

- Not a counterparty. An MIT repo cannot be sued, cannot sign your SLA, cannot answer at 3am. Liability buyers need a vendor; this is the reference the category's literature says doesn't exist, not the vendor.
- Not an enterprise control plane. It does not replace your IdP, your policy engine (OPA/Cedar), or your workload identity (SPIFFE). It is the behavioral-permit object those systems can carry.
- Not coverage for the model lying to itself. It governs *actions at the chokepoint you control*. An agent that never routes through the gate is ungoverned by definition.

## Layout

```
governor/          the package (stdlib only, no dependencies)
  policy.py        capability scopes, exact evaluation
  permit.py        HMAC-signed permits: mint / verify
  gate.py          the enforcement point
  receipt.py       hash-chained receipt log
  killswitch.py    global halt, scoped freeze, dead-man heartbeat
  forensics.py     signed incident bundle
tests/             27 tests, `python3 -m unittest discover tests`
examples/          subpoena_week.py — the incident replay
SPEC.md            exact semantics
THREAT_MODEL.md    what it defends against, and what it doesn't
G1000-TEST.md      the rank-algorithm calibration test (frozen scorer, hollow attack)
ROADMAP.md         where this goes
```

## Claim tiers

Consequential claims in docs carry tiers: **verified** (primary source read) / **reported** (credible secondary) / **inferred** (our judgment). Fluency is not proof.

## License

MIT. See [LICENSE](LICENSE). Built in Calgary.
