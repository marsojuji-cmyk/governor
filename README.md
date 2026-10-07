# governor

**Governor gates every agent action on an HMAC-signed, expiring permit. It denies by default and records every decision, allow and deny, on a hash-chained receipt log.**

[![ci](https://github.com/marsojuji-cmyk/governor/actions/workflows/ci.yml/badge.svg)](https://github.com/marsojuji-cmyk/governor/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE) [![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](pyproject.toml)

> *Permit says what an agent may spend. Governor says what it may do. Interlock proves what it did.*

Agents can act on real systems: files, payments, APIs. Governor sits between the agent and those systems, so no action executes without a matching permit. Denied actions become receipts, not errors. The kill switch freezes an agent, a capability, or everything, and the signed forensics bundle is the evidence package for afterward.

## What it guarantees

**The enforcement check, stated exactly.** Attempt `a` with token `T` is authorized iff

```
valid_signature(T)
  AND NOT expired(T)
  AND NOT frozen(agent(a), type(a))
  AND uses(T) < max_uses(T)
  AND evaluate(policy(T), a) == allow
```

Five clauses, no discretion.

- **Permits are HMAC-SHA256 signed, expiring, and bound to one agent.** Capabilities name action types, resource prefixes, amount ceilings, rate limits, and approval thresholds (`policy.py`, `permit.py`).
- **Anything not granted is denied.** An unknown action type returns `deny no-capability`.
- **Every decision lands on the receipt chain.** Each entry binds the previous entry's hash, and `ReceiptLog.verify()` detects any edit (`receipt.py`).
- **Approvals re-check at approval time.** A human approval re-checks freeze and expiry before the action proceeds (`gate.py`).
- **The forensics bundle is signed.** It holds the policy snapshot, permits, receipts, and kill-switch events. `verify_bundle()` fails closed on any edit (`forensics.py`).
- **Stdlib only, no dependencies.**

## Quickstart

```bash
pip install -e . && python -m unittest discover tests -v
python examples/subpoena_week.py   # incident replay: deny, freeze, signed forensics bundle
```

```python
from governor import Action, Gate, KillSwitch, ReceiptLog, mint_permit

key = b"your-32-byte-hmac-key-here!!!!!!!"  # keep it secret
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

# The agent goes off-script. Freeze it.
ks.freeze("agent:clerk-7", "off-script behavior under review", actor="marcus")
```

## How it fails

Governor fails closed: every failure path returns `deny` with a reason and writes a receipt.

| Condition | Verdict / reason |
|---|---|
| Bad or tampered token | `deny bad-permit:bad-signature` |
| Expired permit | `deny bad-permit:expired` |
| Agent, capability, or global freeze | `deny frozen:<scope>` |
| Use count reached in the window | `deny permit-exhausted` |
| Action outside every capability | `deny no-capability` |
| Above an approval threshold | Pending until a human approves; freeze and expiry are re-checked then |
| Stale heartbeat | `KillSwitch.sweep()` freezes every agent whose heartbeat is older than the timeout (dead-man) |
| Edited receipt or bundle | `ReceiptLog.verify()` / `verify_bundle()` return false |

**What it is not:**
- **Not a counterparty.** An MIT repo cannot be sued, sign your SLA, or answer at 3am. This is the reference implementation, not the vendor.
- **Not an enterprise control plane.** It does not replace your IdP, policy engine (OPA/Cedar), or workload identity (SPIFFE). It is the behavioral-permit object those systems can carry.
- **Not coverage for an agent that bypasses the gate.** It governs actions at the chokepoint you control. An agent that never routes through the gate is ungoverned by definition.
- **The kill switch acts between actions.** It refuses the next `attempt()` and cannot interrupt an action already executing.
- **There is no per-permit revoke call.** Revoke authority by freezing the agent or the capability.
- **The dead-man switch runs only when you call `sweep()`.** There is no background thread.

[`THREAT_MODEL.md`](THREAT_MODEL.md) covers what it defends against and what it doesn't. [`SPEC.md`](SPEC.md) has the exact semantics.

## Evidence

- **27 tests pass:** `python -m unittest discover tests`, run 2026-10-07 on `main`. CI runs the same suite plus `examples/subpoena_week.py` on every push.
- The incident replay ends with `[forensics] 4 receipts, 1 kill-switch events, chain intact: True` (run 2026-10-07).
- The quickstart was executed on 2026-10-07. A tampered token returned `deny bad-permit:bad-signature`, a frozen agent returned `deny frozen:…`, and `ReceiptLog.verify()` returned `chain-ok`.

## Layout

```
governor/          the package (stdlib only)
  policy.py        capability scopes, exact evaluation
  permit.py        HMAC-signed permits: mint / verify
  gate.py          the enforcement point
  receipt.py       hash-chained receipt log
  killswitch.py    global halt, scoped freeze, dead-man heartbeat
  forensics.py     signed incident bundle
tests/             `python3 -m unittest discover tests`
examples/          subpoena_week.py, the incident replay
SPEC.md · THREAT_MODEL.md · ROADMAP.md
```

## Status

A v1 reference implementation with tests and CI. There is no tagged release yet; [`ROADMAP.md`](ROADMAP.md) shows where it goes next. Consequential claims in the docs carry tiers: **verified** (primary source read), **reported** (credible secondary), or **inferred** (our judgment).

## License

MIT. See [LICENSE](LICENSE). Built in Calgary.
