"""[SavedViewHistory] (view.hst) exporter/importer."""
from __future__ import annotations

from far2l_history.services.base import LinesTypesTimesHistory


class ViewHistory(LinesTypesTimesHistory):
    """Service for [SavedViewHistory] (view.hst) using Lines/Types/Times."""
    HEADER = "[SavedViewHistory]"

    def import_(self, data: dict) -> str:
        """Serialize a dict for view history back into view.hst text.

        :param data: Structure produced by export().
        :returns: Text for view.hst.
        """
        return super().import_(data)
