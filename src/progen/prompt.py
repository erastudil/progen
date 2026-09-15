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
    rel = _NAMES[key]
    # 1. repo root
    repo_path = repo_root() / rel
    if repo_path.is_file():
        return repo_path.read_text(encoding="utf-8")
    # 2. package data
    pkg_path = Path(__file__).resolve().parent / "data" / rel
    if pkg_path.is_file():
        return pkg_path.read_text(encoding="utf-8")
    raise FileNotFoundError(f"prompt file not found for {name!r}")
