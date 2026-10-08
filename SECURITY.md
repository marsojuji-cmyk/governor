# Security Policy

## What this repository is

`governor` gates agent actions on expiring HMAC permits and hash-chained receipts.

## Reporting a vulnerability

**Preferred: GitHub private vulnerability reporting.** Open the **Security** tab on this repository and
choose **Report a vulnerability**. That channel is private between you and the maintainer, requires no
email, and nothing is posted publicly. Private reporting is enabled on this repository.

If you cannot use that channel, open a **minimal public issue** stating only that you have a security
report and how to reach you. Please do **not** include exploit details, proof-of-concept code, or
affected-version specifics in a public issue.

## Scope

**In scope:**
- Permit forgeability, replay, scope bypass, or signature verification defects.
- Hash-chain corruption or receipt log tampering that goes undetected.
- Kill-switch bypass or failure to freeze targeted agents.

**Out of scope / stated plainly:**
- Governor is a software gate within the application runtime; it cannot prevent actions taken entirely outside its execution boundary.

## What to expect

| Stage | Commitment |
|---|---|
| Acknowledgement of your report | within 7 days |
| Initial assessment and severity call | within 14 days |
| Fix, or an agreed public disclosure | coordinated with you |

You will be credited in the fix or advisory unless you ask to remain anonymous.

## What this policy does NOT offer

There is **no bug bounty**, and no monetary reward is offered or implied. This is an independent
research project maintained by one person. What it can offer is a fast, honest response and public
credit.

## Related

- Threat model: see [`THREAT_MODEL.md`](THREAT_MODEL.md) for trust boundaries, attacker capabilities, and defenses.
- Review methodology: see the `adversarial-seat` repository for the review method, and `hermes-refuse` for fail-closed execution.
