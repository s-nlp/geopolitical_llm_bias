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
                preferred_language TEXT DEFAULT 'en' CHECK(preferred_language IN ('ar', 'en', 'fr', 'he', 'ru', 'zh', 'de')),
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
                country_b TEXT,
                language TEXT DEFAULT 'en' CHECK(language IN ('ar', 'en', 'fr', 'he', 'ru', 'zh', 'de'))
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
                step_1_choice TEXT CHECK(step_1_choice IN ('neutral', 'biased', 'error')) NOT NULL,
                step_2_choice TEXT CHECK(step_2_choice IN ('skip', 'dont_know') OR step_2_choice IS NULL OR LENGTH(step_2_choice) > 0),
                has_error BOOLEAN DEFAULT FALSE,
                error_description TEXT,
                completed_step INTEGER CHECK(completed_step IN (1, 2)) NOT NULL,
                annotation_language TEXT DEFAULT 'en',
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
    preferred_language: str = "en",
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
                preferred_language,
                created_at,
                updated_at
            ) VALUES (
                ?,?,?,?,?,?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            )
            ON CONFLICT(telegram_id) DO UPDATE SET
                nationality=excluded.nationality,
                age=excluded.age,
                occupation_type=excluded.occupation_type,
                education_level=excluded.education_level,
                preferred_language=excluded.preferred_language,
                updated_at=CURRENT_TIMESTAMP
            ;
            """,
            (
                telegram_id,
                nationality,
                age,
                occupation_type,
                education_level,
                preferred_language,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def get_user(telegram_id: int) -> Optional[Dict[str, Any]]:

    conn = _connect()
    try:
        cur = conn.execute(
            """
            SELECT telegram_id, nationality, age, occupation_type, education_level, preferred_language
            FROM users
            WHERE telegram_id = ?;
            """,
            (telegram_id,)
        )
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def insert_annotation(
    user_telegram_id: int,
    viewpoint_id: int,
    step_1_choice: str,
    step_2_choice: str = None,
    has_error: bool = False,
    error_description: str = None,
    completed_step: int = 1,
    annotation_language: str = "en",
) -> None:

    conn = _connect()
    try:
        conn.execute(
            """
            INSERT INTO annotations (
                user_telegram_id,
                viewpoint_id,
                step_1_choice,
                step_2_choice,
                has_error,
                error_description,
                completed_step,
                annotation_language
            ) VALUES (?,?,?,?,?,?,?,?);
            """,
            (
                user_telegram_id,
                viewpoint_id,
                step_1_choice,
                step_2_choice,
                has_error,
                error_description,
                completed_step,
                annotation_language,
            ),
        )
        conn.commit()
    finally:
        conn.close()


# No migrations needed - database will be recreated with new schema


def get_user_annotation_count(telegram_id: int) -> int:
    """Get the count of annotations made by a user."""
    
    conn = _connect()
    try:
        cursor = conn.execute(
            "SELECT COUNT(*) FROM annotations WHERE user_telegram_id = ?",
            (telegram_id,)
        )
        row = cursor.fetchone()
        return row[0] if row else 0
    finally:
        conn.close()


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
    language: Optional[str] = "en",
) -> int:

    conn = _connect()
    try:
        cur = conn.execute(
            """
            INSERT INTO events (
                event_index, seed_name, topic_name, topic_url, topic_description, years, country_a, country_b, language
            ) VALUES (?,?,?,?,?,?,?,?,?);
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
                language,
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


def get_weighted_viewpoint_with_event(priority_min_count_probability: float = 0.9, language: str = "en") -> Optional[Dict[str, Any]]:

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
                   e.language AS event_language,
                   COALESCE(a.cnt, 0) AS annotations_count
            FROM viewpoints v
            JOIN events e ON e.id = v.event_id
            LEFT JOIN (
                SELECT viewpoint_id, COUNT(*) AS cnt
                FROM annotations
                GROUP BY viewpoint_id
            ) a ON a.viewpoint_id = v.id
            WHERE e.language = ?;
            """,
            (language,)
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


def get_admin_user_statistics() -> List[Dict[str, Any]]:
    """Get user statistics for admin dashboard, sorted by annotation count."""
    
    conn = _connect()
    try:
        cur = conn.execute(
            """
            SELECT u.telegram_id,
                   u.nationality,
                   u.age,
                   u.occupation_type,
                   u.education_level,
                   u.preferred_language,
                   COALESCE(total_annotations.count, 0) AS total_annotations,
                   COALESCE(error_annotations.count, 0) AS error_annotations
            FROM users u
            LEFT JOIN (
                SELECT user_telegram_id, COUNT(*) AS count
                FROM annotations
                GROUP BY user_telegram_id
            ) total_annotations ON total_annotations.user_telegram_id = u.telegram_id
            LEFT JOIN (
                SELECT user_telegram_id, COUNT(*) AS count
                FROM annotations
                WHERE has_error = 1
                GROUP BY user_telegram_id
            ) error_annotations ON error_annotations.user_telegram_id = u.telegram_id
            ORDER BY total_annotations DESC, u.telegram_id;
            """
        )
        rows = [dict(r) for r in cur.fetchall()]
        return rows
    finally:
        conn.close()


def get_general_statistics() -> Dict[str, int]:
    """Get general statistics about annotations and errors."""
    
    conn = _connect()
    try:
        cur = conn.execute(
            """
            SELECT 
                COUNT(*) AS total_annotations,
                SUM(CASE WHEN has_error = 1 THEN 1 ELSE 0 END) AS total_errors,
                COUNT(DISTINCT user_telegram_id) AS total_users
            FROM annotations;
            """
        )
        row = cur.fetchone()
        return dict(row) if row else {"total_annotations": 0, "total_errors": 0, "total_users": 0}
    finally:
        conn.close()

