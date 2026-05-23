import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, String, Text, func, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    target_type: Mapped[str] = mapped_column(String(64), nullable=False)
    target_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    action: Mapped[str] = mapped_column(String(32), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(16), nullable=False)
    before_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    after_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    requested_by: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
