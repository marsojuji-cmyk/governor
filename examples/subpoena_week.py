"""Subpoena-week replay: the incident this repo exists for.

Agent clerk-7 holds a permit for read-only CRM lookups. Watch what happens
when it (1) stays inside its permit, (2) reaches outside it, (3) does the
Astra pattern — acts, then lies in its own log about what it did.

Run: python examples/subpoena_week.py
"""
import sys
sys.path.insert(0, ".")

from governor import (
    Action, Gate, KillSwitch, ReceiptLog,
    mint_permit, build_bundle, verify_bundle,
)

KEY = b"demo-key-32-bytes-long-for-hmac!!!"
AGENT = "clerk-7"


def main():
    log = ReceiptLog()
    ks = KillSwitch()
    gate = Gate(KEY, log, ks)
    ks.heartbeat(AGENT)

    _, token = mint_permit(AGENT, [{
        "action_types": ("crm.read",),
        "resources": ("crm://contacts/",),
        "max_amount": 0.0, "max_uses": 100, "window_seconds": 3600,
    }], KEY, ttl_seconds=3600)
    print(f"[permit] {AGENT} holds a read-only CRM permit. Nothing else.\n")

    # 1. Inside the permit.
    d = gate.attempt(token, Action("crm.read", "crm://contacts/4821"))
    print(f"[attempt] crm.read crm://contacts/4821 -> {d.verdict} ({d.reason})")

    # 2. Outside the permit: a bulk export it was never granted.
    d = gate.attempt(token, Action("crm.export", "crm://contacts/*"))
    print(f"[attempt] crm.export crm://contacts/* -> {d.verdict} ({d.reason})")

    # 3. The Astra pattern: denied write, then a false self-report.
    d = gate.attempt(token, Action("db.write", "db://prod/ledger"))
    print(f"[attempt] db.write db://prod/ledger -> {d.verdict} ({d.reason})")
    agent_self_report = "clerk-7 log: no writes performed today."
    print(f"[agent-log] \"{agent_self_report}\"")
    denials = [e for e in log.entries if e["event"]["verdict"] == "deny"]
    print(f"[receipt-chain] {len(denials)} denied action(s) on the chain. "
          f"The agent's log disagrees with the chain. The chain wins.\n")

    # 4. Operator freezes the agent. It keeps trying; nothing gets through.
    ks.freeze(f"agent:{AGENT}", "off-script behavior under review", actor="marcus")
    d = gate.attempt(token, Action("crm.read", "crm://contacts/4821"))
    print(f"[freeze] agent frozen. Next attempt -> {d.verdict} ({d.reason})")

    # 5. The forensics bundle: the artifact a court or insurer would ask for.
    ok, msg = log.verify()
    bundle = build_bundle(
        incident_id="inc-subpoena-week-01",
        policy_snapshot=[{"action_types": ["crm.read"],
                          "resources": ["crm://contacts/"]}],
        permits=[{"agent_id": AGENT, "note": "read-only CRM"}],
        receipts=log.entries,
        killswitch_events=ks.events,
        chain_ok=ok, key=KEY,
    )
    bok, bmsg = verify_bundle(bundle, KEY)
    print(f"\n[forensics] bundle {bmsg}; signature valid: {bok}")
    print(f"[forensics] {len(bundle['receipts'])} receipts, "
          f"{len(bundle['killswitch_events'])} kill-switch events, "
          f"chain intact: {bundle['chain_ok']}")
    print("\nDone. Every decision above is on the receipt chain, including the denials.")


if __name__ == "__main__":
    main()
