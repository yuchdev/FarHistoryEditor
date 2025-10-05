"""[SavedDialogHistory] (dialogs.hst) exporter/importer with subsections."""
from __future__ import annotations

import re
from typing import Dict, Any, List, Tuple

from far2l_history.core import extract_quoted_block, extract_simple_pair
from far2l_history.services.base import HistoryFile


_SECTION_RE = re.compile(r"^\[SavedDialogHistory/([^\]]+)\]\s*$", re.MULTILINE)


class DialogsHistory(HistoryFile):
    HEADER = "[SavedDialogHistory]"

    def export(self, text: str) -> dict:
        """Parse dialogs.hst with multiple subsections into a structured dict.

        Each subsection [SavedDialogHistory/<Name>] becomes a category with its
        own Locks, Position, and History list aligned by index.

        :param text: Raw dialogs.hst contents.
        :returns: A dictionary with Header, HistoryCount, and Categories.
        :raises ValueError: If the structure cannot be parsed (surfaced from helpers).
        """
        # Top-level header block may contain HistoryCount (and sometimes nothing else)
        # We remove ONLY the first occurrence of the header line to avoid eating subsections.
        # Then we fish out the optional HistoryCount right after it, if present.
        top_history_count = self._read_top_history_count(text)

        categories: List[Dict[str, Any]] = []
        for name, block in self._iter_sections(text):
            lines_raw, _ = extract_quoted_block(block, "Lines")
            locks, _ = extract_simple_pair(block, "Locks")
            position, _ = extract_simple_pair(block, "Position")
            times_str, _ = extract_simple_pair(block, "Times")

            items = self._split_items(lines_raw)
            hex_list = [t for t in (times_str or "").split() if t]
            iso_list = self._times_hex_to_iso_list(hex_list)

            # One-to-one mapping: index -> line/time
            history: List[Dict[str, Any]] = []
            for i, line in enumerate(items):
                history.append({
                    "line": line,
                    "timeHex": hex_list[i] if i < len(hex_list) else None,
                    "timeISO": iso_list[i] if i < len(iso_list) else None,
                })

            categories.append({
                "name": name,
                "Locks": locks or "",
                "Position": int(position) if position else -1,
                "History": history,
            })

        return {
            "Header": self.HEADER,
            "HistoryCount": top_history_count,
            "Categories": categories,
        }

    def import_(self, data: dict) -> str:
        """Serialize the dialogs structure back into dialogs.hst format.

        :param data: Structure produced by export(), with Categories and fields.
        :returns: Text suitable for a dialogs.hst file.
        :raises KeyError: If required keys are missing.
        """
        header = data.get("Header") or self.HEADER
        if header != self.HEADER:
            # allow caller to force; but we serialize as our header anyway
            header = self.HEADER

        hist_count = int(data.get("HistoryCount", 0))
        cats = data.get("Categories", []) or []

        out: List[str] = [f"{self.HEADER}\n", f"HistoryCount={hist_count}\n\n"]

        for cat in cats:
            name = cat.get("name") or "Unnamed"
            locks = cat.get("Locks", "") or ""
            position = int(cat.get("Position", -1))
            history = cat.get("History", []) or []

            lines_list = [e.get("line") or "" for e in history]
            time_pairs = [(e.get("timeHex"), e.get("timeISO")) for e in history]
            times_hex = self._hex_list_from_records(time_pairs)

            out.append(f"[SavedDialogHistory/{name}]\n")
            out.append(f'Lines="{self._join_items(lines_list)}"\n')
            out.append(f"Locks={locks}\n" if locks != "" else "Locks=\n")
            out.append(f"Position={position}\n")
            out.append("Times=" + " ".join(times_hex) + "\n\n")

        return "".join(out)


    @staticmethod
    def _iter_sections(text: str) -> List[Tuple[str, str]]:
        """
        Yield (name, block_text) for each [SavedDialogHistory/<Name>] section.
        block_text starts at the section header and ends right before the next section/header or EOF.
        """
        matches = list(_SECTION_RE.finditer(text))
        sections: List[Tuple[str, str]] = []
        for i, m in enumerate(matches):
            name = m.group(1)
            start = m.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            sections.append((name, text[start:end]))
        return sections

    @staticmethod
    def _read_top_history_count(text: str) -> int:
        """
        Read the HistoryCount from the top-level [SavedDialogHistory] header if present.
        """
        # Find the header line first
        hdr = re.search(r"^\s*\[SavedDialogHistory]\s*$", text, re.MULTILINE)
        if not hdr:
            return 0
        # Search for a HistoryCount=... following it (before the first subsection header)
        next_sub = _SECTION_RE.search(text, hdr.end())
        scope_end = next_sub.start() if next_sub else len(text)
        m = re.search(r"^HistoryCount=(\d+)\s*$", text[hdr.end():scope_end], re.MULTILINE)
        return int(m.group(1)) if m else 0
