"""
Service layer: concrete exporters/importers for each Far2l history file type.

Public classes:
- CommandsHistory       -> [SavedHistory]          (commands.hst)
- DialogsHistory        -> [SavedDialogHistory]    (dialogs.hst)
- FoldersHistory        -> [SavedFolderHistory]    (folders.hst)
- ViewHistory           -> [SavedViewHistory]      (view.hst)

Routing:
- REGISTRY (dict) maps header -> service class
- get_service_for_header(header: str) -> HistoryFile
"""
from far_history_toolset.services.base import HistoryFile
from far_history_toolset.services.commands import CommandsHistory
from far_history_toolset.services.dialogs import DialogsHistory
from far_history_toolset.services.folders import FoldersHistory
from far_history_toolset.services.view import ViewHistory
from far_history_toolset.services.registry import REGISTRY, get_service_for_header

__all__ = [
    "HistoryFile",
    "CommandsHistory",
    "DialogsHistory",
    "FoldersHistory",
    "ViewHistory",
    "REGISTRY",
    "get_service_for_header",
]
