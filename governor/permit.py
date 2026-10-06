"""HMAC-signed action permits. Stdlib only.

A permit is a signed grant of capabilities to one agent. The token is
self-contained: `g1.<base64url-payload>.<hex-hmac>`. Verification needs only
the key — no database, no network. A forged or edited token fails closed.

Payload fields: permit_id, agent_id, capabilities (list of dicts, see policy),
issued_at, expires_at, max_uses (0 = unlimited), nonce.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from dataclasses import dataclass, field

TOKEN_PREFIX = "g1"


class PermitError(Exception):
    """Any permit failure: malformed, forged, expired, or exhausted."""


def _b64e(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64d(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


@dataclass
class ActionPermit:
    permit_id: str
    agent_id: str
    capabilities: list = field(default_factory=list)
    issued_at: float = 0.0
    expires_at: float = 0.0
    max_uses: int = 0
    nonce: str = ""

    def to_dict(self) -> dict:
        return {
            "permit_id": self.permit_id,
            "agent_id": self.agent_id,
            "capabilities": self.capabilities,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "max_uses": self.max_uses,
            "nonce": self.nonce,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ActionPermit":
        return cls(
            permit_id=d["permit_id"],
            agent_id=d["agent_id"],
            capabilities=d.get("capabilities", []),
            issued_at=float(d.get("issued_at", 0.0)),
            expires_at=float(d.get("expires_at", 0.0)),
            max_uses=int(d.get("max_uses", 0)),
            nonce=d.get("nonce", ""),
        )

    def expired(self, now: float | None = None) -> bool:
        return (now if now is not None else time.time()) >= self.expires_at


def _sign(payload_b64: str, key: bytes) -> str:
    msg = f"{TOKEN_PREFIX}.{payload_b64}".encode("ascii")
    return hmac.new(key, msg, hashlib.sha256).hexdigest()


def mint_permit(agent_id: str, capabilities: list[dict], key: bytes,
                ttl_seconds: int = 3600, max_uses: int = 0) -> tuple[ActionPermit, str]:
    """Mint a permit and its token. The key never leaves the issuer."""
    now = time.time()
    permit = ActionPermit(
        permit_id="pmt_" + secrets.token_hex(8),
        agent_id=agent_id,
        capabilities=capabilities,
        issued_at=now,
        expires_at=now + ttl_seconds,
        max_uses=max_uses,
        nonce=secrets.token_hex(12),
    )
    payload = _b64e(json.dumps(permit.to_dict(), sort_keys=True, separators=(",", ":")).encode())
    return permit, f"{TOKEN_PREFIX}.{payload}.{_sign(payload, key)}"


def verify_token(token: str, key: bytes, now: float | None = None) -> ActionPermit:
    """Verify a token. Raises PermitError on anything wrong. Fails closed."""
    try:
        prefix, payload_b64, sig = token.split(".")
    except ValueError:
        raise PermitError("malformed-token")
    if prefix != TOKEN_PREFIX:
        raise PermitError("malformed-token")
    if not hmac.compare_digest(_sign(payload_b64, key), sig):
        raise PermitError("bad-signature")
    try:
        permit = ActionPermit.from_dict(json.loads(_b64d(payload_b64)))
    except Exception:
        raise PermitError("malformed-payload")
    if permit.expired(now):
        raise PermitError("expired")
    return permit
