# SPDX-License-Identifier: AGPL-3.0-or-later
"""mechanical pass toward iron. marks what it can. does not compile english."""

from __future__ import annotations

import re

from . import tells

_SENT_SPLIT = re.compile(r"(?<=[!?])\s+|(?<=\.)\s+(?=[A-Z\[])")


def iron_text(source: str) -> str:
    out: list[str] = []
    for raw in source.splitlines():
        if not raw.strip():
            if out and out[-1] != "":
                out.append("")
            continue
        stripped = raw.strip()
        if stripped.startswith("#") or stripped.startswith("|") or stripped.startswith("```"):
            out.append(raw.rstrip())
            continue
        pieces = _SENT_SPLIT.split(stripped) if not stripped.startswith("//") else [stripped]
        kept: list[str] = []
        asides: list[str] = []
        for piece in pieces:
            piece = piece.strip()
            if not piece:
                continue
            if _drop(piece):
                continue
            text, lifted = _lift_parens(piece)
            asides.extend(lifted)
            text = _positive(text)
            text = _topic_comment(text)
            text = _tidy(text)
            if text:
                kept.append(text)
        line = " ".join(kept)
        if asides:
            tail = " ".join(f"// {a}" for a in asides)
            line = f"{line} {tail}".strip()
        if line:
            out.append(line)
    while out and out[-1] == "":
        out.pop()
    return "\n".join(out) + ("\n" if source.endswith("\n") or out else "")


def _drop(s: str) -> bool:
    if tells.MUSH.search(s) or tells.AS_AI.search(s) or tells.DISCLAIMER.search(s):
        return True
    if tells.RECAP.search(s) or tells.MARKETING.search(s) or tells.ROBUST.search(s):
        return True
    if tells.HOOK.search(s) or tells.HOOK_END.search(s):
        return True
    if tells.TRIPLE.match(s):
        return True
    return False


def _lift_parens(s: str) -> tuple[str, list[str]]:
    lifted: list[str] = []

    def take(m: re.Match) -> str:
        inner = m.group(1).strip()
        if _paren_keep(inner):
            return m.group(0)
        lifted.append(inner.rstrip("."))
        return " "

    s = tells.PAREN.sub(take, s)
    s = re.sub(r"\s+", " ", s).strip()
    return s, lifted


def _paren_keep(inner: str) -> bool:
    if inner.startswith("http"):
        return True
    if re.match(r"^[\w.+-]+@[\w.-]+$", inner):
        return True
    return False


def _positive(s: str) -> str:
    s = s.strip()
    m = tells.IS_NOT_Y.match(s.rstrip("."))
    if m:
        topic = m.group(1).strip()
        comment = m.group(2).strip().rstrip(".")
        return f"{topic} : {comment}."
    m = tells.ITS_NOT_Y.match(s.rstrip("."))
    if m:
        return _tidy(m.group(1))
    m = tells.THIS_IS_NOT_Y.match(s.rstrip("."))
    if m:
        return _tidy(m.group(1))
    m = tells.NOT_A_A.match(s.rstrip("."))
    if m:
        return _tidy(m.group(1))
    return s


def _topic_comment(s: str) -> str:
    s = s.strip()
    if " : " in s:
        return s
    t = s.rstrip(".")
    m = tells.TOPIC_IS.match(t)
    if not m:
        return s
    topic = m.group(1).strip().strip("`")
    comment = m.group(3).strip()
    if topic.lower() in {"there", "this", "that", "it", "what", "who"}:
        return s
    if len(topic.split()) > 6:
        return s
    return f"{topic} : {comment}."


def _tidy(s: str) -> str:
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s+([,.])", r"\1", s)
    if not s:
        return s
    if s[-1] not in ".!?:" and not s.startswith("//") and " : " in s:
        if not s.endswith("."):
            s = s + "."
    return s
