from __future__ import annotations

from pystatsv1 import get_local_docs_path


def test_docs_pdf_is_packaged_and_exists() -> None:
    pdf = get_local_docs_path()
    assert pdf.name == "pystatsv1.pdf"
    assert pdf.exists()
    # sanity: make sure it's not empty / stub
    assert pdf.stat().st_size > 50_000