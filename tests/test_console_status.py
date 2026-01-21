from __future__ import annotations


def test_status_helpers_are_ascii() -> None:
    from pystatsv1.console import status_fail, status_ok, status_warn

    assert status_ok("hello").isascii()
    assert status_warn("hello").isascii()
    assert status_fail("hello").isascii()


def test_status_helpers_prefixes() -> None:
    from pystatsv1.console import status_fail, status_ok, status_warn

    assert status_ok("Done").startswith("[OK] ")
    assert status_warn("Heads up").startswith("[WARN] ")
    assert status_fail("Nope").startswith("NOT OK ")
