# SAS to Python: Customer Payment Join

A side-by-side SAS and Python implementation of the same payment-processing
job, plus an automated parity check that proves the two outputs match.

## Why this exists

Most SAS-to-Python migrations don't fail on the obvious code — they fail on
edge cases where the two languages handle missing values, types, or sort
order differently. This repo shows the full loop: translate the code, run
both versions, verify the outputs are identical.

## The job

Apply a monthly payment file to a customer account file:

1. Left-join payments to accounts on `customer_number`.
2. Subtract `payment_amount` from `account_balance`.
3. Record `payment_date` as `last_payment`.
4. Write the updated accounts to a new file.

## Repo layout

    data/         Input CSVs and generated outputs
    sas/          SAS implementation
    python/       Python (pandas) implementation
    validation/   Parity check comparing both outputs

## Run it

    # Python
    python python/payment_processing.py

    # SAS (SAS Studio or Base SAS, with working directory at repo root)
    %include "sas/payment_processing.sas";

    # Verify the two outputs match
    python validation/parity_check.py

## The gotcha this repo highlights

A naive left join leaves `payment_amount` missing (`NaN` in pandas, `.` in
SAS) for customers who didn't pay this month. Subtracting that from
`account_balance` silently destroys the balance.

- **Python fix:** `df["payment_amount"].fillna(0)` before the subtraction.
- **SAS fix:** `coalesce(b.payment_amount, 0)` inside the `PROC SQL` select.

The included sample data contains two customers with no September payment
specifically to exercise this case. The parity check confirms both
implementations handle it the same way.

## Requirements

- SAS 9.4+ (or SAS Studio / SAS OnDemand)
- Python 3.9+, pandas 1.0+

## Author

Daryl Reavis — SAS programmer focused on legacy SAS maintenance and
SAS-to-Python migration with output parity validation.
