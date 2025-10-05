from far_history_toolset.services.folders import FoldersHistory

HX0 = "0028c8515035dc01"
HX1 = "80be60525035dc01"
HX2 = "0055f9525035dc01"

def _mock_hst() -> str:
    lines = r"/a\n/b\n/c"
    times = f"{HX0} {HX1} {HX2}"
    types = "101"
    return (
        "[SavedFolderHistory]\n"
        "HistoryCount=3\n"
        f'Lines="{lines}"\n'
        "Locks=000\n"
        "Position=-1\n"
        f"Times={times}\n"
        f"Types={types}\n"
    )

def test_export_and_types():
    svc = FoldersHistory()
    data = svc.export(_mock_hst())
    assert data["Header"] == "[SavedFolderHistory]"
    assert data["Locks"] == "000"
    hist = data["History"]
    assert len(hist) == 3
    assert hist[0]["path"] == "/a"
    assert hist[0]["typeFlag"] == 1
    assert hist[1]["typeFlag"] == 0

def test_import_roundtrip():
    svc = FoldersHistory()
    hst = _mock_hst()
    data = svc.export(hst)
    rebuilt = svc.import_(data)
    assert rebuilt == hst
