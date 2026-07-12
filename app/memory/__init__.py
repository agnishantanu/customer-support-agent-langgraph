import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.utils.config import settings


def _get_db_path(db_path: Optional[str] = None) -> Path:
    path = Path(db_path or settings.SQLITE_DB_PATH)
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _connect(db_path: Optional[str] = None) -> sqlite3.Connection:
    db_path = _get_db_path(db_path)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            created_at TEXT NOT NULL,
            query TEXT NOT NULL,
            response TEXT NOT NULL,
            intent TEXT NOT NULL,
            department TEXT NOT NULL,
            metadata TEXT NOT NULL
        )
        """
    )
    connection.commit()
    return connection


def save_conversation(
    conversation_id: str,
    customer_name: str,
    query: str,
    response: str,
    intent: str,
    department: str,
    metadata: Optional[Dict[str, Any]] = None,
    db_path: Optional[str] = None,
) -> Dict[str, Any]:
    connection = _connect(db_path)
    created_at = datetime.utcnow().isoformat()
    payload = json.dumps(metadata or {})
    cursor = connection.execute(
        """
        INSERT INTO conversations (
            conversation_id, customer_name, created_at, query, response, intent, department, metadata
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (conversation_id, customer_name, created_at, query, response, intent, department, payload),
    )
    connection.commit()
    connection.close()
    return {
        "id": cursor.lastrowid,
        "conversation_id": conversation_id,
        "customer_name": customer_name,
        "created_at": created_at,
        "query": query,
        "response": response,
        "intent": intent,
        "department": department,
        "metadata": metadata or {},
    }


def load_history(
    conversation_id: Optional[str] = None,
    customer_name: Optional[str] = None,
    limit: int = 10,
    db_path: Optional[str] = None,
) -> List[Dict[str, Any]]:
    connection = _connect(db_path)
    if conversation_id:
        rows = connection.execute(
            """
            SELECT * FROM conversations
            WHERE conversation_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (conversation_id, limit),
        )
    elif customer_name:
        rows = connection.execute(
            """
            SELECT * FROM conversations
            WHERE customer_name = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (customer_name, limit),
        )
    else:
        rows = connection.execute(
            """
            SELECT * FROM conversations
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )

    history = []
    for row in rows.fetchall():
        history.append(
            {
                "id": row["id"],
                "conversation_id": row["conversation_id"],
                "customer_name": row["customer_name"],
                "created_at": row["created_at"],
                "query": row["query"],
                "response": row["response"],
                "intent": row["intent"],
                "department": row["department"],
                "metadata": json.loads(row["metadata"] or "{}"),
            }
        )
    connection.close()
    return history


def retrieve_previous_issue(
    customer_name: str,
    db_path: Optional[str] = None,
) -> str:
    history = load_history(customer_name=customer_name, limit=5, db_path=db_path)
    if not history:
        return "No previous support issue found."

    latest = history[0]
    return (
        f"Your most recent issue was: '{latest['query']}'. "
        f"Support handled it under {latest['department']} with the intent {latest['intent']}."
    )


__all__ = [
    "save_conversation",
    "load_history",
    "retrieve_previous_issue",
]
