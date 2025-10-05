"""
FILETIME helpers: convert between Far/Windows FILETIME (<-> hex LE) and ISO-8601.

- FILETIME is the number of 100-nanosecond intervals since 1601-01-01 UTC.
- Far2l stores FILETIME values as 8-byte little-endian hex tokens.
"""
from __future__ import annotations

import datetime
from typing import Final

try:
    UTC: datetime.tzinfo = datetime.UTC  # Python 3.11+
except AttributeError:  # pragma: no cover - older Pythons
    UTC = datetime.timezone.utc

FILETIME_EPOCH: Final[int] = 116444736000000000  # 1601-01-01 .. 1970-01-01 in 100ns ticks
_TICKS_PER_SEC: Final[int] = 10_000_000


def filetime_hex_to_int_le(h: str) -> int:
    """
    Convert an 8-byte little-endian hex string to a FILETIME integer.
    Accepts shorter strings; left-pads to 16 hex digits.
    """
    s = h.strip().zfill(16)[-16:]
    return int.from_bytes(bytes.fromhex(s), "little", signed=False)


def filetime_int_to_hex_le(v: int) -> str:
    """Convert a FILETIME integer to an 8-byte little-endian hex string (lowercase)."""
    return int(v).to_bytes(8, "little", signed=False).hex()


def filetime_int_to_iso(v: int) -> str:
    """Convert a FILETIME integer to an ISO-8601 UTC timestamp string."""
    secs = (int(v) - FILETIME_EPOCH) / _TICKS_PER_SEC
    return datetime.datetime.fromtimestamp(secs, UTC).isoformat()


def iso_to_filetime_int(iso: str) -> int:
    """Convert an ISO-8601 timestamp string to a FILETIME integer."""
    dt = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return int(dt.timestamp() * _TICKS_PER_SEC) + FILETIME_EPOCH


def now_filetime_int() -> int:
    """Current time as FILETIME integer."""
    return int(datetime.datetime.now(UTC).timestamp() * _TICKS_PER_SEC) + FILETIME_EPOCH
