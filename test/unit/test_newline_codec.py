"""Unit tests for newline encoding/decoding helpers.

Ensures that encoded literal backslash-n sequences are normalized correctly.
Expected: splitting and joining behave predictably.
"""
from far_history_toolset.core.newline_codec import smart_split_multiline, encode_literal_backslash_n

def test_smart_split_basic():
    """A simple '\\n'-encoded list should split into three items."""
    raw = r"a\nb\nc"
    assert smart_split_multiline(raw) == ["a", "b", "c"]

def test_smart_split_nested_backslashes():
    raw = r"a\\n b\\n c".replace(" ", "")
    # "\\n" -> "\n" pass1, then "\n" split
    assert smart_split_multiline(raw) == ["a", "b", "c"]

def test_encode_literal_backslash_n():
    items = ["one", "two", "three"]
    s = encode_literal_backslash_n(items)
    assert s == r"one\ntwo\nthree"
