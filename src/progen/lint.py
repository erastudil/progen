# SPDX-License-Identifier: AGPL-3.0-or-later
"""progen output linter. owns the tell-list so agents do not recite it."""

from __future__ import annotations

from dataclasses import dataclass
import json
import re
from pathlib import Path
from typing import Iterable, Optional


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str
    line: int
    excerpt: str
    title: str


_MUSH = re.compile(
    r"\b(i['’]d be happy to|i would be happy to|great question|absolutely!|"
    r"happy to help)\b",
    re.IGNORECASE,
)
_AS_AI = re.compile(r"\b(as an ai|i am an ai|i['’]m an ai)\b", re.IGNORECASE)
_DUALISM = re.compile(
    r"\b(it['’]s not\b.{1,60}\bit['’]s\b|this is not\b.{1,60}\bit is\b|"
    r"not a .{1,40}, a )",
    re.IGNORECASE,
)
_HOOK = re.compile(
    r"\b(what should we\b|what would you like\b|want me to\b|shall i\b|"
    r"let me know if\b|anything else i can\b|how can i (help|assist)\b|"
    r"what would you like (me )?to (do|work on)\b)",
    re.IGNORECASE,
)
_RECAP = re.compile(
    r"\b(in conclusion\b|to recap\b|to summarize\b|full circle\b|"
    r"let me recap\b|as (i|we) mentioned\b)",
    re.IGNORECASE,
)
_DISCLAIMER = re.compile(
    r"\b(not (a |legal |financial |medical )?advice\b|i am not a (lawyer|doctor|cpa)\b|"
    r"this is not (legal|financial|medical) advice\b|consult a (professional|lawyer|doctor)\b)",
    re.IGNORECASE,
)
_MARKETING = re.compile(
    r"\b(delve|leverage|tapestry|let['’]s dive in|dive in)\b",
    re.IGNORECASE,
)
_TRIPLE = re.compile(r"^\[(EN|RO|JA)\]\s", re.MULTILINE)
_ROBUST = re.compile(r"\brobust\b", re.IGNORECASE)
_PAREN = re.compile(r"\(([A-Za-z][^)]{2,120})\)")

_HOOK_END = re.compile(
    r"(what should we|what would you like|want me to|shall i|"
    r"let me know if|anything else|how can i help).{0,40}\?\s*$",
    re.IGNORECASE,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_rules() -> list[dict]:
    path = _repo_root() / "spec" / "progen.v1.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data["lint_rules"])


def lint_text(source: str, role: str = "agent") -> list[Finding]:
    if role == "human":
        return _lint_human(source)
    return _lint_agent(source)


def _lint_human(source: str) -> list[Finding]:
    # slack: asides are legal. marks are optional. almost nothing fails.
    return []


def _lint_agent(source: str) -> list[Finding]:
    findings: list[Finding] = []
    visible = _mask_fences(source)
    rules = {r["id"]: r for r in load_rules()}

    def add(rule_id: str, line: int, excerpt: str) -> None:
        meta = rules[rule_id]
        findings.append(
            Finding(
                rule=rule_id,
                severity=meta["severity"],
                line=line,
                excerpt=_clip(excerpt),
                title=meta["title"],
            )
        )

    for i, line in enumerate(visible.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("|"):
            continue
        if stripped.startswith("```"):
            continue
        if _MUSH.search(stripped):
            add("P002", i, stripped)
        if _AS_AI.search(stripped):
            add("P003", i, stripped)
        if _DISCLAIMER.search(stripped):
            add("P007", i, stripped)
        if _MARKETING.search(stripped) or _ROBUST.search(stripped):
            add("P008", i, stripped)
        if _DUALISM.search(stripped):
            add("P004", i, stripped)
        if _RECAP.search(stripped):
            add("P006", i, stripped)
        if _TRIPLE.search(stripped):
            add("P011", i, stripped)
        for m in _PAREN.finditer(stripped):
            inner = m.group(1)
            if _paren_allowed(inner, stripped):
                continue
            add("P001", i, stripped)
            break

    last = _last_content_line(visible)
    if last and last[1].rstrip().endswith("?"):
        text = last[1]
        if _HOOK.search(text) or _HOOK_END.search(text):
            add("P005", last[0], text)

    return findings


def _paren_allowed(inner: str, line: str) -> bool:
    if inner.startswith("http"):
        return True
    if re.match(r"^[\w.+-]+@[\w.-]+$", inner):
        return True
    if re.match(r"^C\)", inner) or inner in {"C", "R", "TM"}:
        return True
    if re.match(r"^[\w.-]+\.\w{1,6}$", inner):
        return True
    # markdown link already masked; function-call-ish
    if re.search(r"`[^`]*\(" + re.escape(inner[:12]), line):
        return True
    return False


def _mask_fences(source: str) -> str:
    """Replace fenced code and inline code so line numbers stay aligned."""
    lines = source.splitlines(True)
    out: list[str] = []
    fence = False
    for line in lines:
        if line.strip().startswith("```"):
            fence = not fence
            out.append("\n" if line.endswith("\n") else "")
            continue
        if fence:
            out.append("\n" if line.endswith("\n") else "")
            continue
        out.append(_mask_inline(line))
    return "".join(out)


def _mask_inline(line: str) -> str:
    def ticks(m: re.Match) -> str:
        return " " * len(m.group(0))

    line = re.sub(r"`[^`]+`", ticks, line)
    line = re.sub(r"\[[^\]]+\]\([^)]+\)", ticks, line)
    line = re.sub(r"https?://\S+", ticks, line)
    return line


def _last_content_line(source: str) -> Optional[tuple[int, str]]:
    last = None
    for i, line in enumerate(source.splitlines(), start=1):
        if line.strip():
            last = (i, line)
    return last


def _clip(s: str, n: int = 120) -> str:
    s = s.strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def format_findings(findings: Iterable[Finding], path: str = "") -> str:
    rows = list(findings)
    if not rows:
        return "clean"
    parts = []
    for f in rows:
        loc = f"{path}:{f.line}" if path else f"line {f.line}"
        parts.append(f"{f.severity}:{f.rule} {loc} {f.title}: {f.excerpt}")
    return "\n".join(parts)
