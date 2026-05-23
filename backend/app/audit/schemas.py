from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AuditLogRead(BaseModel):
    id: str
    actor_id: str | None
    actor_type: str
    action: str
    target_type: str
    target_id: str | None
    before_data: dict[str, Any] | None
    after_data: dict[str, Any] | None
    metadata_json: dict[str, Any] | None
    created_at: datetime

    model_config = {"from_attributes": True}
