"""The kill-switch. Global halt, scoped freeze, dead-man heartbeat.

Scopes: "global" (everything stops), "agent:<id>", "capability:<action-type>".
A freeze is an event on the record, not a silent flag — every freeze and
unfreeze is timestamped with actor and reason, and feeds the forensics bundle.

The dead-man heartbeat inverts the usual control: the agent must check in.
Missed check-ins freeze it. A rogue agent that stops phoning home cannot keep
acting — silence is itself the tripwire.
"""
from __future__ import annotations

import time


class KillSwitch:
    def __init__(self):
        self._global: dict | None = None
        self._agents: dict[str, dict] = {}
        self._capabilities: dict[str, dict] = {}
        self._beats: dict[str, float] = {}
        self.events: list[dict] = []

    def freeze(self, scope: str, reason: str, actor: str = "operator",
               ts: float | None = None) -> None:
        """scope: 'global', 'agent:<id>', or 'capability:<type>'."""
        ts = ts if ts is not None else time.time()
        record = {"scope": scope, "reason": reason, "actor": actor, "ts": ts}
        if scope == "global":
            self._global = record
        elif scope.startswith("agent:"):
            self._agents[scope[6:]] = record
        elif scope.startswith("capability:"):
            self._capabilities[scope[11:]] = record
        else:
            raise ValueError("bad-scope")
        self.events.append({"kind": "freeze", **record})

    def unfreeze(self, scope: str, actor: str = "operator",
                 ts: float | None = None) -> None:
        ts = ts if ts is not None else time.time()
        if scope == "global":
            self._global = None
        elif scope.startswith("agent:"):
            self._agents.pop(scope[6:], None)
        elif scope.startswith("capability:"):
            self._capabilities.pop(scope[11:], None)
        else:
            raise ValueError("bad-scope")
        self.events.append({"kind": "unfreeze", "scope": scope, "actor": actor, "ts": ts})

    def denied_by(self, agent_id: str, action_type: str) -> str | None:
        """None if clear; otherwise the freeze reason that blocks this action."""
        if self._global:
            return f"global:{self._global['reason']}"
        if agent_id in self._agents:
            return f"agent:{self._agents[agent_id]['reason']}"
        for cap, rec in self._capabilities.items():
            if action_type == cap or action_type.startswith(cap.rstrip("*")):
                return f"capability:{rec['reason']}"
        return None

    def heartbeat(self, agent_id: str, ts: float | None = None) -> None:
        self._beats[agent_id] = ts if ts is not None else time.time()

    def sweep(self, now: float | None = None, timeout_seconds: int = 60) -> list[str]:
        """Freeze every agent whose heartbeat is stale. Returns frozen ids."""
        now = now if now is not None else time.time()
        frozen = []
        for agent_id, last in self._beats.items():
            if now - last > timeout_seconds and agent_id not in self._agents:
                self.freeze(f"agent:{agent_id}", "dead-man:heartbeat-stale",
                            actor="killswitch", ts=now)
                frozen.append(agent_id)
        return frozen

    @property
    def is_global_freeze(self) -> bool:
        return self._global is not None
