"""
Minimal lexing helpers for .hst files.

We intentionally keep this tiny and predictable:
- extract_quoted_block:  key="...possibly multiline with inner quotes..."<EOL>
- extract_simple_pair:   key=value
- detect_header:         returns the first known header tag if present
"""
from __future__ import annotations

import re
from typing import Tuple, Optional

# Precompiled fragments
_NEXT_KEY_RE = re.compile(r"^[A-Za-z0-9_]+=", re.MULTILINE)

# Known headers by precedence order
KNOWN_HEADERS = (
    "[SavedHistory]",
    "[SavedDialogHistory]",
    "[SavedFolderHistory]",
    "[SavedViewHistory]",
)


def extract_quoted_block(text: str, key: str) -> Tuple[str, str]:
    """
    Extract a Far2l-style quoted block: key="...<may include quotes and \\n>..."
    We scan from 'key="' until the next line that starts with SOMEKEY= or EOF.
    Then we strip exactly one closing quote at the very end (with trailing ws).
    """
    m = re.compile(rf'^{re.escape(key)}="', re.MULTILINE).search(text)
    if not m:
        return "", text

    value_start = m.end()
    m2 = _NEXT_KEY_RE.search(text, pos=value_start)
    if m2:
        block = text[value_start:m2.start()]
        remainder = text[:m.start()] + text[m2.start():]
    else:
        block = text[value_start:]
        remainder = text[:m.start()]

    # Drop exactly one terminal quote and trailing whitespace/newlines if present.
    block = re.sub(r'"\s*\Z', "", block, count=1)
    return block, remainder


def extract_simple_pair(text: str, key: str) -> Tuple[str, str]:
    """Extract a simple key=value pair (value is everything to line end)."""
    m = re.compile(rf'^{re.escape(key)}=(.*)$', re.MULTILINE).search(text)
    if not m:
        return "", text
    return m.group(1).strip(), text[:m.start()] + text[m.end():]


def detect_header(text: str) -> Optional[str]:
    """Return the first recognized header found in the text, else None."""
    for hdr in KNOWN_HEADERS:
        if re.search(rf"^\s*{re.escape(hdr)}\s*$", text, re.MULTILINE):
            return hdr
    return None
