"""Top-level conftest. Ensures the project root is on sys.path so that
`from tests.methodology.alignment_score import ...` resolves regardless of where
pytest is invoked from.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
