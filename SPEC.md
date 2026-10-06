# governor — specification v0.1.0

Exact semantics. Where this document and the code disagree, the code is wrong
until fixed — file the discrepancy.

## 1. Actions

An `Action` is `(type, resource, amount, meta)`. `type` is a dotted verb
(`crm.read`); `resource` is a URI; `amount` is money moved (0.0 default);
`meta` carries anything else. Actions are values, not objects with behavior.

## 2. Capabilities and policy evaluation

A `Capability` grants:

| field | meaning | default |
|---|---|---|
| `action_types` | fnmatch patterns, e.g. `("crm.*",)` | `()` |
| `resources` | resource prefixes, e.g. `("crm://contacts/",)` | `()` |
| `max_amount` | money ceiling per action | `0.0` = none may move |
| `max_uses` | uses per window | `0` = unlimited |
| `window_seconds` | rate window | `3600` |
| `approval_above` | amount above which a human approves | `0.0` = never |
| `always_approve` | every matching action needs approval | `False` |

`Policy.evaluate(action, uses_in_window)` — first matching capability wins:

1. no capability matches → `deny / no-capability`
2. `action.amount > cap.max_amount` → `deny / amount-exceeds-cap`
3. `cap.max_uses > 0 and uses_in_window >= cap.max_uses` → `deny / rate-exceeded`
4. `cap.always_approve or (cap.approval_above > 0 and action.amount > cap.approval_above)` → `require_approval / approval-required`
5. otherwise → `allow / within-permit`

The order is load-bearing: grant identity, then hard ceilings, then the
approval gate. Safe defaults: `max_amount=0.0` denies any money movement
unless a grant explicitly raises the ceiling.

## 3. Permits

Token format: `g1.<base64url(payload)>.<hex-hmac-sha256>`, where the HMAC
covers the literal string `g1.<payload>` under the issuer key.

Payload: `permit_id` (`pmt_` + 16 hex), `agent_id`, `capabilities` (list of
dicts per §2), `issued_at`, `expires_at`, `max_uses` (0 = unlimited),
`nonce` (24 hex, uniqueness only).

`verify_token` fails closed with `PermitError` on: malformed structure,
unknown prefix, bad signature (constant-time compare), malformed payload,
expiry. There is no revocation list — permits are short-lived by design;
revocation is the kill-switch's job (§5).

## 4. The gate

`Gate.attempt(token, action)`:

1. `verify_token` → `PermitError` ⇒ `deny / bad-permit:<kind>`, agent `?`
2. `killswitch.denied_by(agent, type)` ⇒ `deny / frozen:<reason>`
3. `uses(permit_id) >= permit.max_uses > 0` ⇒ `deny / permit-exhausted`
4. `Policy.from_dicts(permit.capabilities).evaluate(action, uses_in_window)` ⇒ verdict
5. `require_approval` ⇒ decision parked as pending; `approve(id, approver)`
   re-runs checks 1–2, then allows with reason `approved-by-human`.
   Unknown or settled ids raise `KeyError`.

Every decision is appended to the receipt log before return — including
denials and pending approvals. Uses are recorded only for non-pending
decisions (an approval records its use at approval time).

`uses_in_window` uses the tightest window among matching capabilities.

## 5. Kill-switch

Scopes: `global`, `agent:<id>`, `capability:<prefix>`. `freeze`/`unfreeze`
record `(scope, reason, actor, ts)` on the event list. `denied_by` checks in
order: global → agent → capability prefix. Capability matching is prefix on
the action type.

`heartbeat(agent_id)` records the check-in. `sweep(now, timeout)` freezes
every agent whose last beat is older than the timeout, actor `killswitch`,
reason `dead-man:heartbeat-stale`. Silence trips the wire.

## 6. Receipt chain

JSONL entries: `{seq, ts, prev_hash, event, hash}` where
`hash = sha256(canonical(seq, ts, prev_hash, event))`. Genesis `prev_hash`
is 64 zeros. `verify()` returns the first broken link or tampered entry.
`window(start, end)` slices by timestamp.

## 7. Forensics bundle

`build_bundle(incident_id, policy_snapshot, permits, receipts,
killswitch_events, chain_ok, key)` → dict with `format:
"governor-forensics/1"` plus `signature = HMAC(key, canonical(bundle
minus signature))`. `verify_bundle` fails closed on: missing signature,
bad signature, `chain_ok == false`. A bundle over a broken chain verifies
as `bundle-ok` only if the chain is intact — the signature covers the
`chain_ok` flag, so it cannot be flipped after signing.
