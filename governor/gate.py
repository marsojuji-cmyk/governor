"""The enforcement point. Every action passes through the gate; every
decision — allowed or denied — lands on the receipt log.

Order of checks is load-bearing:
  1. permit integrity (bad token fails closed)
  2. kill-switch (a frozen agent cannot act, permit or not)
  3. permit budgets (total uses, expiry already checked at verify)
  4. policy evaluation (the capability check)

`require_approval` pauses the decision: approve() completes it with a human
in the loop, re-checking freeze and expiry at approval time.
"""
from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field

from .permit import PermitError, verify_token
from .policy import Action, Policy, ALLOW, DENY, REQUIRE_APPROVAL
from .receipt import ReceiptLog
from .killswitch import KillSwitch


@dataclass
class Decision:
    decision_id: str
    agent_id: str
    action: Action
    verdict: str          # allow | deny | require_approval
    reason: str
    ts: float
    permit_id: str = ""
    pending: bool = False
    approver: str = ""

    @property
    def allowed(self) -> bool:
        return self.verdict == ALLOW and not self.pending


class Gate:
    def __init__(self, key: bytes, receipt_log: ReceiptLog, killswitch: KillSwitch):
        self._key = key
        self._log = receipt_log
        self._ks = killswitch
        self._uses: dict[str, list[float]] = {}   # permit_id -> action timestamps
        self._pending: dict[str, tuple[str, Action]] = {}  # decision_id -> (token, action)

    def _uses_in_window(self, permit_id: str, window: int, now: float) -> int:
        cutoff = now - window
        stamps = [t for t in self._uses.get(permit_id, []) if t >= cutoff]
        self._uses[permit_id] = stamps
        return len(stamps)

    def attempt(self, token: str, action: Action, now: float | None = None) -> Decision:
        now = now if now is not None else time.time()
        try:
            permit = verify_token(token, self._key, now)
        except PermitError as e:
            return self._record(Decision(
                decision_id="dec_" + secrets.token_hex(6), agent_id="?",
                action=action, verdict=DENY, reason=f"bad-permit:{e}", ts=now))

        frozen = self._ks.denied_by(permit.agent_id, action.type)
        if frozen:
            return self._record(Decision(
                decision_id="dec_" + secrets.token_hex(6), agent_id=permit.agent_id,
                action=action, verdict=DENY, reason=f"frozen:{frozen}",
                ts=now, permit_id=permit.permit_id))

        total_uses = len(self._uses.get(permit.permit_id, []))
        if permit.max_uses > 0 and total_uses >= permit.max_uses:
            return self._record(Decision(
                decision_id="dec_" + secrets.token_hex(6), agent_id=permit.agent_id,
                action=action, verdict=DENY, reason="permit-exhausted",
                ts=now, permit_id=permit.permit_id))

        policy = Policy.from_dicts(permit.capabilities)
        # windowed uses: use the tightest window among matching caps
        windows = [c.window_seconds for c in policy.capabilities if c.matches(action)]
        window = min(windows) if windows else 3600
        evaluation = policy.evaluate(action, self._uses_in_window(permit.permit_id, window, now))

        decision = Decision(
            decision_id="dec_" + secrets.token_hex(6),
            agent_id=permit.agent_id, action=action,
            verdict=evaluation.verdict, reason=evaluation.reason,
            ts=now, permit_id=permit.permit_id,
            pending=(evaluation.verdict == REQUIRE_APPROVAL),
        )
        if decision.pending:
            self._pending[decision.decision_id] = (token, action)
        else:
            self._uses.setdefault(permit.permit_id, []).append(now)
        return self._record(decision)

    def approve(self, decision_id: str, approver: str, now: float | None = None) -> Decision:
        """Complete a pending require_approval decision. Re-checks everything."""
        now = now if now is not None else time.time()
        if decision_id not in self._pending:
            raise KeyError("unknown-or-settled-decision")
        token, action = self._pending.pop(decision_id)
        try:
            permit = verify_token(token, self._key, now)
        except PermitError as e:
            return self._record(Decision(
                decision_id=decision_id, agent_id="?", action=action,
                verdict=DENY, reason=f"bad-permit-at-approval:{e}",
                ts=now, approver=approver))
        frozen = self._ks.denied_by(permit.agent_id, action.type)
        if frozen:
            return self._record(Decision(
                decision_id=decision_id, agent_id=permit.agent_id, action=action,
                verdict=DENY, reason=f"frozen-at-approval:{frozen}",
                ts=now, permit_id=permit.permit_id, approver=approver))
        self._uses.setdefault(permit.permit_id, []).append(now)
        return self._record(Decision(
            decision_id=decision_id, agent_id=permit.agent_id, action=action,
            verdict=ALLOW, reason="approved-by-human", ts=now,
            permit_id=permit.permit_id, approver=approver))

    def _record(self, decision: Decision) -> Decision:
        self._log.append({
            "kind": "decision",
            "decision_id": decision.decision_id,
            "agent_id": decision.agent_id,
            "permit_id": decision.permit_id,
            "action": {"type": decision.action.type,
                       "resource": decision.action.resource,
                       "amount": decision.action.amount,
                       "meta": decision.action.meta},
            "verdict": decision.verdict,
            "reason": decision.reason,
            "pending": decision.pending,
            "approver": decision.approver,
        })
        return decision
