# SPDX-License-Identifier: AGPL-3.0-or-later
"""tell patterns. the linter owns this list. prompts point here."""

from __future__ import annotations

import re

MUSH = re.compile(
    r"\b(i['’]d be happy to|i would be happy to|great question|absolutely!|"
    r"happy to help)\b",
    re.IGNORECASE,
)
AS_AI = re.compile(r"\b(as an ai|i am an ai|i['’]m an ai)\b", re.IGNORECASE)
DUALISM = re.compile(
    r"\b(it['’]s not\b.{1,60}\bit['’]s\b|this is not\b.{1,60}\bit is\b|"
    r"not a .{1,40}, a )",
    re.IGNORECASE,
)
NOT_THIS = re.compile(r"\bis not this\b", re.IGNORECASE)
OVER_NOT_OVER = re.compile(r"\bover\b.{0,80}\bnot over\b", re.IGNORECASE)
COMMA_NOT_ON_THE = re.compile(
    r",\s*not on the (net|weights|architecture|model|base)\b",
    re.IGNORECASE,
)
SPLIT_HEAD = re.compile(r"\b(this is not|it['’]s not)\b", re.IGNORECASE)
SPLIT_TAIL = re.compile(r"^(it['’]s|it is)\b", re.IGNORECASE)
TOPIC_COMMENT = re.compile(r"^[^:\n#|]{1,48}:\s+\S")
EXTRA_SCOPE = re.compile(
    r"\b(while i was here|drive[- ]by|might as well|also refactored|also cleaned(?: up)?)\b",
    re.IGNORECASE,
)
PROOF = re.compile(
    r"\b(pytest|unittest|progen check|tests? passed|tool proof|\d+ passing)\b",
    re.IGNORECASE,
)
CODE_JOB = re.compile(
    r"\b(patch landed|landed the patch|the patch is done|fixed the bug)\b",
    re.IGNORECASE,
)
WORD = re.compile(r"[a-z0-9']+", re.IGNORECASE)
STOP = frozenset(
    "the a an of and to for in on is it as at by or we you they this that with from".split()
)
HOOK = re.compile(
    r"\b(what should we\b|what would you like\b|want me to\b|shall i\b|"
    r"let me know if\b|anything else i can\b|how can i (help|assist)\b|"
    r"what would you like (me )?to (do|work on)\b)",
    re.IGNORECASE,
)
HOOK_END = re.compile(
    r"(what should we|what would you like|want me to|shall i|"
    r"let me know if|anything else|how can i help).{0,40}\?\s*$",
    re.IGNORECASE,
)
RECAP = re.compile(
    r"\b(in conclusion\b|to recap\b|to summarize\b|full circle\b|"
    r"let me recap\b|as (i|we) mentioned\b)",
    re.IGNORECASE,
)
DISCLAIMER = re.compile(
    r"\b(not (a |legal |financial |medical )?advice\b|i am not a (lawyer|doctor|cpa)\b|"
    r"this is not (legal|financial|medical) advice\b|consult a (professional|lawyer|doctor)\b)",
    re.IGNORECASE,
)
MARKETING = re.compile(
    r"\b(delve|leverage|tapestry|let['’]s dive in|dive in)\b",
    re.IGNORECASE,
)
ROBUST = re.compile(r"\brobust\b", re.IGNORECASE)
TRIPLE = re.compile(r"^\[(EN|RO|JA)\]\s")
PAREN = re.compile(r"\(([A-Za-z][^)]{2,120})\)")
WILL_NOT_BULLET = re.compile(
    r"^[-*]\s+(do not|don't|do\s+not|never)\b",
    re.IGNORECASE,
)
STUB = re.compile(r"\b(TODO|TBD|FIXME|placeholder)\b")
DONE_CLAIM = re.compile(r"\b(done|complete|finished)\b", re.IGNORECASE)
IS_NOT_Y = re.compile(
    r"^(.+?)\s+is not\b.+?,\s*it['’]s\s+(.+)$",
    re.IGNORECASE,
)
ITS_NOT_Y = re.compile(
    r"^it['’]s not\b.+?\bit['’]s\s+(.+)$",
    re.IGNORECASE,
)
THIS_IS_NOT_Y = re.compile(
    r"^this is not\b.+?\bit is\s+(.+)$",
    re.IGNORECASE,
)
NOT_A_A = re.compile(
    r"^not a .+?, a (.+)$",
    re.IGNORECASE,
)
TOPIC_IS = re.compile(
    r"^(?:The |A |An )?([A-Za-z][\w. `'-]{0,40}?) (is|are) (.+)$",
    re.IGNORECASE,
)
LATCH_THRESHOLD = 3
