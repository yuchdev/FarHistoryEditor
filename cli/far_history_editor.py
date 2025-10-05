#!/usr/bin/env python3
"""
far_history_editor.py: Comprehensive CLI for Far2l history export/import.

Usage examples:
  # Export HST -> JSON (auto-detect header)
  far_history_editor.py export ~/.config/far2l/history/commands.hst commands.json --pretty

  # Import JSON -> HST (header inferred from JSON["Header"])
  far_history_editor.py import commands.json ~/.config/far2l/history/commands.hst

  # Work with stdin/stdout
  far_history_editor.py export ~/.config/far2l/history/folders.hst - --pretty | jq .HistoryCount
  far_history_editor.py import - out.hst < edited.json

Exit codes:
  0 success
  1 usage/argument error
  2 parse/serialization error
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from far_history_toolset.core.hst_lexer import detect_header
from far_history_toolset.core.errors import UnknownHeaderError, ParseError, SchemaError, RoundtripError
from far_history_toolset.services import get_service_for_header


def _read_text(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    p = Path(path).expanduser()
    return p.read_text(encoding="utf-8", errors="replace")


def _write_text(path: str, text: str) -> None:
    if path == "-":
        sys.stdout.write(text)
        return
    p = Path(path).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8", newline="\n")


def _read_json(path: str) -> Dict[str, Any]:
    if path == "-":
        return json.loads(sys.stdin.read())
    p = Path(path).expanduser()
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: str, data: Dict[str, Any], pretty: bool, ensure_ascii: bool) -> None:
    if path == "-":
        json.dump(data, sys.stdout, indent=2 if pretty else None, ensure_ascii=ensure_ascii)
        if pretty:
            sys.stdout.write("\n")
        return
    p = Path(path).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2 if pretty else None, ensure_ascii=ensure_ascii)
        if pretty:
            f.write("\n")


def cmd_export(args: argparse.Namespace) -> int:
    try:
        text = _read_text(args.hst_in)
        header = detect_header(text)
        if header is None and not args.header:
            raise UnknownHeaderError("Header not found; specify --header to force a parser.")
        if args.header:
            header = args.header
        assert header is not None

        svc = get_service_for_header(header)
        data = svc.export(text)

        if args.include_header:
            data["_cli"] = {"detectedHeader": header}

        _write_json(args.json_out, data, pretty=args.pretty, ensure_ascii=not args.no_ascii)
        return 0
    except (UnknownHeaderError, ParseError) as e:
        sys.stderr.write(f"[far_history_editor.py] export error: {e}\n")
        return 2
    except FileNotFoundError as e:
        sys.stderr.write(f"[far_history_editor.py] file not found: {e}\n")
        return 1
    except Exception as e:
        sys.stderr.write(f"[far_history_editor.py] unexpected error: {e}\n")
        return 2


def cmd_import(args: argparse.Namespace) -> int:
    try:
        data = _read_json(args.json_in)

        # Prefer explicit override, else JSON["Header"]
        header: Optional[str] = args.header or data.get("Header")
        if not header:
            raise UnknownHeaderError("JSON lacks 'Header' and no --header override was provided.")
        svc = get_service_for_header(header)

        hst_text = svc.import_(data)
        _write_text(args.hst_out, hst_text)
        return 0
    except (UnknownHeaderError, SchemaError, RoundtripError, ParseError) as e:
        sys.stderr.write(f"[far_history_editor.py] import error: {e}\n")
        return 2
    except FileNotFoundError as e:
        sys.stderr.write(f"[far_history_editor.py] file not found: {e}\n")
        return 1
    except json.JSONDecodeError as e:
        sys.stderr.write(f"[far_history_editor.py] invalid JSON: {e}\n")
        return 2
    except Exception as e:
        sys.stderr.write(f"[far_history_editor.py] unexpected error: {e}\n")
        return 2


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="far_history_editor.py",
        description="Far2l history export/import tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  far_history_editor.py export ~/.config/far2l/history/commands.hst commands.json --pretty\n"
            "  far_history_editor.py import commands.json ~/.config/far2l/history/commands.hst\n"
            "  far_history_editor.py export in.hst - | jq .\n"
            "  far_history_editor.py import - out.hst < edited.json\n"
        ),
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # export
    pe = sub.add_parser("export", help="Export .hst to JSON (auto-detect header)")
    pe.add_argument("hst_in", help="Input .hst file path (or '-' for stdin)")
    pe.add_argument("json_out", help="Output JSON path (or '-' for stdout)")
    pe.add_argument("--header", choices=[
        "[SavedHistory]", "[SavedDialogHistory]", "[SavedFolderHistory]", "[SavedViewHistory]"
    ], help="Force a specific parser if auto-detection is ambiguous/missing.")
    pe.add_argument("--pretty", action="store_true", help="Pretty-print JSON output with indentation.")
    pe.add_argument("--no-ascii", action="store_true", help="Do not escape non-ASCII characters in JSON.")
    pe.add_argument("--include-header", action="store_true", help="Include a small _cli block with detection info.")
    pe.set_defaults(func=cmd_export)

    # import
    pi = sub.add_parser("import", help="Import JSON to .hst (header inferred from JSON)")
    pi.add_argument("json_in", help="Input JSON path (or '-' for stdin)")
    pi.add_argument("hst_out", help="Output .hst path (or '-' for stdout)")
    pi.add_argument("--header", choices=[
        "[SavedHistory]", "[SavedDialogHistory]", "[SavedFolderHistory]", "[SavedViewHistory]"
    ], help="Override JSON['Header'] when importing.")
    pi.set_defaults(func=cmd_import)

    return p


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
