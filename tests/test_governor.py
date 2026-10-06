"""governor test suite. Stdlib unittest. Run: python -m unittest discover tests"""
import time
import unittest

from governor import (
    Action, Capability, Policy, ALLOW, DENY, REQUIRE_APPROVAL,
    ActionPermit, PermitError, mint_permit, verify_token,
    ReceiptLog, KillSwitch, Gate, build_bundle, verify_bundle,
)

KEY = b"test-key-32-bytes-long-for-hmac!!"


def caps():
    return [{
        "action_types": ("crm.read",),
        "resources": ("crm://contacts/",),
        "max_amount": 0.0, "max_uses": 3, "window_seconds": 3600,
        "approval_above": 0.0, "always_approve": False,
    }]


def gate_fixture():
    log = ReceiptLog()
    ks = KillSwitch()
    g = Gate(KEY, log, ks)
    _, token = mint_permit("clerk-7", caps(), KEY, ttl_seconds=3600)
    return g, token, log, ks


class TestPermit(unittest.TestCase):
    def test_roundtrip(self):
        permit, token = mint_permit("a1", caps(), KEY)
        back = verify_token(token, KEY)
        self.assertEqual(back.agent_id, "a1")
        self.assertEqual(back.permit_id, permit.permit_id)

    def test_tampered_payload_fails(self):
        _, token = mint_permit("a1", caps(), KEY)
        prefix, payload, sig = token.split(".")
        bad = payload[:-2] + ("AA" if not payload.endswith("AA") else "BB")
        with self.assertRaises(PermitError):
            verify_token(f"{prefix}.{bad}.{sig}", KEY)

    def test_wrong_key_fails(self):
        _, token = mint_permit("a1", caps(), KEY)
        with self.assertRaises(PermitError):
            verify_token(token, b"wrong-key-32-bytes-long-for-hmac!")

    def test_expired_fails(self):
        _, token = mint_permit("a1", caps(), KEY, ttl_seconds=-1)
        with self.assertRaises(PermitError):
            verify_token(token, KEY)

    def test_malformed_fails(self):
        for bad in ["", "g1..", "xx.abc.def", "g1." + "e30" + ".00"]:
            with self.assertRaises(PermitError):
                verify_token(bad, KEY)


class TestPolicy(unittest.TestCase):
    def test_allow_within_permit(self):
        p = Policy.from_dicts(caps())
        e = p.evaluate(Action("crm.read", "crm://contacts/1"), 0)
        self.assertEqual((e.verdict, e.reason), (ALLOW, "within-permit"))

    def test_deny_no_capability(self):
        p = Policy.from_dicts(caps())
        e = p.evaluate(Action("db.write", "db://users"), 0)
        self.assertEqual((e.verdict, e.reason), (DENY, "no-capability"))

    def test_deny_amount(self):
        p = Policy.from_dicts(caps())
        e = p.evaluate(Action("crm.read", "crm://contacts/1", amount=5.0), 0)
        self.assertEqual(e.reason, "amount-exceeds-cap")

    def test_deny_rate(self):
        p = Policy.from_dicts(caps())
        e = p.evaluate(Action("crm.read", "crm://contacts/1"), 3)
        self.assertEqual(e.reason, "rate-exceeded")

    def test_require_approval(self):
        c = dict(caps()[0]); c["always_approve"] = True
        p = Policy.from_dicts([c])
        e = p.evaluate(Action("crm.read", "crm://contacts/1"), 0)
        self.assertEqual((e.verdict, e.reason), (REQUIRE_APPROVAL, "approval-required"))

    def test_approval_above_threshold(self):
        c = dict(caps()[0]); c["max_amount"] = 1000.0; c["approval_above"] = 100.0
        p = Policy.from_dicts([c])
        e = p.evaluate(Action("crm.read", "crm://contacts/1", amount=500.0), 0)
        self.assertEqual(e.verdict, REQUIRE_APPROVAL)


class TestGate(unittest.TestCase):
    def test_allow_and_record(self):
        g, token, log, _ = gate_fixture()
        d = g.attempt(token, Action("crm.read", "crm://contacts/9"))
        self.assertTrue(d.allowed)
        self.assertEqual(log.entries[-1]["event"]["verdict"], ALLOW)

    def test_deny_records_reason(self):
        g, token, log, _ = gate_fixture()
        d = g.attempt(token, Action("db.drop", "db://prod"))
        self.assertFalse(d.allowed)
        self.assertEqual(d.reason, "no-capability")
        self.assertEqual(log.entries[-1]["event"]["reason"], "no-capability")

    def test_bad_token_denied(self):
        g, _, _, _ = gate_fixture()
        d = g.attempt("g1.bogus.deadbeef", Action("crm.read", "crm://contacts/1"))
        self.assertFalse(d.allowed)
        self.assertTrue(d.reason.startswith("bad-permit"))

    def test_frozen_denied(self):
        g, token, _, ks = gate_fixture()
        ks.freeze("agent:clerk-7", "operator halt")
        d = g.attempt(token, Action("crm.read", "crm://contacts/1"))
        self.assertFalse(d.allowed)
        self.assertTrue(d.reason.startswith("frozen"))

    def test_rate_exceeded_denied(self):
        g, token, _, _ = gate_fixture()
        for i in range(3):
            g.attempt(token, Action("crm.read", f"crm://contacts/{i}"))
        d = g.attempt(token, Action("crm.read", "crm://contacts/99"))
        self.assertEqual(d.reason, "rate-exceeded")

    def test_exhausted_denied(self):
        log, ks = ReceiptLog(), KillSwitch()
        g = Gate(KEY, log, ks)
        c = dict(caps()[0]); c["max_uses"] = 0  # capability unlimited; permit budget binds
        _, token = mint_permit("clerk-7", [c], KEY, max_uses=2)
        g.attempt(token, Action("crm.read", "crm://contacts/1"))
        g.attempt(token, Action("crm.read", "crm://contacts/2"))
        d = g.attempt(token, Action("crm.read", "crm://contacts/3"))
        self.assertEqual(d.reason, "permit-exhausted")

    def test_approval_flow(self):
        log, ks = ReceiptLog(), KillSwitch()
        g = Gate(KEY, log, ks)
        c = dict(caps()[0]); c["always_approve"] = True
        _, token = mint_permit("clerk-7", [c], KEY)
        d = g.attempt(token, Action("crm.read", "crm://contacts/1"))
        self.assertEqual(d.verdict, REQUIRE_APPROVAL)
        self.assertTrue(d.pending)
        d2 = g.approve(d.decision_id, "marcus")
        self.assertTrue(d2.allowed)
        self.assertEqual(d2.reason, "approved-by-human")

    def test_approval_after_freeze_denied(self):
        log, ks = ReceiptLog(), KillSwitch()
        g = Gate(KEY, log, ks)
        c = dict(caps()[0]); c["always_approve"] = True
        _, token = mint_permit("clerk-7", [c], KEY)
        d = g.attempt(token, Action("crm.read", "crm://contacts/1"))
        ks.freeze("agent:clerk-7", "rogue")
        d2 = g.approve(d.decision_id, "marcus")
        self.assertFalse(d2.allowed)


class TestReceiptLog(unittest.TestCase):
    def test_chain_verifies(self):
        log = ReceiptLog()
        log.append({"kind": "x"}); log.append({"kind": "y"})
        ok, _ = log.verify()
        self.assertTrue(ok)

    def test_tamper_detected(self):
        log = ReceiptLog()
        log.append({"kind": "x"}); log.append({"kind": "y"})
        log.entries[0]["event"]["kind"] = "forged"
        ok, msg = log.verify()
        self.assertFalse(ok)
        self.assertIn("tampered", msg)


class TestKillSwitch(unittest.TestCase):
    def test_global_freeze(self):
        ks = KillSwitch()
        ks.freeze("global", "incident-12")
        self.assertTrue(ks.denied_by("any", "any.type").startswith("global"))
        ks.unfreeze("global")
        self.assertIsNone(ks.denied_by("any", "any.type"))

    def test_agent_and_capability_freeze(self):
        ks = KillSwitch()
        ks.freeze("agent:rogue-1", "off-script")
        self.assertIsNotNone(ks.denied_by("rogue-1", "db.write"))
        self.assertIsNone(ks.denied_by("clerk-7", "crm.read"))
        ks.freeze("capability:db.", "too broad")
        self.assertIsNotNone(ks.denied_by("clerk-7", "db.write"))

    def test_dead_man(self):
        ks = KillSwitch()
        ks.heartbeat("clerk-7", ts=1000.0)
        frozen = ks.sweep(now=1000.0 + 120, timeout_seconds=60)
        self.assertEqual(frozen, ["clerk-7"])
        self.assertIsNotNone(ks.denied_by("clerk-7", "crm.read"))


class TestForensics(unittest.TestCase):
    def test_bundle_roundtrip(self):
        b = build_bundle(incident_id="inc-1", policy_snapshot=caps(),
                         permits=[{"permit_id": "pmt_x"}],
                         receipts=[{"seq": 0}], killswitch_events=[],
                         chain_ok=True, key=KEY)
        ok, _ = verify_bundle(b, KEY)
        self.assertTrue(ok)

    def test_tampered_bundle_fails(self):
        b = build_bundle(incident_id="inc-1", policy_snapshot=caps(),
                         permits=[], receipts=[], killswitch_events=[],
                         chain_ok=True, key=KEY)
        b["receipts"].append({"seq": 99, "forged": True})
        ok, _ = verify_bundle(b, KEY)
        self.assertFalse(ok)

    def test_broken_chain_flagged(self):
        b = build_bundle(incident_id="inc-1", policy_snapshot=[],
                         permits=[], receipts=[], killswitch_events=[],
                         chain_ok=False, key=KEY)
        ok, msg = verify_bundle(b, KEY)
        self.assertFalse(ok)
        self.assertIn("chain", msg)


if __name__ == "__main__":
    unittest.main()
