"""Post-incident forensics bundle — the insurance-grade artifact.

When an agent goes off-script, the question that decides who pays is not
"what did the agent say it did" but "what can be proven." The bundle binds,
in one signed object:

  - the policy snapshot in force at the time (what it was allowed to do)
  - the permits issued (the grants it held)
  - the receipt window (every allowed AND denied decision, hash-chained)
  - the kill-switch events (when it was stopped, by whom, why)
  - the chain verification result (is the record intact?)

Signed with HMAC. verify_bundle() fails closed on any edit.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import time


def _canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def build_bundle(*, incident_id: str, policy_snapshot: list[dict],
                 permits: list[dict], receipts: list[dict],
                 killswitch_events: list[dict], chain_ok: bool,
                 key: bytes, ts: float | None = None) -> dict:
    bundle = {
        "format": "governor-forensics/1",
        "incident_id": incident_id,
        "created_at": ts if ts is not None else time.time(),
        "policy_snapshot": policy_snapshot,
        "permits": permits,
        "receipts": receipts,
        "killswitch_events": killswitch_events,
        "chain_ok": chain_ok,
    }
    sig = hmac.new(key, _canonical(bundle), hashlib.sha256).hexdigest()
    return {**bundle, "signature": sig}


def verify_bundle(bundle: dict, key: bytes) -> tuple[bool, str]:
    """Returns (ok, message). Fails closed."""
    sig = bundle.get("signature")
    if not sig:
        return False, "missing-signature"
    body = {k: v for k, v in bundle.items() if k != "signature"}
    expect = hmac.new(key, _canonical(body), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expect, sig):
        return False, "bad-signature"
    if not body.get("chain_ok"):
        return False, "receipt-chain-broken"
    return True, f"bundle-ok-{len(body.get('receipts', []))}-receipts"
