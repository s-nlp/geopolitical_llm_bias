import os
import random
import sqlite3
from typing import Any, Dict, Optional, Tuple, List


def _get_db_path() -> str:

    return os.path.abspath(os.path.join(os.path.dirname(__file__), "bot.db"))


def _connect() -> sqlite3.Connection:

    conn = sqlite3.connect(_get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


OCCUPATION_ENUM = [
    "student",
    "academic_research",
    "engineer_tech",
    "business_finance",
    "government_public",
    "media_journalism",
    "healthcare",
    "education_teacher",
    "service_trade",
    "unemployed",
    "retired",
    "other",
    "prefer_not_to_say",
]

EDUCATION_ENUM = [
    "high_school_or_less",
    "bachelor",
    "master",
    "doctorate",
    "professional_degree",
    "other",
    "prefer_not_to_say",
]


def init_db() -> None:

    conn = _connect()
    try:
        occ_check = ",".join([f"'{v}'" for v in OCCUPATION_ENUM])
        edu_check = ",".join([f"'{v}'" for v in EDUCATION_ENUM])

        conn.executescript(
            f"""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                nationality TEXT,
                age INTEGER,
                occupation_type TEXT CHECK(occupation_type IN ({occ_check})),
                education_level TEXT CHECK(education_level IN ({edu_check})),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_index INTEGER,
                seed_name TEXT,
                topic_name TEXT,
                topic_url TEXT,
                topic_description TEXT,
                years TEXT,
                country_a TEXT,
                country_b TEXT
            );

            CREATE TABLE IF NOT EXISTS viewpoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                viewpoint_type TEXT CHECK(viewpoint_type IN ('neutral','propaganda')) NOT NULL,
                propaganda_country TEXT,
                viewpoint_index INTEGER,
                language TEXT,
                viewpoint_text TEXT NOT NULL,
                FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS annotations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_telegram_id INTEGER NOT NULL,
                viewpoint_id INTEGER NOT NULL,
                label INTEGER CHECK(label BETWEEN 1 AND 5) NOT NULL,
                label_text TEXT NOT NULL,
                label_language TEXT DEFAULT 'en',
                selected_country TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_telegram_id) REFERENCES users(telegram_id) ON DELETE CASCADE,
                FOREIGN KEY (viewpoint_id) REFERENCES viewpoints(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_annotations_user ON annotations(user_telegram_id);
            CREATE INDEX IF NOT EXISTS idx_annotations_viewpoint ON annotations(viewpoint_id);
            """
        )
        conn.commit()
    finally:
        conn.close()


def upsert_user(
    telegram_id: int,
    nationality: str,
    age: int,
    occupation_type: str,
    education_level: str,
) -> None:

    conn = _connect()
    try:
        conn.execute(
            """
            INSERT INTO users (
                telegram_id,
                nationality,
                age,
                occupation_type,
                education_level,
                created_at,
                updated_at
            ) VALUES (
                ?,?,?,?,?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            )
            ON CONFLICT(telegram_id) DO UPDATE SET
                nationality=excluded.nationality,
                age=excluded.age,
                occupation_type=excluded.occupation_type,
                education_level=excluded.education_level,
                updated_at=CURRENT_TIMESTAMP
            ;
            """,
            (
                telegram_id,
                nationality,
                age,
                occupation_type,
                education_level,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def insert_annotation(
    user_telegram_id: int,
    viewpoint_id: int,
    label: int,
    label_text: str,
    label_language: str = "en",
    selected_country: str = "Neutral",
) -> None:

    conn = _connect()
    try:
        try:
            conn.execute(
                """
                INSERT INTO annotations (
                    user_telegram_id,
                    viewpoint_id,
                    label,
                    label_text,
                    label_language,
                    selected_country
                ) VALUES (?,?,?,?,?,?);
                """,
                (
                    user_telegram_id,
                    viewpoint_id,
                    label,
                    label_text,
                    label_language,
                    selected_country,
                ),
            )
        except sqlite3.OperationalError:
            # Backward compatibility if column missing in older DBs
            conn.execute(
                """
                INSERT INTO annotations (
                    user_telegram_id,
                    viewpoint_id,
                    label,
                    label_text
                ) VALUES (?,?,?,?);
                """,
                (
                    user_telegram_id,
                    viewpoint_id,
                    label,
                    label_text,
                ),
            )
        conn.commit()
    finally:
        conn.close()


# Attempt to migrate existing DBs to include label_language on annotations
def _migrate_add_label_language_column() -> None:

    conn = _connect()
    try:
        cur = conn.execute("PRAGMA table_info(annotations);")
        cols = [row[1] for row in cur.fetchall()]
        if "label_language" not in cols:
            try:
                conn.execute("ALTER TABLE annotations ADD COLUMN label_language TEXT DEFAULT 'en';")
                conn.commit()
            except sqlite3.OperationalError:
                pass
        if "selected_country" not in cols:
            try:
                conn.execute("ALTER TABLE annotations ADD COLUMN selected_country TEXT;")
                conn.commit()
            except sqlite3.OperationalError:
                pass
    finally:
        conn.close()


# Run lightweight migration on module import
try:
    _migrate_add_label_language_column()
except Exception:
    pass


def clear_dataset() -> None:

    conn = _connect()
    try:
        conn.execute("DELETE FROM annotations;")
        conn.execute("DELETE FROM viewpoints;")
        conn.execute("DELETE FROM events;")
        conn.commit()
    finally:
        conn.close()


def insert_event(
    event_index: Optional[int],
    seed_name: Optional[str],
    topic_name: Optional[str],
    topic_url: Optional[str],
    topic_description: Optional[str],
    years: Optional[str],
    country_a: Optional[str],
    country_b: Optional[str],
) -> int:

    conn = _connect()
    try:
        cur = conn.execute(
            """
            INSERT INTO events (
                event_index, seed_name, topic_name, topic_url, topic_description, years, country_a, country_b
            ) VALUES (?,?,?,?,?,?,?,?);
            """,
            (
                event_index,
                seed_name,
                topic_name,
                topic_url,
                topic_description,
                years,
                country_a,
                country_b,
            ),
        )
        event_id = cur.lastrowid
        conn.commit()
        return int(event_id)
    finally:
        conn.close()


def insert_viewpoint(
    event_id: int,
    viewpoint_type: str,
    viewpoint_text: str,
    propaganda_country: Optional[str] = None,
    viewpoint_index: Optional[int] = None,
    language: Optional[str] = None,
) -> int:

    conn = _connect()
    try:
        cur = conn.execute(
            """
            INSERT INTO viewpoints (
                event_id, viewpoint_type, propaganda_country, viewpoint_index, language, viewpoint_text
            ) VALUES (?,?,?,?,?,?);
            """,
            (
                event_id,
                viewpoint_type,
                propaganda_country,
                viewpoint_index,
                language,
                viewpoint_text,
            ),
        )
        vp_id = cur.lastrowid
        conn.commit()
        return int(vp_id)
    finally:
        conn.close()


def get_random_viewpoint_with_event() -> Optional[Dict[str, Any]]:

    conn = _connect()
    try:
        cur = conn.execute(
            """
            SELECT v.id AS viewpoint_id,
                   v.viewpoint_type,
                   v.propaganda_country,
                   v.viewpoint_text,
                   e.id AS event_id,
                   e.seed_name,
                   e.topic_name,
                   e.topic_url,
                   e.topic_description,
                   e.years,
                   e.country_a,
                   e.country_b
            FROM viewpoints v
            JOIN events e ON e.id = v.event_id
            ORDER BY RANDOM()
            LIMIT 1;
            """
        )
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_weighted_viewpoint_with_event(priority_min_count_probability: float = 0.9) -> Optional[Dict[str, Any]]:

    conn = _connect()
    try:
        cur = conn.execute(
            """
            SELECT v.id AS viewpoint_id,
                   v.viewpoint_type,
                   v.propaganda_country,
                   v.viewpoint_text,
                   e.id AS event_id,
                   e.seed_name,
                   e.topic_name,
                   e.topic_url,
                   e.topic_description,
                   e.years,
                   e.country_a,
                   e.country_b,
                   COALESCE(a.cnt, 0) AS annotations_count
            FROM viewpoints v
            JOIN events e ON e.id = v.event_id
            LEFT JOIN (
                SELECT viewpoint_id, COUNT(*) AS cnt
                FROM annotations
                GROUP BY viewpoint_id
            ) a ON a.viewpoint_id = v.id;
            """
        )
        rows = [dict(r) for r in cur.fetchall()]
        if not rows:
            return None

        # Partition by minimum annotation count
        min_count = min(r.get("annotations_count", 0) for r in rows)
        min_rows: List[Dict[str, Any]] = [r for r in rows if r.get("annotations_count", 0) == min_count]
        other_rows: List[Dict[str, Any]] = [r for r in rows if r.get("annotations_count", 0) != min_count]

        # If all equal counts, choose uniformly at random
        if not other_rows:
            return random.choice(min_rows)

        # With given probability, choose from least-labeled set; otherwise from others
        if random.random() < priority_min_count_probability:
            return random.choice(min_rows)
        return random.choice(other_rows)
    finally:
        conn.close()



