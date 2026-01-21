# Track D — BYOD GnuCash Demo (core_gl)

This is a small runnable example project for the Track D BYOD pipeline using the
`gnucash_gl` adapter.

## Run

```bash
# 1) Normalize the raw export into canonical Track D tables
pystatsv1 trackd byod normalize --project .

# 2) Produce an analysis-ready daily time series
pystatsv1 trackd byod daily-totals --project .
```

Outputs are written under `normalized/`.
