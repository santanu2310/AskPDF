import logging
import json
from typing import Any
from app.core.memory_db import SQLiteKVStore
from app.core.exceptions import FileStateUpdateException

from .schemas import TaskUpdate

logger = logging.getLogger(__name__)


async def update_file_state(payload: str, memory_db: SQLiteKVStore) -> dict[str, Any]:
    try:
        logger.critical(f"{payload}")
        data = json.loads(payload)
        data: TaskUpdate = TaskUpdate.model_validate(data)
        memory_db.set(id=data.doc_id, status=data.status, desc=data.reason)

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Error updating file status: {str(e)}")
        raise FileStateUpdateException()
