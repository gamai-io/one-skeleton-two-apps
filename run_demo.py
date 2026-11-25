#!/usr/bin/env python3
"""Run both apps from one skeleton and prove the evidence chain.

  python3 run_demo.py          # both apps + ledger verification
  python3 run_demo.py --tamper # prove an edited verdict breaks the chain
"""
import json
import sys
from pathlib import Path

import importlib.util

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "packages" / "receipt"))
from receipt import Ledger  # noqa: E402


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


quote_app = load("quote_app", "apps/quote_service/app.py")
invoice_app = load("invoice_app", "apps/invoice_check/app.py")


def main() -> int:
    ledger = Ledger()
    out = []
    out.append(quote_app.run(ledger))
    known = {"Mann+Hummel d.o.o.", "Belamionix d.o.o."}
    out.append(invoice_app.run(ledger, {"supplier": "Mann+Hummel d.o.o.", "base": 1450.00,
                                        "vat": 246.50, "total": 1696.50}, known))
    out.append(invoice_app.run(ledger, {"supplier": "Mann+Hummel d.o.o.", "base": 1450.00,
                                        "vat": 290.00, "total": 1740.00}, known))

    print("=== receipts")
    for r in out:
        print(f"  {r['app']:14s} {r['verdict']:12s} receipt={r['receipt']} hash={r['hash']}")
        if r["verdict"] != "CONFIRMED":
            print(f"                 reason: {r['reason']}")

    v = ledger.verify()
    print("=== chain:", json.dumps(v))

    if "--tamper" in sys.argv:
        ledger.items[2].verdict = "CONFIRMED"      # hide the lie
        bad = ledger.verify()
        print("=== after editing receipt #3:", json.dumps(bad))
        return 0 if (v["ok"] and not bad["ok"]) else 1
    return 0 if v["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
