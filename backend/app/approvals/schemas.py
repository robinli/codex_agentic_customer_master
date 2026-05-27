from datetime import datetime
from typing import Any
import uuid

from pydantic import BaseModel


class ApprovalRejectRequest(BaseModel):
    comment: str


class ApprovalSummary(BaseModel):
    id: uuid.UUID
    target_type: str
    target_id: uuid.UUID
    action: str
    risk_level: str
    status: str
    reason: str
    requested_by: uuid.UUID
    reviewed_by: uuid.UUID | None
    reviewed_at: datetime | None
    created_at: datetime
    before_data: dict[str, Any] | None
    after_data: dict[str, Any] | None

    model_config = {"from_attributes": True}
