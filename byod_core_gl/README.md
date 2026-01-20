# Track D — Bring Your Own Data (BYOD)

This folder is a starter project for using your own accounting data with Track D.

## What to edit

- `tables/` contains **student-edited** CSVs.
  Header-only templates are generated from the Track D contract.

## What not to edit

- `normalized/` is for **generated** outputs from future adapters.

## Quickstart

1) Fill in the required CSVs under `tables/`.
2) Validate your dataset:

   ```bash
   pystatsv1 trackd validate --datadir tables --profile core_gl
   ```

If validation fails, fix the missing files/columns and re-run.
