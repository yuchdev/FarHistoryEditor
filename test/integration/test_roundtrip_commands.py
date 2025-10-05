"""Integration test: commands.hst roundtrip.

Verifies that exporting and then importing produces identical text and that
basic structural properties of the exported dict are correct.
Expected: exact byte-for-byte equality and consistent metadata.
"""
from far_history_toolset.core.hst_lexer import detect_header
from far_history_toolset.services import get_service_for_header

# FILETIME hex for 2025-10-04T17:00:00..+0/1/2s
HX0 = "0028c8515035dc01"
HX1 = "80be60525035dc01"
HX2 = "0055f9525035dc01"

def _mock_commands_hst() -> str:
    extras_val = r"/Users/atatat/.config/far2l/history\n/Users/atatat/Projects\n/home/atatat/Downloads"
    lines_val = r"pwd | pbcopy\npython3 far_history_toolset export\npython3 far_history_toolset import"
    times_line = " ".join([HX0, HX1, HX2])
    return (
        "[SavedHistory]\n"
        f'Extras="{extras_val}"\n'
        "HistoryCount=3\n"
        f'Lines="{lines_val}"\n'
        "Locks=\n"
        "Position=-1\n"
        f"Times={times_line}\n"
    )

def test_commands_roundtrip():
    original = _mock_commands_hst()
    header = detect_header(original)
    assert header == "[SavedHistory]"
    svc = get_service_for_header(header)

    data = svc.export(original)
    rebuilt = svc.import_(data)

    # Round-trip must be byte-identical
    assert rebuilt == original

    # Basic structural sanity checks on exported JSON
    assert data["Header"] == header
    assert data["_meta"]["historyCount"] == 3
    assert len(data["History"]) == 3
    assert data["History"][0]["dir"].endswith("far2l/history")
    assert data["History"][2]["timeHex"] == HX2
