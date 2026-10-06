"""governor — the action governor for superintelligent agents.

Permits, not trust — for behavior.

    Permit says what an agent may spend.
    Governor says what it may do.
    Interlock proves what it did.

Claim tiers on consequential claims in docs: verified / reported / inferred.
"""

__version__ = "0.1.0"

from .policy import Action, Capability, Policy, Evaluation, ALLOW, DENY, REQUIRE_APPROVAL
from .permit import ActionPermit, PermitError, mint_permit, verify_token
from .receipt import ReceiptLog
from .killswitch import KillSwitch
from .gate import Gate, Decision
from .forensics import build_bundle, verify_bundle

__all__ = [
    "Action", "Capability", "Policy", "Evaluation",
    "ALLOW", "DENY", "REQUIRE_APPROVAL",
    "ActionPermit", "PermitError", "mint_permit", "verify_token",
    "ReceiptLog", "KillSwitch", "Gate", "Decision",
    "build_bundle", "verify_bundle",
]
