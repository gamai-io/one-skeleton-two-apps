"""App 1 (from the shared skeleton): machine-sales quote.

GAMA TRADE sells and services machines (compressors). This app turns a request
("3 compressors KS-22, service package, 12 months") into a priced quote and emits
a signed receipt proving the arithmetic is right.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "packages" / "receipt"))
from receipt import Ledger, Receipt, judge  # noqa: E402

CATALOG = {"KS-22": 4200.0, "KS-45": 7600.0, "KS-75": 12900.0}
SERVICE = {"basic": 0.05, "standard": 0.09, "full": 0.14}   # share of machine value / year
VAT = 0.17                                                   # BiH

def quote(lines: list[tuple[str, int]], service: str, months: int) -> dict:
    machines = sum(CATALOG[m] * q for m, q in lines)
    service_fee = machines * SERVICE[service] * (months / 12)
    net = machines + service_fee
    vat = round(net * VAT, 2)
    return {"machines": round(machines, 2), "service": round(service_fee, 2),
            "net": round(net, 2), "vat": vat, "total": round(net + vat, 2)}

def probe(lines: list[tuple[str, int]], service: str, months: int) -> dict:
    """Independent recomputation from the catalogue, not from the agent's numbers."""
    machines = sum(CATALOG[m] * q for m, q in lines)
    service_fee = machines * SERVICE[service] * (months / 12)
    net = machines + service_fee
    return {"machines": round(machines, 2), "service": round(service_fee, 2),
            "net": round(net, 2), "vat": round(net * VAT, 2),
            "total": round(net + round(net * VAT, 2), 2)}

def run(ledger: Ledger) -> dict:
    lines, service, months = [("KS-22", 3)], "standard", 12
    claim = quote(lines, service, months)
    observed = probe(lines, service, months)
    verdict, reason = judge(claim, observed)
    r = ledger.append(Receipt(agent="quote-agent", action=f"quote {lines} {service} {months}m",
                              claim=claim, probe=observed, verdict=verdict, reason=reason))
    return {"app": "quote_service", "verdict": verdict, "reason": reason,
            "claim": claim, "receipt": r.receipt_id, "hash": r.hash[:16]}

if __name__ == "__main__":
    led = Ledger()
    print(run(led))
    print("ledger:", led.verify())
