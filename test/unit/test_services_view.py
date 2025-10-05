"""Unit tests for ViewHistory service.

Covers export shape and roundtrip for view history. Expected: paths, types,
position parsed and serialization is identical to input.
"""
from far_history_toolset.services.view import ViewHistory

HX0 = "0028c8515035dc01"
HX1 = "80be60525035dc01"

def _mock_hst() -> str:
    lines = r"/file/one\n/file/two"
    times = f"{HX0} {HX1}"
    types = "11"
    return (
        "[SavedViewHistory]\n"
        "HistoryCount=2\n"
        f'Lines="{lines}"\n'
        "Locks=\n"
        "Position=-1\n"
        f"Times={times}\n"
        f"Types={types}\n"
    )

def test_export_view_shape():
    svc = ViewHistory()
    data = svc.export(_mock_hst())
    assert data["Header"] == "[SavedViewHistory]"
    assert data["Position"] == -1
    hist = data["History"]
    assert len(hist) == 2
    assert hist[0]["path"] == "/file/one"
    assert hist[0]["typeFlag"] == 1

def test_import_roundtrip():
    svc = ViewHistory()
    hst = _mock_hst()
    data = svc.export(hst)
    rebuilt = svc.import_(data)
    assert rebuilt == hst
