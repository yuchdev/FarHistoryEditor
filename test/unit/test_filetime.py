"""Unit tests for FILETIME conversion helpers.

Verifies hex roundtrip, ISO conversions, and monotonicity of now_filetime_int.
Expected: conversions retain value and timestamps are reasonable.
"""
import datetime

from far2l_history.core.filetime import (
    FILETIME_EPOCH,
    filetime_hex_to_int_le,
    filetime_int_to_hex_le,
    filetime_int_to_iso,
    iso_to_filetime_int,
    now_filetime_int,
)

def test_hex_roundtrip():
    val = 1234567890123456
    hx = filetime_int_to_hex_le(val)
    assert len(hx) == 16
    assert filetime_hex_to_int_le(hx) == val

def test_iso_roundtrip():
    iso = "2025-10-04T17:00:00+00:00"
    ft = iso_to_filetime_int(iso)
    back_iso = filetime_int_to_iso(ft)
    # datetime.isoformat keeps full precision, compare by parsing back
    assert back_iso.startswith("2025-10-04T17:00:00")

def test_now_filetime_increases():
    a = now_filetime_int()
    b = now_filetime_int()
    assert b >= a
    # sanity: FILETIME > epoch baseline
    assert a > FILETIME_EPOCH
