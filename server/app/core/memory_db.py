import sqlite3
from typing import Literal, Optional, Dict, Any
from fastapi import Request


class SQLiteKVStore:
    def __init__(self, memory: bool = True, db_path: str = "data.db"):
        if memory:
            self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        else:
            self.conn = sqlite3.connect(db_path, check_same_thread=False)

        self.conn.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS kv_store (
            id TEXT PRIMARY KEY,
            status VARCHAR(10),
            desc TEXT NULL
        );
        """
        self.conn.execute(query)
        self.conn.commit()

    def set(
        self, id: str, status: Literal["success", "failed"], desc: Optional[str]
    ) -> None:
        query = """
        INSERT INTO kv_store (id, status, desc)
        VALUES (?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            status=excluded.status,
            desc=excluded.desc;
        """
        self.conn.execute(query, (id, status, desc))
        self.conn.commit()

    def get(self, id: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM kv_store WHERE id = ?"
        cur = self.conn.execute(query, (id,))
        row = cur.fetchone()
        if row:
            return {
                "id": row["id"],
                "status": row["status"],
                "desc": row["desc"],
            }
        return None

    def delete(self, id: str) -> None:
        query = "DELETE FROM kv_store WHERE id = ?"
        self.conn.execute(query, (id,))
        self.conn.commit()

    def all(self) -> list[Dict[str, Any]]:
        query = "SELECT * FROM kv_store"
        cur = self.conn.execute(query)
        rows = cur.fetchall()
        return [
            {"id": row["id"], "status": row["status"], "desc": row["desc"]}
            for row in rows
        ]


# Dependency to inject SQLiteKVStore
def get_memory_db(request: Request) -> SQLiteKVStore:
    return request.app.state.memory_db


all = ["SQLiteKVStore", "get_memory_db"]
