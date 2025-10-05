"""
Core utilities for parsing and serializing Far2l history files.

This package exposes:
- FILETIME helpers (filetime.py)
- Newline encoding/decoding helpers (newline_codec.py)
- Lightweight .hst lexing helpers (hst_lexer.py)
- Typed JSON models for service interfaces (models.py)
- Error types (errors.py)
"""
from far2l_history.core.errors import ParseError, SchemaError, RoundtripError, UnknownHeaderError
from far2l_history.core.filetime import (
    FILETIME_EPOCH,
    filetime_hex_to_int_le,
    filetime_int_to_hex_le,
    filetime_int_to_iso,
    iso_to_filetime_int,
    now_filetime_int,
)
from far2l_history.core.newline_codec import smart_split_multiline, encode_literal_backslash_n
from far2l_history.core.hst_lexer import extract_quoted_block, extract_simple_pair, detect_header
from far2l_history.core import models

__all__ = [
    # errors
    "ParseError", "SchemaError", "RoundtripError", "UnknownHeaderError",
    # filetime
    "FILETIME_EPOCH",
    "filetime_hex_to_int_le", "filetime_int_to_hex_le",
    "filetime_int_to_iso", "iso_to_filetime_int", "now_filetime_int",
    # newline codec
    "smart_split_multiline", "encode_literal_backslash_n",
    # lexer
    "extract_quoted_block", "extract_simple_pair", "detect_header",
    # models
    "models",
]
