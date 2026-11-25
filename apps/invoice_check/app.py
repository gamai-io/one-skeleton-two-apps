"""App 2 (from the same skeleton): supplier invoice check (ulaz robe).

Very different domain, same skeleton + same receipt format: the agent books a
supplier invoice; the probe re-reads it and recomputes VAT 17% and the total.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "packages" / "receipt"))
from receipt import Ledger, Receipt, judge  # noqa: E402

VAT = 0.17

def agent_book(raw: dict) -> dict:
    """What the agent claims after reading the invoice."""
    return {"supplier": raw["supplier"], "base": raw["base"],
            "vat": raw["vat"], "total": raw["total"]}

def probe_check(raw: dict, known_suppliers: set[str]) -> dict:
    """Independent check: known supplier, VAT rate, sum, not a duplicate."""
    base, vat, total = raw["base"], raw["vat"], raw["total"]
    vat_ok = round(base * VAT, 2) == round(vat, 2)
    sum_ok = round(base + vat, 2) == round(total, 2)
    known = raw["supplier"] in known_suppliers
    dup = raw.get("seen_before", False)
    # probe reports only what it could verify from the document + master data
    return {"supplier": raw["supplier"], "base": base,
            "vat": vat if vat_ok else round(base * VAT, 2),
            "total": total if sum_ok else round(base + vat, 2),
            "vat_ok": vat_ok, "sum_ok": sum_ok,
            "supplier_known": known, "duplicate": dup}

def run(ledger: Ledger, raw: dict, known: set[str]) -> dict:
    claim = agent_book(raw)
    observed = probe_check(raw, known)
    # claim is about amounts; map the probe booleans into the claim space
    check = {"supplier": raw["supplier"], "base": raw["base"], "vat": raw["vat"],
             "total": raw["total"], "vat_ok": True, "sum_ok": True,
             "supplier_known": True, "duplicate": False}
    verdict, reason = judge(check, observed)
    r = ledger.append(Receipt(agent="invoice-agent", action=f"book invoice {raw['supplier']} {raw['total']}",
                              claim=claim, probe=observed, verdict=verdict, reason=reason))
    return {"app": "invoice_check", "verdict": verdict, "reason": reason,
            "invoice": raw, "receipt": r.receipt_id, "hash": r.hash[:16]}

if __name__ == "__main__":
    known = {"Mann+Hummel d.o.o.", "Belamionix d.o.o."}
    good = {"supplier": "Mann+Hummel d.o.o.", "base": 1450.00, "vat": 246.50, "total": 1696.50}
    bad = {"supplier": "Mann+Hummel d.o.o.", "base": 1450.00, "vat": 290.00, "total": 1740.00}
    led = Ledger()
    print(run(led, good, known))
    print(run(led, bad, known))
    print("ledger:", led.verify())
