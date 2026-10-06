"""Hash-chained, append-only receipt log. JSONL on disk, memory otherwise.

Every entry binds to the previous entry's hash. Tampering with any entry
breaks every later hash — verify() finds the first break. This is the
Interlock-compatible half of the system: what the agent did, in an order
nobody can silently rewrite.

The Astra lesson: the agent's own log said "no writes performed." The receipt
chain says otherwise. When the two disagree, the chain wins.
"""
from __future__ import annotations

import hashlib
import json
import time

GENESIS_HASH = "0" * 64


def _canonical(obj: dict) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _hash(entry: dict) -> str:
    return hashlib.sha256(_canonical(entry)).hexdigest()


class ReceiptLog:
    def __init__(self, path: str | None = None):
        self.path = path
        self.entries: list[dict] = []
        if path:
            self.load()

    def append(self, event: dict, ts: float | None = None) -> dict:
        entry = {
            "seq": len(self.entries),
            "ts": ts if ts is not None else time.time(),
            "prev_hash": self.entries[-1]["hash"] if self.entries else GENESIS_HASH,
            "event": event,
        }
        entry["hash"] = _hash({k: entry[k] for k in ("seq", "ts", "prev_hash", "event")})
        self.entries.append(entry)
        if self.path:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        return entry

    def verify(self) -> tuple[bool, str]:
        """Returns (ok, message). Finds the first broken link."""
        prev = GENESIS_HASH
        for e in self.entries:
            if e["prev_hash"] != prev:
                return False, f"broken-link-at-seq-{e['seq']}"
            if e["hash"] != _hash({k: e[k] for k in ("seq", "ts", "prev_hash", "event")}):
                return False, f"tampered-entry-at-seq-{e['seq']}"
            prev = e["hash"]
        return True, f"chain-ok-{len(self.entries)}-entries"

    def load(self) -> None:
        self.entries = []
        try:
            with open(self.path, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        self.entries.append(json.loads(line))
        except FileNotFoundError:
            pass

    def window(self, start_ts: float, end_ts: float) -> list[dict]:
        return [e for e in self.entries if start_ts <= e["ts"] <= end_ts]
