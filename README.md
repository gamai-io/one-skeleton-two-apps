# One Skeleton, Two Apps — with receipts

**Kiroween 2026 · Skeleton Crew.** A skeleton lean enough to read in a few minutes, and
flexible enough that two completely different applications come out of it — plus a shared
evidence layer so the agent's claims can be checked by someone who does not trust the agent.

## The skeleton

```
packages/receipt/receipt.py   87 lines: canonical JSON, SHA-256 chain, HMAC signature,
                              deterministic judge(), ledger verify()
apps/quote_service/app.py    machine-sales quote (pricing, VAT 17%, total)
apps/invoice_check/app.py    supplier invoice entry (known supplier, VAT rate, sum, duplicate)
run_demo.py                  runs both apps, prints receipts, verifies the chain
.kiro/specs/*                the specs each app was generated from
```

Nothing else. No framework, no database, no build step: `python3 run_demo.py`.

## Why one skeleton fits two apps

Both apps are the same shape: **an agent produces a claim → something independent observes
the system → a verdict is sealed into a chain.** The only thing that differs is the domain
function (`quote()` vs `probe_check()`). That is the whole point of the skeleton: the
evidence layer stays identical, the domain plugs in.

| | quote_service | invoice_check |
|---|---|---|
| claim | machines + service + VAT + total | supplier + base + VAT + total |
| independent observation | recompute from the catalogue | re-read invoice, recompute VAT 17%, check master data |
| caught lie in the demo | — | VAT 290.00 instead of 246.50 → **REFUTED** |

## Run it

```bash
python3 run_demo.py            # both apps + chain verification
python3 run_demo.py --tamper   # edit one verdict -> chain rejects it
```

Expected:

```
quote_service  CONFIRMED   receipt=… hash=…
invoice_check  CONFIRMED   receipt=… hash=…
invoice_check  REFUTED     receipt=… hash=…   reason: vat: claimed 290.0, observed 246.5
chain: {"ok": true, "count": 3, "head": "…"}
after editing receipt #3: {"ok": false, "at": 2, "why": "body hash mismatch"}
```

## Spec-driven, Kiro-style

Each app has `.kiro/specs/<app>/{requirements,design,tasks}.md`. The specs are written
before the code and kept short on purpose: a spec you cannot read in one screen does not
survive contact with a real deadline.

## What this is not

Not an AI model, not a chatbot. It is the boring layer that makes an agent's output
auditable: who claimed what, what was actually observed, and a hash chain that proves the
record was not edited afterwards. HMAC stands in for Ed25519 here so the demo runs with the
Python standard library only; the production version signs with Ed25519.
