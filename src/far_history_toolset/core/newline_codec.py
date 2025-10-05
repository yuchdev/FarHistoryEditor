"""
Helpers for Far2l newline peculiarities.

Far2l often stores multi-item lists inside a single quoted value where item
boundaries are encoded as literal ``\\n`` (two characters), not real newlines.
This module normalizes those encodings and splits/joins predictably.
"""
from __future__ import annotations

from typing import List


def smart_split_multiline(value: str) -> List[str]:
    """
    Convert encoded newline variants inside a single quoted value into actual
    newlines and split to items. Handles CRLF, CR, LF. Also handles nested
    backslash encodings by first collapsing "\\\\n" -> "\\n" repeatedly, then
    converting "\\n" -> "\n".

    Example:
    - r"a\\n b\\n c" -> ["a", "b", "c"]
    - r"x\ny" -> ["x", "y"]
    """
    if not value:
        return []

    # Normalize newline forms in the raw string
    s = value.replace("\r\n", "\n").replace("\r", "\n")

    # First collapse nested backslashes so that sequences like "\\\\n"
    # become "\\n" (and deeper nestings reduce step by step).
    prev = None
    while prev != s:
        prev = s
        s = s.replace("\\\\n", "\\n")

    # Now convert literal backslash-n to actual newline
    s = s.replace("\\n", "\n")

    return [x for x in s.split("\n") if x != ""]


def encode_literal_backslash_n(lines: List[str]) -> str:
    """
    Join a list of items with real newlines, then encode newlines as literal '\\n'
    (the format most Far2l history files use inside quoted blocks).
    """
    return "\n".join(lines).replace("\n", "\\n")
