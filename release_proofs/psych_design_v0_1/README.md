# Psych-design companion v0.1 release proof

This directory governs the two-platform clean-reader proof for the unchanged
PyStatsV1 0.26.0 release candidate. Stage 1 runs the native Ubuntu proof from a
canonical wheel, commits its machine-readable evidence, and exports a WSL proof
kit. Stage 2 accepts only a validated WSL result package, compares the two
receipts, and may then open and merge the Drop-in 034 pull request.

The WSL route rejects native Linux and WSL1, requires Windows interop for environment facts, and avoids persisting absolute user-home paths in committed receipts.

The proof does not alter the ten datasets, analyses, R implementations,
verification policies, figures, APA bindings, or matched limitations. It does
not create `v0.26.0`, publish to PyPI, edit the portal or book, or authorize real
data. PNG bytes may differ because of renderer/font details; their registered
specifications, dimensions, roles, source bindings, labels, and statistical
content may not drift.
