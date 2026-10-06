"""Capability scopes and policy evaluation.

Pure: no I/O, no clock reads except the caller's timestamps. A Policy is the
set of capabilities granted to one agent; evaluation is exact and total — every
action gets exactly one verdict, stated with a reason code.

Verdicts: "allow" | "deny" | "require_approval".
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatchcase

ALLOW = "allow"
DENY = "deny"
REQUIRE_APPROVAL = "require_approval"


@dataclass(frozen=True)
class Action:
    """One thing an agent wants to do."""
    type: str            # e.g. "crm.read", "db.write", "http.post"
    resource: str        # e.g. "crm://contacts/4821"
    amount: float = 0.0  # money moved, if any
    meta: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Capability:
    """One grant inside a permit."""
    action_types: tuple   # fnmatch patterns, e.g. ("crm.*",)
    resources: tuple      # prefixes, e.g. ("crm://contacts/",)
    max_amount: float = 0.0        # 0.0 = no money may move on this grant
    max_uses: int = 0             # 0 = unlimited within the window
    window_seconds: int = 3600
    approval_above: float = 0.0   # amount above which a human must approve; 0 = never
    always_approve: bool = False   # True: every matching action needs approval

    def matches(self, action: Action) -> bool:
        type_ok = any(fnmatchcase(action.type, pat) for pat in self.action_types)
        res_ok = action.resource.startswith(self.resources)
        return type_ok and res_ok


@dataclass(frozen=True)
class Evaluation:
    verdict: str
    reason: str
    capability: "Capability | None" = None


class Policy:
    """The capability set granted to one agent. First match wins."""

    def __init__(self, capabilities: list[Capability]):
        self.capabilities = list(capabilities)

    @classmethod
    def from_dicts(cls, dicts: list[dict]) -> "Policy":
        caps = []
        for d in dicts:
            caps.append(Capability(
                action_types=tuple(d.get("action_types", ())),
                resources=tuple(d.get("resources", ())),
                max_amount=float(d.get("max_amount", 0.0)),
                max_uses=int(d.get("max_uses", 0)),
                window_seconds=int(d.get("window_seconds", 3600)),
                approval_above=float(d.get("approval_above", 0.0)),
                always_approve=bool(d.get("always_approve", False)),
            ))
        return cls(caps)

    def to_dicts(self) -> list[dict]:
        return [dict(
            action_types=list(c.action_types),
            resources=list(c.resources),
            max_amount=c.max_amount,
            max_uses=c.max_uses,
            window_seconds=c.window_seconds,
            approval_above=c.approval_above,
            always_approve=c.always_approve,
        ) for c in self.capabilities]

    def evaluate(self, action: Action, uses_in_window: int) -> Evaluation:
        """Evaluate one action. Exact, total, no discretion.

        Order of checks is load-bearing: identity of grant first, then
        hard ceilings (amount, rate), then the approval gate.
        """
        cap = next((c for c in self.capabilities if c.matches(action)), None)
        if cap is None:
            return Evaluation(DENY, "no-capability")
        if action.amount > cap.max_amount:
            return Evaluation(DENY, "amount-exceeds-cap", cap)
        if cap.max_uses > 0 and uses_in_window >= cap.max_uses:
            return Evaluation(DENY, "rate-exceeded", cap)
        if cap.always_approve or (cap.approval_above > 0 and action.amount > cap.approval_above):
            return Evaluation(REQUIRE_APPROVAL, "approval-required", cap)
        return Evaluation(ALLOW, "within-permit", cap)
