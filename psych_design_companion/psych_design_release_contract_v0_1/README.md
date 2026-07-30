# Psychological Statistics by Design companion release contract v0.1

This directory freezes the release identity and implementation boundaries for the
future public, synthetic-only executable companion. It is an audit and command
contract, not a released companion.

The three existing study batches remain byte-for-byte unchanged. The contract
selects SWL-S02 as the first-result route, plans PyStatsV1 0.26.0 with the
`psych-design` optional extra and CLI namespace, and records the exact gaps that
must be closed before publication.

Run the bounded gate from the repository root:

```bash
make psych-design-release-contract-verify
```

A passing marker does **not** authorize PyPI publication, portal deployment,
book command binding, or real-data use.
