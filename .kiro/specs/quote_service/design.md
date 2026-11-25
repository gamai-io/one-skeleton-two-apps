# Design — quote_service

```
request(lines, service, months)
      │
      ├── agent: quote()   → claim {machines, service, net, vat, total}
      │
      ├── probe: probe()   → observed {same fields, recomputed from CATALOG/SERVICE/VAT}
      │
      └── judge(claim, observed) → CONFIRMED | REFUTED | UNVERIFIABLE
                                    │
                                    └── Receipt.seal(prev_hash) → Ledger
```

- Catalogue and service levels are module constants; no I/O.
- Numbers are floats rounded at the edge (2 dp) to keep the demo dependency-free.
- The probe deliberately does not read the agent's output.
