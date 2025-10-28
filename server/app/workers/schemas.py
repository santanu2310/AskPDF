from typing import Optional, Literal
from pydantic import BaseModel, Field, model_validator


class TaskUpdate(BaseModel):
    doc_id: str = Field(..., description="Unique document identifier")
    status: Literal["success", "failed"] = Field(..., description="Processing status")
    reason: Optional[str] = Field(
        None, description="Failure reason if status is failed"
    )

    @model_validator(mode="after")
    def validate_reason(cls, values):
        status, reason = values.status, values.reason
        if status == "failed" and not reason:
            raise ValueError("reason is required when status is 'failed'")
        return values
