# FarHistoryEditor

Tools and libraries to **export**, **edit**, and **import** Far2l File Manager history files.

Far2l File Manager stores various kinds of history (commands, dialogs, folders, viewer) in `.hst` files using a compact custom format. This project lets you:

- Parse `.hst` files into **clean, editable JSON**
- Make arbitrary edits (e.g., remove sensitive entries)
- Serialize back to the exact Far2l `.hst` format (**round-trip safe**)
- Use a small, friendly **CLI**, or call the **Python API** directly

No external dependencies—pure Python standard library.

---

## Supported files / headers

| File                | Header                   | What it stores                              |
|---------------------|--------------------------|---------------------------------------------|
| `commands.hst`      | `[SavedHistory]`         | Directories + command lines + timestamps    |
| `dialogs.hst`       | `[SavedDialogHistory]`   | Dialog inputs grouped by category           |
| `folders.hst`       | `[SavedFolderHistory]`   | Folder navigation history (+ type flags)    |
| `view.hst`          | `[SavedViewHistory]`     | Viewer file history (+ type flags)          |

The tool **auto-detects** the header and routes to the right parser.

---

## Project goals

- **Safe redaction:** export to JSON, delete anything you don’t want to keep, import back.
- **Faithful round-trip:** formatting and alignment (Times/Types) preserved.
- **Extensible architecture:** easy to add new history formats later.
- **Fast and deterministic:** linear-time parsing with tiny and predictable regexes.

---

## Installation

### From source (recommended while developing)

```bash
# clone your repo
git clone <your-repo-url> FarHistoryEditor
cd FarHistoryEditor

# (optional) create venv
python3 -m venv .venv && source .venv/bin/activate

# install package (editable)
pip install -e .
```

This exposes the CLI `farhistory` (see usage below). You can also run the module in-place:

```bash
python -m far2l_history.cli.main --help
```

---

## Repository layout

```
FarHistoryEditor/
├─ cli/
│  └─ main.py                     # CLI front-end (argparse)
├─ src/
│  └─ far2l_history/
│     ├─ core/                    # shared, low-level utilities
│     │  ├─ __init__.py
│     │  ├─ errors.py             # ParseError, SchemaError, RoundtripError...
│     │  ├─ filetime.py           # FILETIME <-> hex LE <-> ISO helpers
│     │  ├─ hst_lexer.py          # tiny lexer: quoted blocks & key=val pairs
│     │  ├─ models.py             # typed JSON shapes (dataclasses)
│     │  └─ newline_codec.py      # decode/encode literal '\n' lists
│     └─ services/                # per-header services
│        ├─ __init__.py
│        ├─ base.py               # abstract HistoryFile API + helpers
│        ├─ commands.py           # [SavedHistory]  (commands.hst)
│        ├─ dialogs.py            # [SavedDialogHistory] (dialogs.hst)
│        ├─ folders.py            # [SavedFolderHistory] (folders.hst)
│        ├─ view.py               # [SavedViewHistory] (view.hst)
│        └─ registry.py           # header -> service map
├─ test/
│  ├─ unit/                       # isolated unit tests per module
│  └─ integration/                # end-to-end roundtrip tests
├─ pyproject.toml / setup.cfg / setup.py
└─ README.md
```

---

## Architecture overview

### Core (pure functions)
- **`filetime.py`** – Convert between FILETIME (int), little-endian hex tokens, and ISO-8601 strings.
- **`newline_codec.py`** – Normalize/expand Far2l’s literal `\n` encoding and split/join lists.
- **`hst_lexer.py`** – Minimal helpers to extract `key="...quoted..."` blocks and `key=value` pairs; header detector.
- **`models.py`** – Dataclasses documenting JSON schemas.
- **`errors.py`** – Small, descriptive exceptions.

### Services (each header = one class)
All services subclass **`HistoryFile`** and implement:
- `export(text: str) -> dict` (HST → JSON)
- `import_(data: dict) -> str` (JSON → HST)

Services:
- `CommandsHistory` for `[SavedHistory]`
- `DialogsHistory` for `[SavedDialogHistory]` (multi-section)
- `FoldersHistory` for `[SavedFolderHistory]` (with `Types`)
- `ViewHistory` for `[SavedViewHistory]` (with `Types`)

A registry (`services/registry.py`) maps header → service.

---

## JSON shapes (at a glance)

### `commands.hst` → `[SavedHistory]`

```json
{
  "Header": "[SavedHistory]",
  "Locks": "",
  "Position": -1,
  "History": [
    { "dir": "/path/one", "command": "pwd", "timeHex": "0028...", "timeISO": "2025-10-04T17:00:00+00:00" },
    { "dir": "/path/two", "command": "git status", "timeHex": "80be...", "timeISO": "2025-10-04T17:00:01+00:00" }
  ],
  "_meta": {
    "historyCount": 512,
    "extrasStyle": "escaped",
    "linesStyle": "escaped"
  }
}
```

### `dialogs.hst` → `[SavedDialogHistory]`

```json
{
  "Header": "[SavedDialogHistory]",
  "HistoryCount": 512,
  "Categories": [
    {
      "name": "NewFolder",
      "Locks": "000...",
      "Position": -1,
      "History": [
        { "line": "Audiobooks", "timeHex": "0028...", "timeISO": "..." },
        { "line": "assets",     "timeHex": "80be...", "timeISO": "..." }
      ]
    },
    {
      "name": "Copy",
      "Locks": "",
      "Position": -1,
      "History": [
        { "line": "/Users/...", "timeHex": "0055...", "timeISO": "..." }
      ]
    }
  ]
}
```

### `folders.hst` / `view.hst`

```json
{
  "Header": "[SavedFolderHistory]",
  "Locks": "000",
  "Position": -1,
  "History": [
    { "path": "/a", "typeFlag": 1, "timeHex": "0028...", "timeISO": "..." },
    { "path": "/b", "typeFlag": 0, "timeHex": "80be...", "timeISO": "..." }
  ],
  "_meta": { "historyCount": 512, "typesRawLength": 512 }
}
```

> The `typeFlag` is a single digit from the `Types=` string aligned with each line.

---

## CLI usage

After installation (`pip install -e .`), a console script named `farhistory` is available.

### Help

```bash
farhistory --help
```

Typical output:

```
usage: farhistory [-h] {export,import} ...

Far2l history export/import tool

positional arguments:
  {export,import}
    export            Export .hst to JSON (auto-detect header)
    import            Import JSON to .hst (header inferred from JSON)

optional arguments:
  -h, --help         show this help message and exit
```

### Export: `.hst` → JSON

```bash
# Commands history
farhistory export ~/.config/far2l/history/commands.hst commands.json

# Dialogs history (multi-section)
farhistory export ~/.config/far2l/history/dialogs.hst dialogs.json

# Folders & View
farhistory export ~/.config/far2l/history/folders.hst folders.json
farhistory export ~/.config/far2l/history/view.hst view.json
```

The tool **detects** the header and writes a JSON file using the schema above.

### Edit the JSON
Open the JSON, **remove entries** you don’t want to keep (or tweak fields).  
Examples:
- Delete elements from `History` arrays
- For dialogs: delete entire `Categories` or single entries
- Change `timeISO` to normalize timestamps (optional)

> Tip: you can drop `timeHex` and keep `timeISO`; the importer will regenerate correct FILETIME hex. If both are missing, it synthesizes current times for the missing items.

### Import: JSON → `.hst`

```bash
# Overwrite original (make a backup!)
farhistory import commands.json ~/.config/far2l/history/commands.hst

# Write to a copy first:
farhistory import commands.json commands_edited.hst
```

The importer rebuilds the `.hst` and:
- Encodes list items inside quoted fields using **literal `\n`** (Far2l style)
- Reconstructs `Times=` from `timeISO`/`timeHex`
- Reconstructs `Types=` (folders/view) from `typeFlag` values

---

## Python API usage

```python
from pathlib import Path
from far2l_history.core.hst_lexer import detect_header
from far2l_history.services import get_service_for_header

hst_text = Path("~/.config/far2l/history/commands.hst").expanduser().read_text(encoding="utf-8")
header = detect_header(hst_text)
svc = get_service_for_header(header)

data = svc.export(hst_text)    # dict -> edit as you like
data["History"] = data["History"][:100]  # example: keep only first 100 entries

rebuilt = svc.import_(data)
Path("commands_trimmed.hst").write_text(rebuilt, encoding="utf-8")
```

---

## Round-trip guarantees

- **Byte-for-byte** round-trip in our tests for well-formed inputs.
- We preserve ordering and field alignment (e.g., `Times`/`Types` aligned to lines).
- If `timeISO` and `timeHex` are inconsistent, **ISO wins**; hex is regenerated.

See `test/integration/` for end-to-end tests, and `test/unit/` for isolated tests of each module.

Run the whole suite:

```bash
pytest -q
```

---

## Notes & edge cases

- Far2l typically stores lists in a single quoted value with **literal** `\n` sequences. We decode these recursively (handles `\\n`, `\\\n`, etc.), split, and on import encode back to literal `\n`.
- Some files place `HistoryCount=` at top-level (e.g., dialogs/folders/view). We preserve it, but effective counts are derived from the arrays you provide on import.
- Unknown headers raise `UnknownHeaderError`. If Far2l adds new history types, implement a new service and register it.

---

## Roadmap

- Optional **filters** in CLI (e.g., keep last N days, drop paths matching glob).
- Pretty-print / compact JSON flags (`--pretty / --minify`).
- Optional CSV export for simple lists.

---

## License

MIT — do what you like, attribution appreciated.
