"""Unit tests for DialogsHistory service.

Covers multi-section parsing and roundtrip. Expected: categories and their
entries are preserved exactly through export/import.
"""
from far_history_toolset.services.dialogs import DialogsHistory

# Two small subsections, each with 2 entries
HX_A0 = "0028c8515035dc01"
HX_A1 = "80be60525035dc01"
HX_B0 = "0055f9525035dc01"
HX_B1 = "00ec924e5035dc01"

def _mock_hst() -> str:
    top = "[SavedDialogHistory]\nHistoryCount=4\n\n"
    sec_a = (
        "[SavedDialogHistory/NewFolder]\n"
        'Lines="Audiobooks\nassets"\n'.replace("\n", r"\n").replace("\\n", r"\n")  # ensure literal \n in the string
    )
    # The line above encoded too much; let's craft literal \n cleanly:
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

def test_export_categories_shape():
    svc = DialogsHistory()
    data = svc.export(_mock_hst())
    assert data["Header"] == "[SavedDialogHistory]"
    assert data["HistoryCount"] == 4
    cats = data["Categories"]
    assert {c["name"] for c in cats} == {"NewFolder", "Copy"}
    a = [c for c in cats if c["name"] == "NewFolder"][0]
    assert len(a["History"]) == 2
    assert a["History"][0]["line"] == "Audiobooks"
    assert a["History"][0]["timeHex"] == HX_A0

def test_import_roundtrip():
    svc = DialogsHistory()
    hst = _mock_hst()
    data = svc.export(hst)
    rebuilt = svc.import_(data)
    assert rebuilt == hst
