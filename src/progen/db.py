# SPDX-License-Identifier: AGPL-3.0-or-later
"""progen relational database engine and dewey indexing store."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sqlite3
from typing import Generator, Iterable, Optional

from . import dewey
from .parse import Document, Role, parse_text

# Letters, digits, and single spaces. A fact is this alphabet on both sides.
_FACT_TEXT = re.compile(r"[A-Za-z0-9]+(?: [A-Za-z0-9]+)*\Z")


def is_fact_text(text: str) -> bool:
    """True when the string is alphanumeric words."""
    return _FACT_TEXT.fullmatch(text.strip()) is not None


def fact_line(topic: str, comment: str) -> str:
    """Return one `topic: comment` line. Both sides are alphanumeric words."""
    topic_s = topic.strip()
    comment_s = comment.strip()
    if not is_fact_text(topic_s) or not is_fact_text(comment_s):
        raise ValueError("fact is alphanumeric words")
    return f"{topic_s}: {comment_s}"


@dataclass
class UnitRecord:
    id: str
    source_id: int
    line_no: int
    kind: str
    mark: str
    topic: str
    comment: str
    dewey_code: Optional[str]
    parent_unit_id: Optional[str]
    created_at: str
    updated_at: str
    source_uri: Optional[str] = None
    dewey_slug: Optional[str] = None
    asides: list[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        """Render this unit as a canonical Progen line."""
        mark = self.mark or ":"
        asides_str = f" // {' // '.join(self.asides)}" if self.asides else ""
        if self.kind == "definition" or mark == "=":
            return f"{self.topic} = {self.comment}{asides_str}"
        if self.kind == "elevated" or mark == "!":
            return f"! {self.topic} : {self.comment}{asides_str}"
        if self.kind == "test" or mark == "?":
            return f"? {self.topic} : {self.comment}{asides_str}"
        if self.kind == "admin":
            return f"{self.topic}{asides_str}"
        return f"{self.topic} : {self.comment}{asides_str}"


@dataclass
class SourceRecord:
    id: int
    uri: str
    hash: str
    role: str
    layer: str
    unit_count: int
    created_at: str
    updated_at: str


class ProgenDB:
    """Zero-rent SQLite storage engine for Progen dialect units and Dewey indexing."""

    def __init__(self, db_path: str | Path = ":memory:"):
        self.db_path = str(db_path)
        self.conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
            isolation_level=None,  # Autocommit mode; transactions managed explicitly
        )
        self.conn.row_factory = sqlite3.Row
        self._has_fts = False
        self._facts: dict[str, Optional[str]] | None = None
        self._init_db()

    def _init_db(self) -> None:
        cur = self.conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON;")
        cur.execute("PRAGMA temp_store = MEMORY;")
        cur.execute("PRAGMA cache_size = -32000;")
        if self.db_path != ":memory:":
            try:
                cur.execute("PRAGMA journal_mode = WAL;")
                cur.execute("PRAGMA synchronous = NORMAL;")
            except sqlite3.OperationalError:
                pass

        cur.execute("""
            CREATE TABLE IF NOT EXISTS sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uri TEXT UNIQUE NOT NULL,
                hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'syntax',
                layer TEXT NOT NULL DEFAULT 'warehouse',
                unit_count INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_sources_hash ON sources(hash);")

        cur.execute("""
            CREATE TABLE IF NOT EXISTS dewey_classes (
                code TEXT PRIMARY KEY,
                parent_code TEXT,
                slug TEXT NOT NULL,
                title TEXT NOT NULL,
                depth INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (parent_code) REFERENCES dewey_classes(code)
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS units (
                id TEXT PRIMARY KEY,
                source_id INTEGER NOT NULL,
                line_no INTEGER NOT NULL,
                kind TEXT NOT NULL CHECK (kind IN ('topic_comment', 'definition', 'elevated', 'test', 'admin', 'protocol', 'prose')),
                mark TEXT,
                topic TEXT NOT NULL CHECK (length(topic) > 0),
                comment TEXT NOT NULL,
                dewey_code TEXT,
                parent_unit_id TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE CASCADE,
                FOREIGN KEY (dewey_code) REFERENCES dewey_classes(code) ON DELETE SET NULL,
                FOREIGN KEY (parent_unit_id) REFERENCES units(id) ON DELETE SET NULL
            );
        """)

        cur.execute("CREATE INDEX IF NOT EXISTS idx_units_topic ON units(topic COLLATE NOCASE);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_units_dewey ON units(dewey_code);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_units_dewey_topic ON units(dewey_code, topic COLLATE NOCASE);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_units_kind ON units(kind);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_units_source ON units(source_id);")

        cur.execute("""
            CREATE TABLE IF NOT EXISTS asides (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                unit_id TEXT NOT NULL,
                text TEXT NOT NULL,
                line_no INTEGER NOT NULL,
                FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE CASCADE
            );
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_asides_unit ON asides(unit_id);")

        # FTS5 virtual table for full-text search with native sync triggers
        try:
            cur.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS units_fts USING fts5(
                    unit_id UNINDEXED,
                    topic,
                    comment,
                    dewey_code UNINDEXED,
                    asides_text
                );
            """)
            cur.execute("""
                CREATE TRIGGER IF NOT EXISTS trg_units_ai AFTER INSERT ON units
                BEGIN
                    INSERT INTO units_fts (unit_id, topic, comment, dewey_code, asides_text)
                    VALUES (new.id, new.topic, new.comment, COALESCE(new.dewey_code, ''), '');
                END;
            """)
            cur.execute("""
                CREATE TRIGGER IF NOT EXISTS trg_units_ad AFTER DELETE ON units
                BEGIN
                    DELETE FROM units_fts WHERE unit_id = old.id;
                END;
            """)
            cur.execute("""
                CREATE TRIGGER IF NOT EXISTS trg_units_au AFTER UPDATE ON units
                BEGIN
                    DELETE FROM units_fts WHERE unit_id = old.id;
                    INSERT INTO units_fts (unit_id, topic, comment, dewey_code, asides_text)
                    VALUES (new.id, new.topic, new.comment, COALESCE(new.dewey_code, ''),
                            (SELECT COALESCE(GROUP_CONCAT(text, ' '), '') FROM asides WHERE unit_id = new.id));
                END;
            """)
            cur.execute("""
                CREATE TRIGGER IF NOT EXISTS trg_asides_ai AFTER INSERT ON asides
                BEGIN
                    UPDATE units_fts
                    SET asides_text = (SELECT COALESCE(GROUP_CONCAT(text, ' '), '') FROM asides WHERE unit_id = new.unit_id)
                    WHERE unit_id = new.unit_id;
                END;
            """)
            cur.execute("""
                CREATE TRIGGER IF NOT EXISTS trg_asides_ad AFTER DELETE ON asides
                BEGIN
                    UPDATE units_fts
                    SET asides_text = (SELECT COALESCE(GROUP_CONCAT(text, ' '), '') FROM asides WHERE unit_id = old.unit_id)
                    WHERE unit_id = old.unit_id;
                END;
            """)
            self._has_fts = True
        except sqlite3.OperationalError:
            self._has_fts = False

        self._seed_dewey()

    def _seed_dewey(self) -> None:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) as cnt FROM dewey_classes;")
        if cur.fetchone()["cnt"] == 0:
            for c in dewey.DEFAULT_TAXONOMY:
                cur.execute(
                    """
                    INSERT OR IGNORE INTO dewey_classes (code, parent_code, slug, title, depth)
                    VALUES (?, ?, ?, ?, ?);
                    """,
                    (c.code, c.parent_code, c.slug, c.title, c.depth),
                )

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Cursor, None, None]:
        """Atomic transaction context manager."""
        cur = self.conn.cursor()
        cur.execute("BEGIN TRANSACTION;")
        try:
            yield cur
            cur.execute("COMMIT;")
        except Exception:
            cur.execute("ROLLBACK;")
            raise

    def __enter__(self) -> "ProgenDB":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def close(self) -> None:
        self.conn.close()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def make_unit_id(source_uri: str, line_no: int, topic: str, comment: str) -> str:
        raw = f"{source_uri}:{line_no}:{topic.strip().lower()}:{comment.strip()}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    # --- Normal Database Functions: CRUD ---

    def insert_unit(
        self,
        topic: str,
        comment: str,
        mark: str = ":",
        kind: Optional[str] = None,
        dewey_code: Optional[str] = None,
        source_id: Optional[int] = None,
        line_no: int = 1,
        asides: Optional[list[str]] = None,
        parent_unit_id: Optional[str] = None,
    ) -> str:
        """Insert a single unit assertion."""
        if kind is None:
            if mark == "=":
                kind = "definition"
            elif mark == "!":
                kind = "elevated"
            elif mark == "?":
                kind = "test"
            else:
                kind = "topic_comment"

        # Auto-classify Dewey if not explicitly given
        if dewey_code is None:
            dewey_code = dewey.classify_text(topic, comment)

        now = self._now()
        cur = self.conn.cursor()

        if source_id is None:
            cur.execute("SELECT id FROM sources WHERE uri = 'default';")
            row = cur.fetchone()
            if row:
                source_id = row["id"]
            else:
                cur.execute(
                    """
                    INSERT INTO sources (uri, hash, role, layer, unit_count, created_at, updated_at)
                    VALUES ('default', '0', 'syntax', 'warehouse', 0, ?, ?);
                    """,
                    (now, now),
                )
                source_id = cur.lastrowid

        cur.execute("SELECT uri FROM sources WHERE id = ?;", (source_id,))
        s_row = cur.fetchone()
        source_uri = s_row["uri"] if s_row else "default"

        unit_id = self.make_unit_id(source_uri, line_no, topic, comment)

        cur.execute(
            """
            INSERT OR REPLACE INTO units (id, source_id, line_no, kind, mark, topic, comment, dewey_code, parent_unit_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (unit_id, source_id, line_no, kind, mark, topic.strip(), comment.strip(), dewey_code, parent_unit_id, now, now),
        )

        cur.execute("DELETE FROM asides WHERE unit_id = ?;", (unit_id,))
        asides_list = asides or []
        for aside_text in asides_list:
            cur.execute(
                "INSERT INTO asides (unit_id, text, line_no) VALUES (?, ?, ?);",
                (unit_id, aside_text.strip(), line_no),
            )

        # Update source unit count
        cur.execute("SELECT COUNT(*) as cnt FROM units WHERE source_id = ?;", (source_id,))
        cnt = cur.fetchone()["cnt"]
        cur.execute("UPDATE sources SET unit_count = ?, updated_at = ? WHERE id = ?;", (cnt, now, source_id))
        self._cache_topic(topic.strip())
        return unit_id

    def get_unit(self, unit_id: str) -> Optional[UnitRecord]:
        """Retrieve a unit by ID."""
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT u.*, s.uri as source_uri, d.slug as dewey_slug
            FROM units u
            JOIN sources s ON u.source_id = s.id
            LEFT JOIN dewey_classes d ON u.dewey_code = d.code
            WHERE u.id = ?;
            """,
            (unit_id,),
        )
        row = cur.fetchone()
        if not row:
            return None

        cur.execute("SELECT text FROM asides WHERE unit_id = ? ORDER BY id;", (unit_id,))
        asides = [r["text"] for r in cur.fetchall()]

        return UnitRecord(
            id=row["id"],
            source_id=row["source_id"],
            line_no=row["line_no"],
            kind=row["kind"],
            mark=row["mark"],
            topic=row["topic"],
            comment=row["comment"],
            dewey_code=row["dewey_code"],
            parent_unit_id=row["parent_unit_id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            source_uri=row["source_uri"],
            dewey_slug=row["dewey_slug"],
            asides=asides,
        )

    def fact(self, topic: str) -> Optional[str]:
        """Return one alphanumeric fact as `topic: comment`, or None.

        The first call for a topic reads the sqlite index. Later calls read a process hash.
        """
        raw = topic.strip()
        key = raw.casefold()
        if not key or not is_fact_text(raw):
            return None
        if self._facts is not None and key in self._facts:
            return self._facts[key]
        line = self._read_fact(raw)
        if self._facts is None:
            self._facts = {}
        self._facts[key] = line
        return line

    def _read_fact(self, topic: str) -> Optional[str]:
        """Index read for one topic. The last alphanumeric row wins."""
        cur = self.conn.execute(
            """
            SELECT topic, comment FROM units
            WHERE topic = ? COLLATE NOCASE
            ORDER BY updated_at ASC, rowid ASC;
            """,
            (topic,),
        )
        found: Optional[str] = None
        for row in cur:
            if is_fact_text(row["topic"]) and is_fact_text(row["comment"]):
                found = f"{row['topic']}: {row['comment']}"
        return found

    def put_fact(self, topic: str, comment: str) -> str:
        """Store one alphanumeric fact. The same topic replaces the previous line."""
        topic_s = topic.strip()
        comment_s = comment.strip()
        line = fact_line(topic_s, comment_s)
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT id, topic, comment FROM units
            WHERE topic = ? COLLATE NOCASE
            ORDER BY updated_at ASC, rowid ASC;
            """,
            (topic_s,),
        )
        rows = [
            r for r in cur.fetchall()
            if is_fact_text(r["topic"]) and is_fact_text(r["comment"])
        ]
        if not rows:
            uid = self.insert_unit(topic=topic_s, comment=comment_s)
        else:
            uid = rows[-1]["id"]
            for extra in rows[:-1]:
                self.delete_unit(extra["id"])
            self.update_unit(uid, topic=topic_s, comment=comment_s)
        if self._facts is None:
            self._facts = {}
        self._facts[topic_s.casefold()] = line
        return uid

    def _cache_topic(self, topic: str) -> None:
        """Refresh one topic in the hash. A cold hash stays cold."""
        if self._facts is None:
            return
        key = topic.strip().casefold()
        if not key:
            return
        self._facts.pop(key, None)
        cur = self.conn.execute(
            """
            SELECT topic, comment FROM units
            WHERE topic = ? COLLATE NOCASE
            ORDER BY updated_at ASC, rowid ASC;
            """,
            (topic.strip(),),
        )
        for row in cur:
            if is_fact_text(row["topic"]) and is_fact_text(row["comment"]):
                self._facts[row["topic"].casefold()] = f"{row['topic']}: {row['comment']}"

    def update_unit(
        self,
        unit_id: str,
        topic: Optional[str] = None,
        comment: Optional[str] = None,
        mark: Optional[str] = None,
        kind: Optional[str] = None,
        dewey_code: Optional[str] = None,
    ) -> bool:
        """Update fields of an existing unit."""
        existing = self.get_unit(unit_id)
        if not existing:
            return False

        old_topic = existing.topic
        new_topic = topic.strip() if topic is not None else existing.topic
        new_comment = comment.strip() if comment is not None else existing.comment
        new_mark = mark if mark is not None else existing.mark
        new_kind = kind if kind is not None else existing.kind
        new_dewey = dewey_code if dewey_code is not None else existing.dewey_code

        now = self._now()
        cur = self.conn.cursor()
        cur.execute(
            """
            UPDATE units
            SET topic = ?, comment = ?, mark = ?, kind = ?, dewey_code = ?, updated_at = ?
            WHERE id = ?;
            """,
            (new_topic, new_comment, new_mark, new_kind, new_dewey, now, unit_id),
        )
        self._cache_topic(old_topic)
        if new_topic.casefold() != old_topic.casefold():
            self._cache_topic(new_topic)
        return True

    def delete_unit(self, unit_id: str) -> bool:
        """Delete a unit by ID."""
        cur = self.conn.cursor()
        cur.execute("SELECT source_id, topic FROM units WHERE id = ?;", (unit_id,))
        row = cur.fetchone()
        if not row:
            return False
        source_id = row["source_id"]
        topic = row["topic"]

        cur.execute("DELETE FROM units WHERE id = ?;", (unit_id,))

        now = self._now()
        cur.execute("SELECT COUNT(*) as cnt FROM units WHERE source_id = ?;", (source_id,))
        cnt = cur.fetchone()["cnt"]
        cur.execute("UPDATE sources SET unit_count = ?, updated_at = ? WHERE id = ?;", (cnt, now, source_id))
        self._cache_topic(topic)
        return True

    def delete_source(self, uri: str) -> bool:
        """Delete a source and all its cascading units."""
        cur = self.conn.cursor()
        cur.execute("SELECT id FROM sources WHERE uri = ?;", (uri,))
        row = cur.fetchone()
        if not row:
            return False
        source_id = row["id"]

        cur.execute("DELETE FROM sources WHERE id = ?;", (source_id,))
        self._facts = None
        return True

    # --- Ingestion & Sync ---

    def ingest_text(
        self,
        source_text: str,
        uri: str = "inline",
        role: str = "syntax",
        layer: str = "warehouse",
        default_dewey: Optional[str] = None,
    ) -> int:
        """Parse and ingest a Progen document, returning count of units inserted."""
        doc = parse_text(source_text, role=Role(role) if role in Role._value2member_map_ else Role.SYNTAX)
        now = self._now()
        content_hash = hashlib.sha256(source_text.encode("utf-8")).hexdigest()

        with self.transaction() as cur:
            cur.execute("SELECT id, hash FROM sources WHERE uri = ?;", (uri,))
            row = cur.fetchone()
            if row:
                source_id = row["id"]
                if row["hash"] == content_hash:
                    # Idempotent skip if unchanged
                    return len(doc.units)
                cur.execute("DELETE FROM units WHERE source_id = ?;", (source_id,))
                cur.execute(
                    "UPDATE sources SET hash = ?, role = ?, layer = ?, updated_at = ? WHERE id = ?;",
                    (content_hash, role, layer, now, source_id),
                )
            else:
                cur.execute(
                    """
                    INSERT INTO sources (uri, hash, role, layer, unit_count, created_at, updated_at)
                    VALUES (?, ?, ?, ?, 0, ?, ?);
                    """,
                    (uri, content_hash, role, layer, now, now),
                )
                source_id = cur.lastrowid

            asides_by_line: dict[int, list[str]] = {}
            for aside in doc.asides:
                asides_by_line.setdefault(aside.span.line, []).append(aside.text)

            unit_count = 0
            for u in doc.units:
                topic = u.topic or ""
                comment = u.comment or u.text
                if not topic and ":" in comment and u.kind in {"elevated", "test", "admin", "protocol"}:
                    parts = comment.split(":", 1)
                    topic = parts[0].strip()
                    comment = parts[1].strip()

                if not topic and u.kind == "prose":
                    # skip unformatted blank prose if empty
                    continue

                line_no = u.span.line
                unit_id = self.make_unit_id(uri, line_no, topic, comment)
                dewey_code = default_dewey or dewey.classify_text(topic, comment)

                cur.execute(
                    """
                    INSERT INTO units (id, source_id, line_no, kind, mark, topic, comment, dewey_code, parent_unit_id, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL, ?, ?);
                    """,
                    (unit_id, source_id, line_no, u.kind, u.mark or ":", topic, comment, dewey_code, now, now),
                )

                line_asides = asides_by_line.get(line_no, [])
                for a_text in line_asides:
                    cur.execute(
                        "INSERT INTO asides (unit_id, text, line_no) VALUES (?, ?, ?);",
                        (unit_id, a_text, line_no),
                    )

                unit_count += 1

            cur.execute("UPDATE sources SET unit_count = ? WHERE id = ?;", (unit_count, source_id))

        self._facts = None
        return unit_count

    def ingest_file(
        self,
        path: str | Path,
        role: str = "syntax",
        layer: str = "warehouse",
        default_dewey: Optional[str] = None,
    ) -> int:
        """Ingest a Progen markdown file from disk."""
        p = Path(path)
        if not p.is_file():
            raise FileNotFoundError(f"Source file not found: {path}")
        text = p.read_text(encoding="utf-8")
        return self.ingest_text(
            source_text=text,
            uri=str(p.as_posix()),
            role=role,
            layer=layer,
            default_dewey=default_dewey,
        )

    def ingest_directory(
        self,
        dir_path: str | Path,
        pattern: str = "*.md",
        role: str = "syntax",
    ) -> dict[str, int]:
        """Ingest all matching markdown files in a directory tree."""
        root = Path(dir_path)
        results: dict[str, int] = {}
        for file in root.rglob(pattern):
            if file.is_file():
                cnt = self.ingest_file(file, role=role)
                results[str(file.as_posix())] = cnt
        return results

    # --- Query Engine ---

    def query(
        self,
        topic: Optional[str] = None,
        comment: Optional[str] = None,
        dewey_code: Optional[str] = None,
        kind: Optional[str] = None,
        mark: Optional[str] = None,
        source_uri: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[UnitRecord]:
        """Query units using structured filters and full-text search."""
        cur = self.conn.cursor()
        conditions: list[str] = []
        params: list[object] = []

        if search and self._has_fts:
            conditions.append("u.id IN (SELECT unit_id FROM units_fts WHERE units_fts MATCH ?)")
            params.append(search)
        elif search:
            # Fallback if FTS5 not compiled in SQLite
            conditions.append("(u.topic LIKE ? OR u.comment LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%"])

        if topic:
            if "*" in topic or "%" in topic:
                pat = topic.replace("*", "%")
                conditions.append("u.topic LIKE ?")
                params.append(pat)
            else:
                conditions.append("u.topic = ? COLLATE NOCASE")
                params.append(topic.strip())

        if comment:
            conditions.append("u.comment LIKE ?")
            params.append(f"%{comment.strip()}%")

        if dewey_code:
            pat = dewey_code.strip()
            if pat.endswith("*"):
                prefix = pat[:-1]
                conditions.append("u.dewey_code LIKE ?")
                params.append(f"{prefix}%")
            elif "-" in pat:
                parts = pat.split("-", 1)
                conditions.append("CAST(u.dewey_code AS REAL) >= ? AND CAST(u.dewey_code AS REAL) <= ?")
                params.extend([float(parts[0]), float(parts[1])])
            else:
                conditions.append("u.dewey_code = ?")
                params.append(pat)

        if kind:
            conditions.append("u.kind = ?")
            params.append(kind)

        if mark:
            conditions.append("u.mark = ?")
            params.append(mark)

        if source_uri:
            conditions.append("s.uri LIKE ?")
            params.append(f"%{source_uri}%")

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        sql = f"""
            SELECT u.*, s.uri as source_uri, d.slug as dewey_slug
            FROM units u
            JOIN sources s ON u.source_id = s.id
            LEFT JOIN dewey_classes d ON u.dewey_code = d.code
            {where_clause}
            ORDER BY u.dewey_code ASC, u.line_no ASC
            LIMIT ? OFFSET ?;
        """
        params.extend([limit, offset])

        cur.execute(sql, params)
        rows = cur.fetchall()

        unit_ids = [r["id"] for r in rows]
        asides_map: dict[str, list[str]] = {uid: [] for uid in unit_ids}
        if unit_ids:
            placeholders = ",".join("?" for _ in unit_ids)
            cur.execute(
                f"SELECT unit_id, text FROM asides WHERE unit_id IN ({placeholders}) ORDER BY id;",
                unit_ids,
            )
            for a_row in cur.fetchall():
                asides_map[a_row["unit_id"]].append(a_row["text"])

        records: list[UnitRecord] = []
        for r in rows:
            records.append(
                UnitRecord(
                    id=r["id"],
                    source_id=r["source_id"],
                    line_no=r["line_no"],
                    kind=r["kind"],
                    mark=r["mark"],
                    topic=r["topic"],
                    comment=r["comment"],
                    dewey_code=r["dewey_code"],
                    parent_unit_id=r["parent_unit_id"],
                    created_at=r["created_at"],
                    updated_at=r["updated_at"],
                    source_uri=r["source_uri"],
                    dewey_slug=r["dewey_slug"],
                    asides=asides_map.get(r["id"], []),
                )
            )
        return records

    # --- Analytics & Dewey Tooling ---

    def stats(self) -> dict:
        """Return global database counts and metrics."""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) as cnt FROM sources;")
        source_count = cur.fetchone()["cnt"]

        cur.execute("SELECT COUNT(*) as cnt FROM units;")
        unit_count = cur.fetchone()["cnt"]

        cur.execute("SELECT COUNT(*) as cnt FROM asides;")
        aside_count = cur.fetchone()["cnt"]

        cur.execute("SELECT kind, COUNT(*) as cnt FROM units GROUP BY kind;")
        by_kind = {r["kind"]: r["cnt"] for r in cur.fetchall()}

        cur.execute("SELECT dewey_code, COUNT(*) as cnt FROM units WHERE dewey_code IS NOT NULL GROUP BY dewey_code;")
        by_dewey = {r["dewey_code"]: r["cnt"] for r in cur.fetchall()}

        cur.execute("SELECT COUNT(*) as cnt FROM units WHERE dewey_code IS NULL;")
        unclassified = cur.fetchone()["cnt"]

        return {
            "source_count": source_count,
            "unit_count": unit_count,
            "aside_count": aside_count,
            "kinds": by_kind,
            "dewey_classes": by_dewey,
            "unclassified_units": unclassified,
        }

    def dewey_tree(self) -> list[dict]:
        """Return hierarchical Dewey tree with populated unit counts."""
        cur = self.conn.cursor()
        cur.execute("SELECT dewey_code, COUNT(*) as cnt FROM units WHERE dewey_code IS NOT NULL GROUP BY dewey_code;")
        counts = {r["dewey_code"]: r["cnt"] for r in cur.fetchall()}
        return dewey.build_tree(counts)

    def classify_and_tag(self, force: bool = False) -> int:
        """Heuristically assign Dewey codes to unclassified (or all) units."""
        cur = self.conn.cursor()
        sql = "SELECT id, topic, comment, dewey_code FROM units"
        if not force:
            sql += " WHERE dewey_code IS NULL"
        cur.execute(sql)
        rows = cur.fetchall()

        updated = 0
        with self.transaction() as tx:
            for r in rows:
                code = dewey.classify_text(r["topic"], r["comment"])
                if code and code != r["dewey_code"]:
                    tx.execute("UPDATE units SET dewey_code = ? WHERE id = ?;", (code, r["id"]))
                    if self._has_fts:
                        tx.execute("UPDATE units_fts SET dewey_code = ? WHERE unit_id = ?;", (code, r["id"]))
                    updated += 1
        return updated

    # --- Export ---

    def export_markdown(
        self,
        dewey_code: Optional[str] = None,
        topic: Optional[str] = None,
        source_uri: Optional[str] = None,
    ) -> str:
        """Export database units as canonical, clean Progen markdown."""
        units = self.query(dewey_code=dewey_code, topic=topic, source_uri=source_uri, limit=10000)
        lines: list[str] = []
        for u in units:
            lines.append(u.to_markdown())
            lines.append("")  # Blank line between units per SPEC layout law
        return "\n".join(lines).strip() + "\n"

    def export_jsonl(
        self,
        dewey_code: Optional[str] = None,
        source_uri: Optional[str] = None,
    ) -> str:
        """Export database units as JSON Lines."""
        units = self.query(dewey_code=dewey_code, source_uri=source_uri, limit=10000)
        out = []
        for u in units:
            payload = {
                "id": u.id,
                "dewey": u.dewey_code,
                "dewey_slug": u.dewey_slug,
                "kind": u.kind,
                "mark": u.mark,
                "topic": u.topic,
                "comment": u.comment,
                "asides": u.asides,
                "source": u.source_uri,
                "line": u.line_no,
            }
            out.append(json.dumps(payload, ensure_ascii=False))
        return "\n".join(out) + ("\n" if out else "")
