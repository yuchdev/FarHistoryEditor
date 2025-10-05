"""Integration test: detect header and dispatch to appropriate service.

Builds sample .hst texts for all supported types and verifies that detect_header
and service dispatch result in a lossless export/import roundtrip.
Expected: rebuilt text is byte-for-byte equal to the original input.
"""
from far2l_history.core.hst_lexer import detect_header
from far2l_history.services import get_service_for_header

HX0 = "0028c8515035dc01"
HX1 = "80be60525035dc01"
HX2 = "0055f9525035dc01"

def _mocks():
    # Commands
    yield (
        "[SavedHistory]\n"
        'Extras="/x\\n/y"\n'
        "HistoryCount=2\n"
        'Lines="cmd1\\ncmd2"\n'
        "Locks=\n"
        "Position=-1\n"
        f"Times={HX0} {HX1}\n"
    )
    # Folders
    yield (
        "[SavedFolderHistory]\n"
        "HistoryCount=3\n"
        'Lines="/a\\n/b\\n/c"\n'
        "Locks=000\n"
        "Position=-1\n"
        f"Times={HX0} {HX1} {HX2}\n"
        "Types=012\n"
    )
    # View
    yield (
        "[SavedViewHistory]\n"
        "HistoryCount=1\n"
        'Lines="/file/one"\n'
        "Locks=000\n"
        "Position=-1\n"
        f"Times={HX0}\n"
        "Types=1\n"
    )
    # Dialogs with one section
    yield (
        "[SavedDialogHistory]\n"
        "HistoryCount=1\n\n"
        "[SavedDialogHistory/SearchText]\n"
        'Lines="git"\n'
        "Locks=\n"
        "Position=-1\n"
        f"Times={HX0}\n\n"
    )

def test_detect_and_dispatch_all():
    for original in _mocks():
        header = detect_header(original)
        assert header is not None
        svc = get_service_for_header(header)
        data = svc.export(original)
        rebuilt = svc.import_(data)
        assert rebuilt == original
