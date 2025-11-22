from pathlib import Path
import sqlite3
from typing import Optional, List, Dict, Any


# Database file will be placed in the repository root as `viralytics.db`
DB_PATH = Path(__file__).resolve().parent.parent / "viralytics.db"


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Return a sqlite3 connection to the viralytics database.

    The connection is created with check_same_thread=False to allow usage
    from different threads (suitable for simple FastAPI usage).
    """
    path = db_path or DB_PATH
    _ensure_parent(path)
    conn = sqlite3.connect(str(path), check_same_thread=False)
    return conn


def init_db(db_path: Optional[Path] = None) -> None:
    """Initialize the database and create the `analyses` table if it does not exist.

    Schema:
      - id INTEGER PRIMARY KEY AUTOINCREMENT
      - created_at TEXT DEFAULT (datetime('now'))
      - video_filename TEXT
      - score REAL
      - label TEXT
      - explanation TEXT
    """
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT DEFAULT (datetime('now')),
            video_filename TEXT,
            score REAL,
            label TEXT,
            explanation TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def insert_analysis(
    video_filename: str,
    score: Optional[float] = None,
    label: Optional[str] = None,
    explanation: Optional[str] = None,
    db_path: Optional[Path] = None,
) -> int:
    """Insert a new analysis row into the `analyses` table.

    Returns the inserted row id.
    """
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO analyses (video_filename, score, label, explanation) VALUES (?,?,?,?)",
        (video_filename, score, label, explanation),
    )
    conn.commit()
    rowid = cur.lastrowid
    conn.close()
    return rowid


def get_last_analyses(limit: int = 10, db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Return the last `limit` analyses ordered by created_at DESC.

    Each row is returned as a dict with keys matching the table columns.
    """
    if limit is None or limit <= 0:
        limit = 10

    conn = get_connection(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT id, created_at, video_filename, score, label, explanation "
        "FROM analyses "
        "ORDER BY created_at DESC, id DESC "
        "LIMIT ?",
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()

    results: List[Dict[str, Any]] = []
    for r in rows:
        results.append({k: r[k] for k in r.keys()})
    return results


def ensure_db():
    """Convenience wrapper to initialize the default DB file."""
    init_db()
