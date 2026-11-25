"""Shared skeleton module: signed evidence receipts.

Both demo apps import this. One skeleton, two very different apps.
No third-party deps: hashlib + hmac (HMAC stands in for Ed25519 so the demo runs anywhere).
"""
from __future__ import annotations

import hashlib
import hmac
import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any

SECRET = b"kiroween-skeleton-demo-key"


def canon(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass
class Receipt:
    """One agent action, its claim, the independent check, and the verdict."""

    agent: str
    action: str
    claim: dict
    probe: dict
    verdict: str = "UNVERIFIABLE"
    reason: str = ""
    receipt_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    ts: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    prev_hash: str = ""
    hash: str = ""
    signature: str = ""

    def seal(self, prev_hash: str = "") -> "Receipt":
        self.prev_hash = prev_hash
        body = self.body()
        self.hash = sha256(canon(body))
        self.signature = hmac.new(SECRET, self.hash.encode(), hashlib.sha256).hexdigest()
        return self

    def body(self) -> dict:
        d = asdict(self)
        for k in ("hash", "signature"):
            d.pop(k, None)
        return d

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=1, ensure_ascii=False)


def judge(claim: dict, probe: dict) -> tuple[str, str]:
    """Deterministic adjudication: the probe decides, not the agent.

    Rules (same in both apps):
      - probe missing the field it was asked about  -> UNVERIFIABLE
      - probe value differs from the claim          -> REFUTED
      - probe confirms every claimed field          -> CONFIRMED
    """
    if not probe:
        return "UNVERIFIABLE", "probe produced no evidence"
    for key, claimed in claim.items():
        if key not in probe:
            return "UNVERIFIABLE", f"probe did not observe '{key}'"
        observed = probe[key]
        if isinstance(claimed, (int, float)) and isinstance(observed, (int, float)):
            if abs(float(claimed) - float(observed)) > 0.01:
                return "REFUTED", f"{key}: claimed {claimed}, observed {observed}"
        elif claimed != observed:
            return "REFUTED", f"{key}: claimed {claimed!r}, observed {observed!r}"
    return "CONFIRMED", "probe reproduced every claimed field"


class Ledger:
    """Hash-chained list of receipts; verify() proves nothing was edited."""

    def __init__(self) -> None:
        self.items: list[Receipt] = []

    def append(self, receipt: Receipt) -> Receipt:
        prev = self.items[-1].hash if self.items else ""
        receipt.seal(prev)
        self.items.append(receipt)
        return receipt

    def verify(self) -> dict:
        prev = ""
        for i, r in enumerate(self.items):
            if r.prev_hash != prev:
                return {"ok": False, "at": i, "why": "prev_hash mismatch"}
            if r.hash != sha256(canon(r.body())):
                return {"ok": False, "at": i, "why": "body hash mismatch"}
            expected = hmac.new(SECRET, r.hash.encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(expected, r.signature):
                return {"ok": False, "at": i, "why": "signature mismatch"}
            prev = r.hash
        return {"ok": True, "count": len(self.items), "head": prev}
