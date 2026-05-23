from sqlalchemy.orm import Session

from app.agent.models import AgentMessage, AgentSession
from app.approvals.models import ApprovalRequest
from app.audit.models import AuditLog
from app.customers.models import Customer, CustomerAddress, CustomerContact
from app.db import Base, engine
from app.seed import seed_customers


def init_db(*, with_seed: bool = True) -> None:
    Base.metadata.create_all(bind=engine)
    if not with_seed:
        return
    with Session(engine) as session:
        seed_customers(session)

