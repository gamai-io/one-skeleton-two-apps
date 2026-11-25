# Requirements — invoice_check (ulaz robe)

## Purpose
Book a supplier invoice and prove the booking is right before it reaches the ledger.

## User stories
1. As a bookkeeper I photograph/enter a supplier invoice and the agent proposes the booking.
2. As a controller I want the system to refuse a booking whose VAT is not 17% or whose sum
   does not add up.
3. As an auditor I want a signed receipt per invoice, verifiable offline.

## Acceptance criteria
- Agent claim: supplier, base, vat, total.
- Probe re-reads the invoice and reports: supplier, base, vat, total, vat_ok, sum_ok,
  supplier_known, duplicate.
- VAT must equal base × 0.17 (±0.01); total must equal base + vat.
- Unknown supplier or duplicate invoice number → REFUTED.
- Missing observation (e.g. unreadable scan) → UNVERIFIABLE, never CONFIRMED.
