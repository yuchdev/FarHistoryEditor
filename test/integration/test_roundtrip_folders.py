# test/integration/test_roundtrip_folders.py
from far2l_history.core.hst_lexer import detect_header
from far2l_history.services import get_service_for_header

HX0 = "0028c8515035dc01"
HX1 = "80be60525035dc01"
HX2 = "0055f9525035dc01"

def _mock_folders_hst() -> str:
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

def test_folders_roundtrip():
    original = _mock_folders_hst()
    header = detect_header(original)
    assert header == "[SavedFolderHistory]"
    svc = get_service_for_header(header)

    data = svc.export(original)
    rebuilt = svc.import_(data)

    assert rebuilt == original
    # Types alignment sanity
    assert "".join("0" if r["typeFlag"] is None else str(int(r["typeFlag"]))
                   for r in data["History"]) == "101"
