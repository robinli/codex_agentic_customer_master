from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ApprovalRejectRequest(BaseModel):
    comment: str


class ApprovalSummary(BaseModel):
    id: str
    target_type: str
    target_id: str
    action: str
    risk_level: str
    status: str
    reason: str
    requested_by: str
    reviewed_by: str | None
    reviewed_at: datetime | None
    created_at: datetime
    before_data: dict[str, Any] | None
    after_data: dict[str, Any] | None

    model_config = {"from_attributes": True}

