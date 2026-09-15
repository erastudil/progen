# SPDX-License-Identifier: AGPL-3.0-or-later
"""emit drop-in prompts from this tree."""

from __future__ import annotations

from pathlib import Path

_NAMES = {
    "genome": "prompts/genome.md",
    "canon": "prompts/canon.md",
    "warehouse": "prompts/warehouse.md",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_prompt(name: str) -> str:
    key = name.strip().lower()
    if key not in _NAMES:
        known = ", ".join(sorted(_NAMES))
        raise ValueError(f"unknown prompt {name!r}. known: {known}")
    path = repo_root() / _NAMES[key]
    return path.read_text(encoding="utf-8")
