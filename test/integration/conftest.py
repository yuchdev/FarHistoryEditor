# test/integration/conftest.py
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]  # repo root
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
