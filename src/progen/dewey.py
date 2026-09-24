# SPDX-License-Identifier: AGPL-3.0-or-later
"""progen dewey classification taxonomy and indexing utilities."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Optional


@dataclass(frozen=True)
class DeweyClass:
    code: str
    parent_code: Optional[str]
    slug: str
    title: str
    depth: int = 0


# Top-level and primary divisions aligning with standard DDC and The Stacks
DEFAULT_TAXONOMY: tuple[DeweyClass, ...] = (
    # 000: Computer science, information & general works
    DeweyClass("000", None, "general", "Computer science, information, & systems", 0),
    DeweyClass("001", "000", "methods", "Scientific method, evidence, error, knowledge", 1),
    DeweyClass("004", "000", "computing", "Computer hardware, processing, networks", 1),
    DeweyClass("005", "000", "software", "Software engineering, programs, data", 1),
    DeweyClass("005.1", "005", "programming", "Programming, algorithms, design patterns", 2),
    DeweyClass("005.7", "005", "data_structures", "Data management, formats, storage", 2),
    DeweyClass("005.74", "005.7", "databases", "Databases, data models, relational schemas", 3),
    DeweyClass("005.8", "005", "security", "Information security, cryptography, defense", 2),
    DeweyClass("006", "000", "ai_ml", "Artificial intelligence, models, neural inference", 1),

    # 100: Philosophy & psychology
    DeweyClass("100", None, "philosophy", "Philosophy, logic, epistemology, mind", 0),
    DeweyClass("110", "100", "metaphysics", "Metaphysics, ontology, reality", 1),
    DeweyClass("120", "100", "epistemology", "Epistemology, truth, justification", 1),
    DeweyClass("150", "100", "psychology", "Cognition, memory, behavior, perception", 1),
    DeweyClass("160", "100", "logic", "Formal logic, deduction, inference", 1),
    DeweyClass("170", "100", "ethics", "Ethics, moral philosophy, governance", 1),

    # 200: Religion
    DeweyClass("200", None, "religion", "Comparative religion, mythology, sacred traditions", 0),

    # 300: Social sciences
    DeweyClass("300", None, "sociology", "Social structures, culture, anthropology", 0),
    DeweyClass("320", "300", "civics", "Civics, political science, constitutions, rights", 1),
    DeweyClass("330", "300", "finance", "Economics, finance, value, markets, risk", 1),
    DeweyClass("340", "300", "law", "Law, jurisprudence, procedure, contracts", 1),

    # 400: Language
    DeweyClass("400", None, "language", "Linguistics, grammar, meaning, communication", 0),
    DeweyClass("410", "400", "linguistics", "Linguistics, syntax, semantics, dialects", 1),
    DeweyClass("420", "400", "english", "English language, dialectology, usage", 1),

    # 500: Pure sciences
    DeweyClass("500", None, "science", "Natural sciences & mathematics", 0),
    DeweyClass("510", "500", "math", "Mathematics, proof, number, space, calculus", 1),
    DeweyClass("520", "500", "astronomy", "Astronomy, celestial mechanics, astrophysics", 1),
    DeweyClass("530", "500", "physics", "Physics, mechanics, thermodynamics, quantum", 1),
    DeweyClass("540", "500", "chemistry", "Chemistry, matter, reaction, composition", 1),
    DeweyClass("550", "500", "earth_sciences", "Earth sciences, geology, meteorology", 1),
    DeweyClass("570", "500", "biology", "Biology, genetics, cells, evolution, ecology", 1),

    # 600: Technology & applied sciences
    DeweyClass("600", None, "technology", "Applied science & engineering", 0),
    DeweyClass("610", "600", "health", "Medicine, health, physiology, pathology", 1),
    DeweyClass("620", "600", "engineering", "Engineering, circuits, mechanics, structures", 1),
    DeweyClass("630", "600", "agriculture", "Agriculture, plants, soil, food systems", 1),
    DeweyClass("650", "600", "business", "Business, management, accounting, operations", 1),
    DeweyClass("690", "600", "trades", "Building trades, machining, electrical, fabrication", 1),

    # 700: Arts & recreation
    DeweyClass("700", None, "art", "Arts, visual design, composition", 0),
    DeweyClass("780", "700", "music", "Music, acoustic theory, harmony, instruments", 1),

    # 800: Literature
    DeweyClass("800", None, "literature", "Literature, narrative, rhetoric, criticism", 0),
    DeweyClass("811", "800", "poetry", "Poetry, meter, prosody, verse", 1),

    # 900: History & geography
    DeweyClass("900", None, "history", "History, historiography, chronology", 0),
    DeweyClass("910", "900", "geography", "Geography, cartography, travel", 1),
)

_TAXONOMY_MAP = {c.code: c for c in DEFAULT_TAXONOMY}


# Lexical mapping patterns for heuristic auto-classification
_LEXICAL_RULES: list[tuple[re.Pattern, str]] = [
    # Software & Databases
    (re.compile(r"\b(sql|sqlite|database|postgres|schema|index|query|table|b-tree|crud)\b", re.IGNORECASE), "005.74"),
    (re.compile(r"\b(security|cryptography|hash|cipher|sha256|token|key|canary|auth)\b", re.IGNORECASE), "005.8"),
    (re.compile(r"\b(software|code|python|repo|git|linter|parser|compiler|refactor|test)\b", re.IGNORECASE), "005"),

    # Language & Dialects
    (re.compile(r"\b(dialect|grammar|syntax|linguistics|semantic|progen|topic|comment)\b", re.IGNORECASE), "410"),
    (re.compile(r"\b(english|word|vocabulary|lexicon|dictionary|prose)\b", re.IGNORECASE), "420"),

    # AI & Machine Learning
    (re.compile(r"\b(ai|ml|model|llm|neural|weights|inference|prompt|agent|transformer)\b", re.IGNORECASE), "006"),
    (re.compile(r"\b(hardware|cpu|gpu|network|socket|memory|bus|server)\b", re.IGNORECASE), "004"),
    (re.compile(r"\b(method|evidence|falsification|observation|measurement)\b", re.IGNORECASE), "001"),

    # Philosophy & Mind
    (re.compile(r"\b(ethics|moral|duty|justice|virtue|covenant)\b", re.IGNORECASE), "170"),
    (re.compile(r"\b(logic|deduction|premise|syllogism|tautology)\b", re.IGNORECASE), "160"),
    (re.compile(r"\b(psychology|cognition|brain|perception|behavior|attention)\b", re.IGNORECASE), "150"),
    (re.compile(r"\b(epistemology|truth|knowledge|belief|justification)\b", re.IGNORECASE), "120"),
    (re.compile(r"\b(philosophy|ontology|metaphysics|tao|zen|wu wei)\b", re.IGNORECASE), "100"),

    # Social sciences, Law, Finance
    (re.compile(r"\b(law|legal|statute|jurisprudence|contract|license|court)\b", re.IGNORECASE), "340"),
    (re.compile(r"\b(finance|money|currency|market|economy|bank|cost|capital)\b", re.IGNORECASE), "330"),
    (re.compile(r"\b(civics|constitution|government|democracy|citizen|rights)\b", re.IGNORECASE), "320"),

    # Sciences
    (re.compile(r"\b(math|mathematics|calculus|algebra|number|prime|proof|equation)\b", re.IGNORECASE), "510"),
    (re.compile(r"\b(astronomy|star|planet|cosmos|galaxy|orbit)\b", re.IGNORECASE), "520"),
    (re.compile(r"\b(physics|quantum|particle|gravity|velocity|force|energy|thermodynamics)\b", re.IGNORECASE), "530"),
    (re.compile(r"\b(chemistry|molecule|atom|reaction|compound|acid|bond)\b", re.IGNORECASE), "540"),
    (re.compile(r"\b(earth|geology|plate|rock|weather|climate|ocean)\b", re.IGNORECASE), "550"),
    (re.compile(r"\b(biology|cell|gene|dna|organism|evolution|species|ecology)\b", re.IGNORECASE), "570"),

    # Applied sciences
    (re.compile(r"\b(medicine|health|disease|clinical|anatomy|drug|therapy)\b", re.IGNORECASE), "610"),
    (re.compile(r"\b(engineering|circuit|voltage|structural|engine|mechanism)\b", re.IGNORECASE), "620"),
    (re.compile(r"\b(agriculture|soil|crop|farming|plant|irrigation)\b", re.IGNORECASE), "630"),
    (re.compile(r"\b(business|marketing|management|strategy|firm|enterprise)\b", re.IGNORECASE), "650"),
    (re.compile(r"\b(machining|weld|carpentry|plumbing|trade|cnc|tooling)\b", re.IGNORECASE), "690"),

    # Arts & Literature
    (re.compile(r"\b(music|pitch|scale|rhythm|melody|harmony|audio)\b", re.IGNORECASE), "780"),
    (re.compile(r"\b(art|painting|drawing|visual|aesthetic|color)\b", re.IGNORECASE), "700"),
    (re.compile(r"\b(poetry|poem|verse|meter|rhyme|sonnet)\b", re.IGNORECASE), "811"),
    (re.compile(r"\b(literature|fiction|novel|author|narrative|rhetoric)\b", re.IGNORECASE), "800"),

    # History & Geography
    (re.compile(r"\b(geography|map|cartography|latitude|region|terrain)\b", re.IGNORECASE), "910"),
    (re.compile(r"\b(history|historian|century|ancient|empire|war|chronicle)\b", re.IGNORECASE), "900"),
]


def classify_text(topic: str, comment: str = "") -> Optional[str]:
    """Return the best matching Dewey classification code for a topic and comment."""
    combined = f"{topic} {comment}"
    # Check embedded dewey code in topic e.g. [005.8] or (005.8)
    m = re.match(r"^\[([0-9]{3}(?:\.[0-9]+)?)\]", topic)
    if m:
        code = m.group(1)
        if code in _TAXONOMY_MAP:
            return code
    for pattern, code in _LEXICAL_RULES:
        if pattern.search(combined):
            return code
    return None


def get_class(code: str) -> Optional[DeweyClass]:
    """Retrieve metadata for a specific Dewey code."""
    return _TAXONOMY_MAP.get(code)


def matches_dewey(code: Optional[str], pattern: str) -> bool:
    """Check if a dewey code matches a pattern (exact, prefix with *, or range 'X-Y')."""
    if not code:
        return False
    pat = pattern.strip()
    if pat == "*" or pat == "":
        return True
    if "-" in pat:
        parts = pat.split("-", 1)
        try:
            val = float(code)
            min_v = float(parts[0])
            max_v = float(parts[1])
            return min_v <= val <= max_v
        except ValueError:
            return False
    if pat.endswith("*"):
        prefix = pat[:-1]
        return code.startswith(prefix)
    return code == pat


def build_tree(counts: dict[str, int]) -> list[dict]:
    """Build a nested hierarchical taxonomy tree including record counts."""
    tree: list[dict] = []
    nodes: dict[str, dict] = {}

    for c in DEFAULT_TAXONOMY:
        count = counts.get(c.code, 0)
        node = {
            "code": c.code,
            "slug": c.slug,
            "title": c.title,
            "depth": c.depth,
            "count": count,
            "total_count": count,
            "children": [],
        }
        nodes[c.code] = node
        if c.parent_code is None or c.parent_code not in nodes:
            tree.append(node)
        else:
            nodes[c.parent_code]["children"].append(node)

    # Roll up counts to ancestors
    def rollup(node: dict) -> int:
        child_sum = sum(rollup(child) for child in node["children"])
        node["total_count"] = node["count"] + child_sum
        return node["total_count"]

    for root in tree:
        rollup(root)

    return tree
