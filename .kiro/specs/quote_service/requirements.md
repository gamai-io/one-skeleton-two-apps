# Requirements — quote_service

## Purpose
Turn a machine-sales request into a priced quote that a customer can check line by line.

## User stories
1. As a salesperson I enter machines and quantities and get a quote with machines, service,
   net, VAT 17% and total.
2. As a customer I can recompute every number from the catalogue and the VAT rate.
3. As an auditor I get a receipt that proves the numbers in the quote were verified.

## Acceptance criteria
- `quote()` returns exactly: machines, service, net, vat, total.
- Service fee = machine value × service level share × (months/12).
- VAT is 17% of net, rounded to 2 decimals.
- The probe recomputes all five fields from the catalogue, never from the quote.
- Verdict is CONFIRMED only if every field matches; otherwise REFUTED with the first mismatch.
