# test/integration/test_roundtrip_dialogs.py
from far_history_toolset.core.hst_lexer import detect_header
from far_history_toolset.services import get_service_for_header

# Two categories x two entries
HX_A0 = "0028c8515035dc01"
HX_A1 = "80be60525035dc01"
HX_B0 = "0055f9525035dc01"
HX_B1 = "00ec924e5035dc01"

def _mock_dialogs_hst() -> str:
    top = "[SavedDialogHistory]\nHistoryCount=4\n\n"
    sec_a = (
        "[SavedDialogHistory/NewFolder]\n"
        'Lines="Audiobooks\\nassets"\n'
        "Locks=000\n"
        "Position=-1\n"
        f"Times={HX_A0} {HX_A1}\n\n"
    )
    sec_b = (
        "[SavedDialogHistory/Copy]\n"
        'Lines="/path/A\\n/path/B"\n'
        "Locks=\n"
        "Position=-1\n"
        f"Times={HX_B0} {HX_B1}\n\n"
    )
    return top + sec_a + sec_b

def test_dialogs_roundtrip():
    original = _mock_dialogs_hst()
    header = detect_header(original)
    assert header == "[SavedDialogHistory]"
    svc = get_service_for_header(header)

    data = svc.export(original)
    rebuilt = svc.import_(data)

    assert rebuilt == original

    # Sanity checks
    assert data["Header"] == header
    assert data["HistoryCount"] == 4
    cats = {c["name"] for c in data["Categories"]}
    assert cats == {"NewFolder", "Copy"}
    a = [c for c in data["Categories"] if c["name"] == "NewFolder"][0]
    assert [e["line"] for e in a["History"]] == ["Audiobooks", "assets"]
    assert a["History"][0]["timeHex"] == HX_A0
