"""[SavedHistory] (commands.hst) exporter/importer."""
from __future__ import annotations

from typing import List, Dict, Any

from far_history_toolset.core import (
    extract_quoted_block,
    extract_simple_pair,
)
from far_history_toolset.services.base import HistoryFile


class CommandsHistory(HistoryFile):
    """Service for [SavedHistory] (commands.hst).

    Converts Far2l command history text to a structured dict and back.

    Constants:
    - HEADER: The .hst header tag this service handles.
    """
    HEADER = "[SavedHistory]"

    def export(self, text: str) -> dict:
        """Parse commands.hst text into a normalized dictionary.

        The resulting dict has keys: Header, Locks, Position, History (list), and
        a _meta section with historyCount and encoding styles.

        :param text: Raw contents of a commands.hst file.
        :returns: A dictionary ready for inspection or transformation.
        :raises ValueError: If required structure is malformed (handled by helpers).
        """
        extras_raw, rest = extract_quoted_block(text, "Extras")
        history_count, rest = extract_simple_pair(rest, "HistoryCount")
        lines_raw, rest = extract_quoted_block(rest, "Lines")
        times_str, rest = extract_simple_pair(rest, "Times")
        locks, rest = extract_simple_pair(rest, "Locks")
        position, rest = extract_simple_pair(rest, "Position")

        dirs_list = self._split_items(extras_raw)
        cmd_list = self._split_items(lines_raw)

        # Times
        hex_list = [t for t in (times_str or "").split() if t]
        iso_list = self._times_hex_to_iso_list(hex_list)

        # Pair by index, longest wins
        n = max(len(dirs_list), len(cmd_list))
        history: List[Dict[str, Any]] = []
        for i in range(n):
            history.append({
                "dir": dirs_list[i] if i < len(dirs_list) else "",
                "command": cmd_list[i] if i < len(cmd_list) else "",
                "timeHex": hex_list[i] if i < len(hex_list) else None,
                "timeISO": iso_list[i] if i < len(iso_list) else None,
            })

        return {
            "Header": self.HEADER,
            "Locks": locks or "",
            "Position": int(position) if position else -1,
            "History": history,
            "_meta": {
                "historyCount": int(history_count) if history_count else len(cmd_list),
                "extrasStyle": "escaped",
                "linesStyle": "escaped",
            },
        }

    def import_(self, data: dict) -> str:
        """Serialize a previously exported dict back into commands.hst text.

        Missing or unparsable times are synthesized deterministically using the
        current FILETIME when needed to keep lengths aligned.

        :param data: Structure produced by export(), possibly modified.
        :returns: Text suitable to be written as a commands.hst file.
        :raises KeyError: If expected keys are missing in the input structure.
        """
        history = data.get("History", []) or []
        locks = data.get("Locks", "") or ""
        position = int(data.get("Position", -1))

        dirs_list: List[str] = []
        cmd_list: List[str] = []
        time_pairs: List[tuple[str | None, str | None]] = []

        for rec in history:
            d = rec.get("dir") or ""
            c = rec.get("command") or ""
            hx = rec.get("timeHex")
            iso = rec.get("timeISO")
            if d != "" or len(dirs_list) < len(cmd_list):
                dirs_list.append(d)
            else:
                dirs_list.append("")
            if c != "" or len(cmd_list) < len(dirs_list):
                cmd_list.append(c)
            else:
                cmd_list.append("")
            time_pairs.append((hx, iso))

        # build times aligned to commands length
        hex_out = self._hex_list_from_records(time_pairs)
        if len(hex_out) < len(cmd_list):
            # pad synthesized
            pad = [self._hex_list_from_records([(None, None)])[-1]] * (len(cmd_list) - len(hex_out))
            hex_out.extend(pad)
        hex_out = hex_out[:len(cmd_list)]

        extras_val = self._join_items(dirs_list)
        lines_val = self._join_items(cmd_list)

        out = [
            f"{self.HEADER}\n",
            f'Extras="{extras_val}"\n',
            f"HistoryCount={len(cmd_list)}\n",
            f'Lines="{lines_val}"\n',
            f"Locks={locks}\n" if locks != "" else "Locks=\n",
            f"Position={position}\n",
            "Times=" + " ".join(hex_out) + "\n",
        ]
        return "".join(out)
