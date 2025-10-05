# test/integration/test_roundtrip_folders.py
from far_history_toolset.core.hst_lexer import detect_header
from far_history_toolset.services import get_service_for_header

HX0 = "0028c8515035dc01"
HX1 = "80be60525035dc01"
HX2 = "0055f9525035dc01"


def _mock_view_hst() -> str:
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


def test_view_roundtrip():
    original = _mock_view_hst()
    header = detect_header(original)
    assert header == "[SavedViewHistory]"
    svc = get_service_for_header(header)

    data = svc.export(original)
    rebuilt = svc.import_(data)
    assert rebuilt == original
    assert len(data["History"]) == 2
