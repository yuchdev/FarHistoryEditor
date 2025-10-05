"""Service registry: map header -> service class."""
from __future__ import annotations

from typing import Dict, Type

from far_history_toolset.services.base import HistoryFile
from far_history_toolset.services.commands import CommandsHistory
from far_history_toolset.services.dialogs import DialogsHistory
from far_history_toolset.services.folders import FoldersHistory
from far_history_toolset.services.view import ViewHistory


REGISTRY: Dict[str, Type[HistoryFile]] = {
    CommandsHistory.HEADER: CommandsHistory,
    DialogsHistory.HEADER: DialogsHistory,
    FoldersHistory.HEADER: FoldersHistory,
    ViewHistory.HEADER: ViewHistory,
}


def get_service_for_header(header: str) -> HistoryFile:
    """
    Return a concrete HistoryFile instance for a given header, or raise KeyError.
    """
    cls = REGISTRY[header]
    return cls()
