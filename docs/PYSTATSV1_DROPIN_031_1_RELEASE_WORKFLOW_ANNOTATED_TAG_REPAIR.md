# PyStatsV1 Drop-in 031.1 — Release Workflow Annotated-Tag Checkout Repair

## Purpose

Repair the manual trusted-publisher workflow after an otherwise valid annotated
``v0.25.1`` tag failed in GitHub Actions. The original workflow was dispatched at
the tag ref, but ``actions/checkout`` materialized a commit-shaped local tag ref.
The release verifier correctly rejected that local lightweight ref even though the
remote ``v0.25.1`` tag itself is annotated.

## What changes

The workflow now accepts an explicit ``release_tag`` input while it is dispatched
from ``main``. It checks out the requested release source, force-fetches that exact
``refs/tags/<tag>`` ref from ``origin`` into the local tag namespace, verifies that
the ref is an annotated tag, verifies that it resolves to the checked-out commit,
and only then invokes the existing package-version release gate.

The canonical dispatch command is:

```bash
gh workflow run pypi-publish.yml --ref main -f release_tag=v0.25.1
```

## Boundaries

This is workflow-only release infrastructure. It does not change the package
version, Chapter 20 calculation, public Book 1 Companion v0.2 asset, existing
``v0.25.0`` or ``v0.25.1`` tags, or the LearnToProgram portal's Book 1 proof
binding.

## Validation intent

The regression test asserts the workflow contains the explicit input, release-source
checkout, tag re-fetch, annotated-tag type check, commit-equivalence check, and
existing Python release checker.
