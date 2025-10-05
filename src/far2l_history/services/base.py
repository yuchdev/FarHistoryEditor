"""Abstract base service and small shared helpers."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Tuple

from far2l_history.core import (
    filetime_hex_to_int_le,
    filetime_int_to_hex_le,
    filetime_int_to_iso,
    iso_to_filetime_int,
    now_filetime_int,
    smart_split_multiline,
    encode_literal_backslash_n,
)


class HistoryFile(ABC):
    """Abstract service for a Far2l history file type."""
    HEADER: str  # e.g., "[SavedHistory]"

    @abstractmethod
    def export(self, text: str) -> dict:
        """Parse .hst text into a JSON-like dict (service-specific schema).

        :param text: Raw contents of a .hst history file.
        :returns: A structured dictionary representing the parsed history.
        :raises Exception: Implementations may raise on malformed input.
        """

    @abstractmethod
    def import_(self, data: dict) -> str:
        """Build .hst text from a dict previously produced by export().

        :param data: Parsed data to serialize back into .hst text.
        :returns: A string ready to be saved as a .hst file.
        :raises Exception: Implementations may raise on invalid schema.
        """


    @staticmethod
    def _split_items(block_value: str) -> List[str]:
        """Split a Far2l-encoded block (literal '\\n' etc.) to items."""
        return smart_split_multiline(block_value)

    @staticmethod
    def _join_items(items: List[str]) -> str:
        """Encode items as a single Far2l value with literal '\\n' separators."""
        return encode_literal_backslash_n(items)

    @staticmethod
    def _times_hex_to_iso_list(hex_tokens: List[str]) -> List[str | None]:
        """Convert each hex token to ISO; invalid tokens become None."""
        out: List[str | None] = []
        for hx in hex_tokens:
            if not hx:
                out.append(None)
                continue
            try:
                out.append(filetime_int_to_iso(filetime_hex_to_int_le(hx)))
            except Exception:
                out.append(None)
        return out

    @staticmethod
    def _times_from_records(time_hex: str | None, time_iso: str | None) -> int:
        """
        Prefer original hex to preserve exact byte roundtrip; fall back to ISO.
        If neither parseable, synthesize current FILETIME.
        """
        if time_hex:
            try:
                return filetime_hex_to_int_le(time_hex)
            except Exception:
                pass
        if time_iso:
            try:
                return iso_to_filetime_int(time_iso)
            except Exception:
                pass
        return now_filetime_int()

    @staticmethod
    def _hex_list_from_records(records: List[tuple[str | None, str | None]]) -> List[str]:
        """Build Times hex list from (timeHex, timeISO) tuples."""
        ints = [HistoryFile._times_from_records(hx, iso) for (hx, iso) in records]
        return [filetime_int_to_hex_le(v) for v in ints]

    @staticmethod
    def _align(a_len: int, b: List) -> List:
        """
        Trim or pad list b to length a_len.
        Padding uses synthesized FILETIME for Times; empty strings for Lines.
        Caller decides what padding value should be before calling.
        """
        if len(b) > a_len:
            return b[:a_len]
        if len(b) < a_len:
            # Caller should pass a list already padded when needed; keep as is.
            return b + [None] * (a_len - len(b))
        return b


class LinesTypesTimesHistory(HistoryFile):
    """
    Intermediary base for histories that use Lines/Types/Times with the same layout.
    Implements shared export/import logic used by FoldersHistory and ViewHistory.
    """

    def export(self, text: str) -> dict:
        """Parse a history with Lines/Types/Times into a normalized dict.

        :param text: Raw contents of folders.hst or view.hst.
        :returns: Dict with Header, Locks, Position, History, and _meta.
        :raises ValueError: If input is malformed (errors propagate from helpers).
        """
        # Local imports to avoid circular dependency at module import order.
        from far2l_history.core import extract_quoted_block, extract_simple_pair
        from typing import List, Dict, Any

        lines_raw, rest = extract_quoted_block(text, "Lines")
        locks, rest = extract_simple_pair(rest, "Locks")
        history_count, _ = extract_simple_pair(rest, "HistoryCount")
        position, rest = extract_simple_pair(rest, "Position")
        times_str, rest = extract_simple_pair(rest, "Times")
        types_str, rest = extract_simple_pair(rest, "Types")

        paths = self._split_items(lines_raw)
        hex_list = [t for t in (times_str or "").split() if t]
        iso_list = self._times_hex_to_iso_list(hex_list)

        types = (types_str or "")
        # Map each type char -> int where possible
        type_flags: List[int | None] = []
        for i in range(len(paths)):
            if i < len(types):
                ch = types[i]
                try:
                    type_flags.append(int(ch))
                except Exception:
                    type_flags.append(None)
            else:
                type_flags.append(None)

        history: List[Dict[str, Any]] = []
        for i, p in enumerate(paths):
            history.append({
                "path": p,
                "typeFlag": type_flags[i],
                "timeHex": hex_list[i] if i < len(hex_list) else None,
                "timeISO": iso_list[i] if i < len(iso_list) else None,
            })

        return {
            "Header": self.HEADER,
            "Locks": locks or "",
            "Position": int(position) if position else -1,
            "History": history,
            "_meta": {
                "historyCount": int(history_count) if history_count else len(paths),
                "typesRawLength": len(types),
            },
        }

    def import_(self, data: dict) -> str:
        """Serialize Lines/Types/Times style history back into text.

        :param data: Structure produced by export().
        :returns: Text suitable for folders.hst or view.hst.
        :raises KeyError: If required keys are missing.
        """
        locks = data.get("Locks", "") or ""
        position = int(data.get("Position", -1))
        history = data.get("History", []) or []

        paths = [r.get("path") or "" for r in history]
        time_pairs = [(r.get("timeHex"), r.get("timeISO")) for r in history]
        times_hex = self._hex_list_from_records(time_pairs)

        types_chars = []
        for r in history:
            tf = r.get("typeFlag")
            types_chars.append("0" if tf is None else str(int(tf)))
        types_str = "".join(types_chars)

        out = [
            f"{self.HEADER}\n",
            f"HistoryCount={len(paths)}\n",
            f'Lines="{self._join_items(paths)}"\n',
            f"Locks={locks}\n" if locks != "" else "Locks=\n",
            f"Position={position}\n",
            "Times=" + " ".join(times_hex) + "\n",
            f"Types={types_str}\n",
        ]
        return "".join(out)
