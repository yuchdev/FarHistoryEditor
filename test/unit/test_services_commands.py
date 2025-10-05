"""Unit tests for CommandsHistory service.

Covers export structure and import roundtrip. Expected: parsed dict matches
fields and roundtrip reproduces identical text.
"""
from far2l_history.services.commands import CommandsHistory

# FILETIME hex for 2025-10-04T17:00:00..+0/1/2s
HX0 = "0028c8515035dc01"
HX1 = "80be60525035dc01"
HX2 = "0055f9525035dc01"

def _mock_hst() -> str:
    extras_val = r"/Users/atatat/.config/far2l/history\n/Users/atatat/Projects\n/home/atatat/Downloads"
    lines_val = r"pwd | pbcopy\npython3 far2l_history export\npython3 far2l_history import"
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

def test_export_structure():
    svc = CommandsHistory()
    data = svc.export(_mock_hst())
    assert data["Header"] == "[SavedHistory]"
    assert data["Locks"] == ""
    assert data["Position"] == -1
    assert len(data["History"]) == 3
    assert data["History"][0]["dir"].endswith("far2l/history")
    assert data["History"][0]["command"].startswith("pwd")
    assert data["History"][0]["timeHex"] == HX0
    assert data["_meta"]["historyCount"] == 3

def test_import_roundtrip():
    svc = CommandsHistory()
    hst = _mock_hst()
    data = svc.export(hst)
    rebuilt = svc.import_(data)
    assert rebuilt == hst
