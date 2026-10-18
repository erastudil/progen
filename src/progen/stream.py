# SPDX-License-Identifier: AGPL-3.0-or-later
"""Streaming Progen tokenizer for incremental chunk-by-chunk parsing."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re
from typing import List, Optional

from .parse import _ADMIN_LINE, _split_asides, _topic_ok, _looks_like_heading
from .tells import COPULA_LEAD


class UnitType(str, Enum):
    TOPIC_COMMENT = "topic_comment"
    DEFINITION = "definition"
    ELEVATED = "elevated"
    TEST = "test"
    ADMIN = "admin"
    PROTOCOL = "protocol"
    PROSE = "prose"
    ASIDE = "aside"


@dataclass
class StreamEvent:
    unit_type: UnitType
    topic: Optional[str] = None
    comment: Optional[str] = None
    text: Optional[str] = None
    warnings: Optional[List[str]] = None

    def __post_init__(self) -> None:
        if self.warnings is None:
            self.warnings = []


class StreamingProgenTokenizer:
    """
    A streaming tokenizer that processes incremental token chunks and detects
    topic:comment boundaries in real-time without waiting for EOF.
    """

    def __init__(self, role: str = "syntax") -> None:
        self.role = role
        self.buffer = ""
        self.line_buffer = ""
        self.line_no = 0
        self.offset = 0
        self.in_code_block = False
        if role == "slack":
            self.topic_pattern = re.compile(r"^([^,]{1,40}?),\s+(\S.*)$")
        else:
            self.topic_pattern = re.compile(r"^([^:]{1,80}?):\s+(\S.*)$")
        self.syntax_fallback_pattern = re.compile(r"^([^:]{1,80}?):\s+(\S.*)$")
        self.definition_pattern = re.compile(r"^([^=\n]{1,80}?)\s+=\s+(\S.*)$")
        self.elevated_pattern = re.compile(r"^!\s*(.+)$")
        self.test_pattern = re.compile(r"^\?\s*(.+)$")
        self.admin_pattern = _ADMIN_LINE
        self.protocol_cmd_pattern = re.compile(r"^CMD,")
        self.protocol_look_format_pattern = re.compile(r"^(LOOK|FORMAT):")
        self.aside_pattern = re.compile(r"//")

    def feed(self, chunk: str) -> List[StreamEvent]:
        """Feed a chunk of text and return any completed StreamEvents."""
        events: List[StreamEvent] = []
        self.buffer += chunk

        while "\n" in self.buffer:
            line, self.buffer = self.buffer.split("\n", 1)
            self.line_buffer += line + "\n"
            self.line_no += 1
            raw = line.rstrip("\r")
            events.extend(self._process_line(raw, self.offset, self.line_no))
            self.offset += len(line) + 1

        return events

    def flush(self) -> List[StreamEvent]:
        """Flush any remaining buffered text at end of stream."""
        if not self.buffer:
            return []
        raw = self.buffer.rstrip("\r\n")
        self.line_buffer += raw
        self.line_no += 1
        line_offset = self.offset
        self.offset += len(self.buffer)
        self.buffer = ""
        return self._process_line(raw, line_offset, self.line_no)

    def _process_line(self, raw: str, line_start: int, line_no: int) -> List[StreamEvent]:
        events: List[StreamEvent] = []
        stripped = raw.strip()
        if stripped.startswith("```"):
            self.in_code_block = not self.in_code_block
            return events
        if self.in_code_block or not stripped or stripped.startswith("#"):
            return events

        body, asides = _split_asides(raw, line_start, line_no)
        body_stripped = body.strip()

        if body_stripped:
            events.append(self._classify_body(body_stripped))

        for aside in asides:
            events.append(StreamEvent(unit_type=UnitType.ASIDE, text=aside.text))

        return events

    def _classify_body(self, stripped: str) -> StreamEvent:
        warnings: List[str] = []

        m_elev = self.elevated_pattern.match(stripped)
        if m_elev:
            return StreamEvent(
                unit_type=UnitType.ELEVATED,
                comment=m_elev.group(1).strip(),
                text=stripped,
                warnings=warnings,
            )

        m_test = self.test_pattern.match(stripped)
        if m_test:
            return StreamEvent(
                unit_type=UnitType.TEST,
                comment=m_test.group(1).strip(),
                text=stripped,
                warnings=warnings,
            )

        if self.admin_pattern.match(stripped) and " " in stripped and not _looks_like_heading(stripped):
            return StreamEvent(
                unit_type=UnitType.ADMIN,
                text=stripped,
                warnings=warnings,
            )

        if self.protocol_cmd_pattern.match(stripped) or self.protocol_look_format_pattern.match(stripped):
            return StreamEvent(
                unit_type=UnitType.PROTOCOL,
                text=stripped,
                warnings=warnings,
            )

        m_def = self.definition_pattern.match(stripped)
        if m_def and ":" not in m_def.group(1):
            return StreamEvent(
                unit_type=UnitType.DEFINITION,
                topic=m_def.group(1).strip(),
                comment=m_def.group(2).strip(),
                text=stripped,
                warnings=warnings,
            )

        if self.role == "slack":
            m_topic = self.topic_pattern.match(stripped)
            if (
                m_topic
                and _topic_ok(m_topic.group(1))
                and m_topic.group(1).count(" ") <= 5
                and stripped.count(",") == 1
            ):
                topic = m_topic.group(1).strip()
                comment = m_topic.group(2).strip()
                return StreamEvent(
                    unit_type=UnitType.TOPIC_COMMENT,
                    topic=topic,
                    comment=comment,
                    text=stripped,
                    warnings=warnings,
                )
            m_syn = self.syntax_fallback_pattern.match(stripped)
            if m_syn and _topic_ok(m_syn.group(1)):
                topic = m_syn.group(1).strip()
                comment = m_syn.group(2).strip()
                return StreamEvent(
                    unit_type=UnitType.TOPIC_COMMENT,
                    topic=topic,
                    comment=comment,
                    text=stripped,
                    warnings=warnings,
                )
        else:
            m_topic = self.topic_pattern.match(stripped)
            if m_topic and _topic_ok(m_topic.group(1)):
                topic = m_topic.group(1).strip()
                comment = m_topic.group(2).strip()
                if COPULA_LEAD.search(stripped):
                    warnings.append("P018: leading copula in comment")
                return StreamEvent(
                    unit_type=UnitType.TOPIC_COMMENT,
                    topic=topic,
                    comment=comment,
                    text=stripped,
                    warnings=warnings,
                )

        return StreamEvent(
            unit_type=UnitType.PROSE,
            text=stripped,
            warnings=warnings,
        )
