"""Unit tests for service registry mapping and dispatch.

Ensures that the REGISTRY contains all known headers and that get_service_for_header
returns instances of the correct concrete service classes.
"""
from far_history_toolset.services import REGISTRY, get_service_for_header
from far_history_toolset.services.commands import CommandsHistory
from far_history_toolset.services.dialogs import DialogsHistory
from far_history_toolset.services.folders import FoldersHistory
from far_history_toolset.services.view import ViewHistory

def test_registry_contains_all():
    """Registry should include all supported service headers."""
    assert CommandsHistory.HEADER in REGISTRY
    assert DialogsHistory.HEADER in REGISTRY
    assert FoldersHistory.HEADER in REGISTRY
    assert ViewHistory.HEADER in REGISTRY

def test_get_service_for_header_instances():
    assert isinstance(get_service_for_header(CommandsHistory.HEADER), CommandsHistory)
    assert isinstance(get_service_for_header(DialogsHistory.HEADER), DialogsHistory)
    assert isinstance(get_service_for_header(FoldersHistory.HEADER), FoldersHistory)
    assert isinstance(get_service_for_header(ViewHistory.HEADER), ViewHistory)
