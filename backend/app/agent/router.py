from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.agent.schemas import AgentMessageCreate, AgentMessageRead, AgentResponse, AgentSessionCreate, AgentSessionRead
from app.agent.service import create_session, handle_message, list_messages, list_sessions
from app.auth.dependencies import get_current_user
from app.auth.schemas import CurrentUser
from app.db import get_db

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/sessions", response_model=AgentSessionRead)
def create_agent_session(
    payload: AgentSessionCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> AgentSessionRead:
    return create_session(db, user=current_user, title=payload.title)


@router.get("/sessions", response_model=list[AgentSessionRead])
def get_agent_sessions(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[AgentSessionRead]:
    return list_sessions(db, user=current_user)


@router.get("/sessions/{session_id}/messages", response_model=list[AgentMessageRead])
def get_agent_messages(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[AgentMessageRead]:
    return list_messages(db, session_id=session_id, user=current_user)


@router.post("/sessions/{session_id}/messages", response_model=AgentResponse)
def send_agent_message(
    session_id: str,
    payload: AgentMessageCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> AgentResponse:
    return handle_message(db, session_id=session_id, message=payload.message, user=current_user)

