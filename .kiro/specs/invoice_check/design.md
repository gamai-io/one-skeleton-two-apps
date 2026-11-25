# Design — invoice_check

Same skeleton as quote_service; only the domain functions change.

```
raw invoice ──▶ agent_book()  → claim  {supplier, base, vat, total}
      │
      └───────▶ probe_check() → observed {supplier, base, vat, total,
                                           vat_ok, sum_ok, supplier_known, duplicate}
judge(claim, observed) → verdict → Receipt → Ledger
```

Deliberate asymmetry: the probe returns the *recomputed* vat/total when the document's
numbers are wrong, so the reason string shows the exact difference
(`vat: claimed 290.0, observed 246.5`).
