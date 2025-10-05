"""
Typed JSON-facing models used by services.

Services are free to construct dicts directly; these dataclasses/TypedDicts
document the expected shapes and help with static checking in larger codebases.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ----------------------------- Commands (SavedHistory) -----------------------------

@dataclass
class CommandRecord:
    dir: str
    command: str
    timeHex: Optional[str] = None
    timeISO: Optional[str] = None


@dataclass
class CommandsJson:
    Header: str                    # "[SavedHistory]"
    Locks: str
    Position: int
    History: List[CommandRecord]
    _meta: Dict[str, Any] = field(default_factory=dict)


# --------------------------- Dialogs (SavedDialogHistory) --------------------------

@dataclass
class DialogEntry:
    line: str
    timeHex: Optional[str] = None
    timeISO: Optional[str] = None


@dataclass
class DialogCategory:
    name: str                      # e.g., "NewFolder", "Copy", ...
    Locks: str
    Position: int
    History: List[DialogEntry]


@dataclass
class DialogsJson:
    Header: str                    # "[SavedDialogHistory]"
    HistoryCount: int
    Categories: List[DialogCategory]


# ---------------------------- Folders (SavedFolderHistory) -------------------------

@dataclass
class FolderRecord:
    path: str
    typeFlag: Optional[int] = None  # usually '0'/'1' mapped to int
    timeHex: Optional[str] = None
    timeISO: Optional[str] = None


@dataclass
class FoldersJson:
    Header: str                    # "[SavedFolderHistory]"
    Locks: str
    Position: int
    History: List[FolderRecord]
    _meta: Dict[str, Any] = field(default_factory=dict)


# ------------------------------ View (SavedViewHistory) ---------------------------

@dataclass
class ViewRecord:
    path: str
    typeFlag: Optional[int] = None
    timeHex: Optional[str] = None
    timeISO: Optional[str] = None


@dataclass
class ViewJson:
    Header: str                    # "[SavedViewHistory]"
    Locks: str
    Position: int
    History: List[ViewRecord]
    _meta: Dict[str, Any] = field(default_factory=dict)
