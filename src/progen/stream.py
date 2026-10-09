# src/progen/stream.py
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, List
import re


class UnitType(str, Enum):
    TOPIC_COMMENT = "topic_comment"
    PROSE = "prose"
    DEFINITION = "definition"
    ELEVATED = "elevated"
    TEST = "test"
    ADMIN = "admin"
    PROTOCOL = "protocol"
    ASIDE = "aside"


@dataclass
class StreamEvent:
    unit_type: UnitType
    topic: Optional[str] = None
    comment: Optional[str] = None
    text: Optional[str] = None
    warnings: List[str] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class StreamingProgenTokenizer:
    """
    A streaming tokenizer that processes incremental token chunks and detects
    topic:comment boundaries in real-time without waiting for EOF.
    """
    
    def __init__(self, role: str = "syntax"):
        self.role = role
        self.buffer = ""
        self.line_buffer = ""
        self.in_code_block = False
        self.copula_pattern = re.compile(r'\b(is|are|was|were|being)\b', re.IGNORECASE)
        if role == "slack":
            self.topic_pattern = re.compile(r'^([^,]{1,40}?),\s+(\S.*)$')
        else:
            self.topic_pattern = re.compile(r'^([^:]{1,80}?):\s+(\S.*)$')
        self.definition_pattern = re.compile(r'^([^=\n]{1,80}?)\s+=\s+(\S.*)$')
        self.elevated_pattern = re.compile(r'^!\s*(.+)$')
        self.test_pattern = re.compile(r'^\?\s*(.+)$')
        self.admin_pattern = re.compile(r'^[A-Z0-9][A-Z0-9 ,.\'-!]{2,}[A-Z0-9.!?]$')
        self.protocol_cmd_pattern = re.compile(r'^CMD,')
        self.protocol_look_format_pattern = re.compile(r'^(LOOK|FORMAT):')
        self.aside_pattern = re.compile(r'//')

    def feed(self, chunk: str) -> List[StreamEvent]:
        """
        Feed a chunk of text and return any completed StreamEvents.
        """
        events = []
        self.buffer += chunk
        
        # Process complete lines
        while '\n' in self.buffer:
            line, self.buffer = self.buffer.split('\n', 1)
            self.line_buffer += line + '\n'
            
            # Check for code block markers
            stripped_line = line.strip()
            if stripped_line.startswith('
