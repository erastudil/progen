# SPDX-License-Identifier: AGPL-3.0-or-later
"""progen mark parser.

Does not compile English. Marks what SPEC says a parser can see.
Slack commas use a short-topic heuristic. Named here so it cannot hide.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import re
from typing import Optional


class Role(str, Enum):
    IRON = "iron"
    SLACK = "slack"


@dataclass(frozen=True)
class Span:
    start: int
    end: int
    line: int


@dataclass(frozen=True)
class Aside:
    text: str
    span: Span


@dataclass(frozen=True)
class Unit:
    kind: str
    text: str
    span: Span
    topic: Optional[str] = None
    comment: Optional[str] = None
    mark: Optional[str] = None


@dataclass
class Document:
    role: Role
    source: str
    units: list[Unit] = field(default_factory=list)
    asides: list[Aside] = field(default_factory=list)
    flags: dict = field(default_factory=dict)


_ASIDE = re.compile(r"//")
_SLACK_TOPIC = re.compile(r"^([^,]{1,40}?),\s+(\S.*)$")
_IRON_TOPIC = re.compile(r"^([^:]{1,80}?):\s+(\S.*)$")
_DEFINITION = re.compile(r"^([^=\n]{1,80}?)\s+=\s+(\S.*)$")
_OPEN_CLASS = re.compile(r"\betc\.?\b", re.IGNORECASE)
_ADMIN_LINE = re.compile(r"^[A-Z0-9][A-Z0-9 ,.'\-!]{2,}[A-Z0-9.!?]$")
_PROTOCOL = re.compile(r"^(LOOK|FORMAT):")
_CMD = re.compile(r"^CMD,")


def parse_text(source: str, role: Role | str = Role.IRON) -> Document:
    role = Role(role)
    doc = Document(role=role, source=source)
    offset = 0
    for line_no, line in enumerate(source.splitlines(keepends=True), start=1):
        raw = line.rstrip("\r\n")
        line_start = offset
        offset += len(line)
        if not raw.strip():
            continue
        body, asides = _split_asides(raw, line_start, line_no)
        doc.asides.extend(asides)
        if not body.strip():
            continue
        doc.units.append(_unit(body, role, line_start, line_no))
        _flags(doc, body)
    if doc.asides:
        doc.flags["has_asides"] = True
    return doc


def _split_asides(raw: str, line_start: int, line_no: int) -> tuple[str, list[Aside]]:
    asides: list[Aside] = []
    if "//" not in raw:
        return raw, asides
    # URLs: https://  — not an aside
    pieces = []
    i = 0
    while i < len(raw):
        j = raw.find("//", i)
        if j < 0:
            pieces.append(raw[i:])
            break
        prefix = raw[max(0, j - 6) : j]
        if prefix.endswith(":") and j >= 1:
            # scheme://
            pieces.append(raw[i : j + 2])
            i = j + 2
            continue
        pieces.append(raw[i:j])
        rest = raw[j + 2 :]
        cut = rest.find(". ")
        if cut >= 0:
            aside_text = rest[: cut + 1].strip()
            remainder = rest[cut + 1 :]
        else:
            aside_text = rest.strip()
            remainder = ""
        asides.append(
            Aside(
                text=aside_text,
                span=Span(line_start + j, line_start + j + 2 + len(aside_text), line_no),
            )
        )
        i = len(raw) - len(remainder)
        if remainder:
            pieces.append(remainder)
            break
    return "".join(pieces).rstrip(), asides


def _unit(body: str, role: Role, line_start: int, line_no: int) -> Unit:
    stripped = body.strip()
    span = Span(line_start, line_start + len(body), line_no)
    if stripped.startswith("!") and len(stripped) > 1:
        inner = stripped[1:].lstrip()
        return Unit(kind="elevated", text=stripped, span=span, mark="!", comment=inner)
    if stripped.startswith("?") and len(stripped) > 1:
        inner = stripped[1:].lstrip()
        return Unit(kind="test", text=stripped, span=span, mark="?", comment=inner)
    if _ADMIN_LINE.match(stripped) and " " in stripped and not _looks_like_heading(stripped):
        return Unit(kind="admin", text=stripped, span=span, mark="CAPSLOCK")
    if _PROTOCOL.match(stripped) or _CMD.match(stripped):
        mark = "," if _CMD.match(stripped) else ":"
        return Unit(kind="protocol", text=stripped, span=span, mark=mark)
    m = _DEFINITION.match(stripped)
    if m and ":" not in m.group(1):
        return Unit(
            kind="definition",
            text=stripped,
            span=span,
            topic=m.group(1).strip(),
            comment=m.group(2).strip(),
            mark="=",
        )
    if role is Role.IRON:
        m = _IRON_TOPIC.match(stripped)
        if m and _topic_ok(m.group(1)):
            return Unit(
                kind="topic_comment",
                text=stripped,
                span=span,
                topic=m.group(1).strip(),
                comment=m.group(2).strip(),
                mark=":",
            )
    else:
        m = _SLACK_TOPIC.match(stripped)
        # one comma on the line. many commas stay english prose.
        if (
            m
            and _topic_ok(m.group(1))
            and m.group(1).count(" ") <= 5
            and stripped.count(",") == 1
        ):
            return Unit(
                kind="topic_comment",
                text=stripped,
                span=span,
                topic=m.group(1).strip(),
                comment=m.group(2).strip(),
                mark=",",
            )
        m = _IRON_TOPIC.match(stripped)
        if m and _topic_ok(m.group(1)):
            return Unit(
                kind="topic_comment",
                text=stripped,
                span=span,
                topic=m.group(1).strip(),
                comment=m.group(2).strip(),
                mark=":",
            )
    return Unit(kind="prose", text=stripped, span=span)


def _topic_ok(topic: str) -> bool:
    t = topic.strip()
    if not t or t.endswith((".", "?", "!")):
        return False
    if t.lower().startswith(("http://", "https://")):
        return False
    # markdown / clock times
    if re.match(r"^\d+$", t):
        return False
    return True


def _looks_like_heading(s: str) -> bool:
    return s.startswith("#") or s.endswith(":")


def _flags(doc: Document, body: str) -> None:
    if _OPEN_CLASS.search(body):
        doc.flags["open_class"] = True
    stripped = body.strip()
    if stripped.startswith("!"):
        doc.flags["elevated"] = True
    if stripped.startswith("?"):
        doc.flags["test"] = True
    if _ADMIN_LINE.match(stripped) and " " in stripped:
        doc.flags["admin"] = True
