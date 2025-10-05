"""Unit tests for lightweight .hst lexer helpers.

Covers quoted block extraction, simple pairs, and header detection.
Expected: functions correctly parse and remove keys while returning remainders.
"""
from far_history_toolset.core.hst_lexer import extract_quoted_block, extract_simple_pair, detect_header

def test_extract_quoted_block_with_trailing_quote_and_newline():
    """It should extract Extras quoted value and remove it from the remainder."""
    text = (
        '[SavedHistory]\n'
        'Extras="/a/b\\n/c/d"\n'
        'HistoryCount=2\n'
        'Lines="cmd1\\ncmd2"\n'
    )
    val, rest = extract_quoted_block(text, "Extras")
    assert val == r"/a/b\n/c/d"
    assert 'Extras=' not in rest

def test_extract_simple_pair():
    text = "Locks=0000\nPosition=-1\n"
    val, rest = extract_simple_pair(text, "Locks")
    assert val == "0000"
    assert "Locks=" not in rest
    val2, rest2 = extract_simple_pair(rest, "Position")
    assert val2 == "-1"
    assert "Position=" not in rest2

def test_detect_header_variants():
    assert detect_header("[SavedHistory]\n") == "[SavedHistory]"
    assert detect_header("  [SavedDialogHistory]\n") == "[SavedDialogHistory]"
    assert detect_header("x") is None
