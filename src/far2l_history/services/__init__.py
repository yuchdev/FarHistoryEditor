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
from far2l_history.services.base import HistoryFile
from far2l_history.services.commands import CommandsHistory
from far2l_history.services.dialogs import DialogsHistory
from far2l_history.services.folders import FoldersHistory
from far2l_history.services.view import ViewHistory
from far2l_history.services.registry import REGISTRY, get_service_for_header

__all__ = [
    "HistoryFile",
    "CommandsHistory",
    "DialogsHistory",
    "FoldersHistory",
    "ViewHistory",
    "REGISTRY",
    "get_service_for_header",
]
