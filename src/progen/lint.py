# SPDX-License-Identifier: AGPL-3.0-or-later
"""progen output linter. owns the tell-list so agents state the is."""

from __future__ import annotations

from dataclasses import dataclass
import json
import re
from pathlib import Path
from typing import Iterable, Optional

from . import tells


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str
    line: int
    excerpt: str
    title: str


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_rules() -> list[dict]:
    path = _repo_root() / "spec" / "progen.v1.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data["lint_rules"])


def lint_text(
    source: str,
    role: str = "agent",
    ask: Optional[str] = None,
) -> list[Finding]:
    if role == "human":
        return []
    return _lint_agent(source, ask=ask)


def _lint_agent(source: str, ask: Optional[str] = None) -> list[Finding]:
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

    lines = visible.splitlines()
    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("```"):
            continue
        check = stripped
        # tables still carry dualism / mush if someone hides there
        if stripped.startswith("|"):
            check = stripped.strip("|")
        if tells.MUSH.search(check):
            add("P002", i, stripped)
        if tells.AS_AI.search(check):
            add("P003", i, stripped)
        if tells.DISCLAIMER.search(check):
            add("P007", i, stripped)
        if tells.MARKETING.search(check) or tells.ROBUST.search(check):
            add("P008", i, stripped)
        if tells.DUALISM.search(check):
            add("P004", i, stripped)
        if tells.RECAP.search(check):
            add("P006", i, stripped)
        if tells.TRIPLE.search(check):
            add("P011", i, stripped)
        if not stripped.startswith("|"):
            for m in tells.PAREN.finditer(stripped):
                inner = m.group(1)
                if _paren_allowed(inner, stripped):
                    continue
                add("P001", i, stripped)
                break

    last = _last_content_line(visible)
    if last and last[1].rstrip().endswith("?"):
        text = last[1]
        if tells.HOOK.search(text) or tells.HOOK_END.search(text):
            add("P005", last[0], text)

    _will_not(lines, add)
    _latch(visible, add)
    _stub(visible, add)
    if ask is not None:
        _scale(ask, source, add)

    return findings


def _will_not(lines: list[str], add) -> None:
    run = 0
    start = 1
    excerpt = ""
    for i, line in enumerate(lines, start=1):
        s = line.strip()
        if tells.WILL_NOT_BULLET.match(s):
            if run == 0:
                start = i
                excerpt = s
            run += 1
        else:
            if run >= 3:
                add("P012", start, excerpt)
            run = 0
    if run >= 3:
        add("P012", start, excerpt)


def _latch(visible: str, add) -> None:
    data = json.loads((_repo_root() / "spec" / "progen.v1.json").read_text(encoding="utf-8"))
    body = visible.lower()
    for family, words in data.get("latch_families", {}).items():
        n = 0
        for word in words:
            n += len(re.findall(r"\b" + re.escape(word.lower()) + r"\b", body))
        if n >= tells.LATCH_THRESHOLD:
            add("P014", 1, f"{family} analog x{n}")


def _stub(visible: str, add) -> None:
    if tells.STUB.search(visible) and tells.DONE_CLAIM.search(visible):
        add("P013", 1, "placeholder plus done")


def _scale(ask: str, source: str, add) -> None:
    aw = max(1, len(ask.split()))
    ow = len(source.split())
    if aw <= 20 and ow > max(80, aw * 8):
        add("P010", 1, f"ask {aw} words, out {ow} words")


def _paren_allowed(inner: str, line: str) -> bool:
    if inner.startswith("http"):
        return True
    if re.match(r"^[\w.+-]+@[\w.-]+$", inner):
        return True
    if re.match(r"^C\)", inner) or inner in {"C", "R", "TM"}:
        return True
    if re.match(r"^[\w.-]+\.\w{1,6}$", inner):
        return True
    if re.search(r"`[^`]*\(" + re.escape(inner[:12]), line):
        return True
    return False


def _mask_fences(source: str) -> str:
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
