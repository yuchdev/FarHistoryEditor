"""[SavedFolderHistory] (folders.hst) exporter/importer."""
from __future__ import annotations

from far2l_history.services.base import LinesTypesTimesHistory


class FoldersHistory(LinesTypesTimesHistory):
    """Service for [SavedFolderHistory] (folders.hst) using Lines/Types/Times."""
    HEADER = "[SavedFolderHistory]"

    def import_(self, data: dict) -> str:
        """Serialize a dict for folders history back into folders.hst text.

        :param data: Structure produced by export().
        :returns: Text for folders.hst.
        """
        return super().import_(data)
