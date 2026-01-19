# SPDX-License-Identifier: MIT

from __future__ import annotations

import re
from pathlib import Path


def test_docs_do_not_use_positional_dest_for_workbook_init() -> None:
    """Guardrail: our docs should not show the old positional-dest syntax.

    The CLI uses --dest (and does not accept a positional destination).
    """

    docs_root = Path("docs/source")
    assert docs_root.exists(), "docs/source missing"

    bad_patterns = [
        re.compile(r"pystatsv1\s+workbook\s+init\s+\./"),
        re.compile(r"pystatsv1\s+workbook\s+init\s+--track\s+[a-z]\s+\./"),
    ]

    offenders: list[str] = []

    for path in sorted(docs_root.rglob("*.rst")):
        txt = path.read_text(encoding="utf-8")
        for pat in bad_patterns:
            m = pat.search(txt)
            if m:
                # Provide a small excerpt to make fixes trivial.
                start = max(0, m.start() - 40)
                end = min(len(txt), m.end() + 40)
                excerpt = txt[start:end].replace("\n", "\\n")
                offenders.append(f"{path}: {excerpt}")
                break

    assert not offenders, "Found old positional-dest workbook init syntax in docs:\n" + "\n".join(
        offenders
    )
