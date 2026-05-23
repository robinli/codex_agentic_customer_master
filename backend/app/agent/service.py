import re
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agent.graph import invoke_agent_graph
from app.agent.models import AgentMessage, AgentSession
from app.agent.schemas import AgentResponse, ToolCallResult
from app.agent.tools import customer_create_tool, customer_disable_request_tool, customer_search_tool, customer_update_tool
from app.auth.schemas import CurrentUser
from app.common.errors import bad_request, not_found

CONFIRM_WORDS = {"確認", "確定", "同意", "送出審核", "送出", "approve", "yes", "ok"}


def create_session(db: Session, *, user: CurrentUser, title: str | None) -> AgentSession:
    session = AgentSession(user_id=uuid.UUID(user.id), title=title or "New session")
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def list_sessions(db: Session, *, user: CurrentUser) -> list[AgentSession]:
    stmt = select(AgentSession).where(AgentSession.user_id == uuid.UUID(user.id)).order_by(AgentSession.updated_at.desc())
    return list(db.scalars(stmt))


def list_messages(db: Session, *, session_id: str, user: CurrentUser) -> list[AgentMessage]:
    session = db.get(AgentSession, uuid.UUID(session_id))
    if not session or str(session.user_id) != user.id:
        raise not_found("Session not found")
    stmt = select(AgentMessage).where(AgentMessage.session_id == uuid.UUID(session_id)).order_by(AgentMessage.created_at.asc())
    return list(db.scalars(stmt))


def _store_message(
    db: Session,
    *,
    session_id: str,
    role: str,
    content: str,
    tool_name: str | None = None,
    tool_args: dict | None = None,
    tool_result: dict | None = None,
) -> AgentMessage:
    message = AgentMessage(
        session_id=uuid.UUID(session_id),
        role=role,
        content=content,
        tool_name=tool_name,
        tool_args=tool_args,
        tool_result=tool_result,
    )
    db.add(message)
    db.flush()
    return message


def _extract_tax_id(message: str) -> str | None:
    match = re.search(r"\b\d{8}\b", message)
    return match.group(0) if match else None


def _extract_payment_terms(message: str) -> str | None:
    match = re.search(r"(月結\s*\d+\s*天|月結\d+天)", message)
    if not match:
        return None
    return re.sub(r"\s+", " ", match.group(1)).strip()


def _extract_phone(message: str) -> str | None:
    match = re.search(r"改成\s*([0-9\-]+)", message)
    return match.group(1) if match else None


def _extract_reason(message: str) -> str | None:
    for pattern in [r"原因是[:：]?\s*(.+)$", r"因為[:：]?\s*(.+)$", r"理由是[:：]?\s*(.+)$"]:
        match = re.search(pattern, message)
        if match:
            return match.group(1).strip(" 。")
    return None


def _extract_customer_name_for_create(message: str) -> str | None:
    match = re.search(r"新增一筆客戶[:：]?\s*([^，,]+)", message)
    return match.group(1).strip() if match else None


def _normalize_search_query(message: str) -> str | None:
    text = re.sub(r"(幫我|請|查詢|搜尋|找出|客戶|資料|統編|的|電話|付款條件|停用)", " ", message)
    text = re.sub(r"\s+", " ", text).strip(" ，,。")
    return text or None


def _store_assistant_response(
    db: Session,
    *,
    session_id: str,
    message: str,
    tool_calls: list[ToolCallResult],
    data: dict[str, Any] | None = None,
) -> AgentResponse:
    _store_message(db, session_id=session_id, role="assistant", content=message, tool_result={"tool_calls": [call.model_dump() for call in tool_calls], "data": data})
    db.commit()
    return AgentResponse(message=message, tool_calls=tool_calls, data=data)


def _find_customer_candidates(db: Session, message: str) -> dict[str, Any]:
    tax_id = _extract_tax_id(message)
    query = None if tax_id else _normalize_search_query(message)
    return customer_search_tool(db, query=query, tax_id=tax_id, status=None)


def _get_active_pending_action(db: Session, *, session_id: str) -> AgentMessage | None:
    stmt = (
        select(AgentMessage)
        .where(
            AgentMessage.session_id == uuid.UUID(session_id),
            AgentMessage.role == "system",
            AgentMessage.tool_name == "pending_action",
        )
        .order_by(AgentMessage.created_at.desc())
    )
    for message in db.scalars(stmt):
        if (message.tool_result or {}).get("status") == "pending":
            return message
        return None
    return None


def _is_confirmation(message: str) -> bool:
    lowered = message.lower().strip()
    return lowered in CONFIRM_WORDS or any(word in message for word in CONFIRM_WORDS)


def _mark_pending_action_resolved(db: Session, *, session_id: str, pending: AgentMessage) -> None:
    _store_message(
        db,
        session_id=session_id,
        role="system",
        content="Pending action resolved",
        tool_name="pending_action",
        tool_args=pending.tool_args,
        tool_result={"status": "resolved"},
    )


def _queue_pending_action(
    db: Session,
    *,
    session_id: str,
    action_type: str,
    payload: dict[str, Any],
    preview_message: str,
) -> None:
    _store_message(
        db,
        session_id=session_id,
        role="system",
        content=preview_message,
        tool_name="pending_action",
        tool_args={"action_type": action_type, **payload},
        tool_result={"status": "pending"},
    )


def _execute_pending_action(
    db: Session,
    *,
    session_id: str,
    pending: AgentMessage,
    user: CurrentUser,
) -> AgentResponse:
    action = pending.tool_args or {}
    tool_calls: list[ToolCallResult] = []

    if action["action_type"] == "customer.update_sensitive":
        result = customer_update_tool(
            db,
            customer_id=action["customer_id"],
            payload=action["payload"],
            user=user,
            reason=action.get("reason"),
        )
        tool_calls.append(
            ToolCallResult(
                tool_name="customer.update",
                status="success",
                input=action["payload"],
                output=result,
            )
        )
        _store_message(
            db,
            session_id=session_id,
            role="tool",
            content="Sensitive customer update request submitted",
            tool_name="customer.update",
            tool_args=action["payload"],
            tool_result=result,
        )
        _mark_pending_action_resolved(db, session_id=session_id, pending=pending)
        return _store_assistant_response(
            db,
            session_id=session_id,
            message="已建立審核申請，不會直接修改敏感資料。",
            tool_calls=tool_calls,
            data=result,
        )

    if action["action_type"] == "customer.disable":
        result = customer_disable_request_tool(db, customer_id=action["customer_id"], reason=action["reason"], user=user)
        tool_calls.append(
            ToolCallResult(
                tool_name="customer.disable_request",
                status="success",
                input={"reason": action["reason"]},
                output=result,
            )
        )
        _store_message(
            db,
            session_id=session_id,
            role="tool",
            content="Customer disable request submitted",
            tool_name="customer.disable_request",
            tool_args={"reason": action["reason"]},
            tool_result=result,
        )
        _mark_pending_action_resolved(db, session_id=session_id, pending=pending)
        return _store_assistant_response(
            db,
            session_id=session_id,
            message="已建立停用審核申請。",
            tool_calls=tool_calls,
            data=result,
        )

    raise bad_request("Unsupported pending action")


def _handle_search(db: Session, *, session_id: str, message: str) -> AgentResponse:
    payload = {
        "query": _normalize_search_query(message),
        "tax_id": _extract_tax_id(message),
    }
    result = customer_search_tool(db, **payload, status=None)
    tool_call = ToolCallResult(tool_name="customer.search", status="success", input=payload, output=result)
    _store_message(db, session_id=session_id, role="tool", content="Customer search executed", tool_name="customer.search", tool_args=payload, tool_result=result)

    if len(result["items"]) > 1:
        names = "、".join(item["customer_name"] for item in result["items"][:5])
        return _store_assistant_response(
            db,
            session_id=session_id,
            message=f"查到多筆客戶：{names}。請提供更明確的客戶名稱或統編。",
            tool_calls=[tool_call],
            data=result,
        )

    if len(result["items"]) == 0:
        return _store_assistant_response(
            db,
            session_id=session_id,
            message="查無符合的客戶資料，請提供更明確的客戶名稱或統編。",
            tool_calls=[tool_call],
            data=result,
        )

    item = result["items"][0]
    return _store_assistant_response(
        db,
        session_id=session_id,
        message=f"找到 1 筆客戶資料：{item['customer_name']}。",
        tool_calls=[tool_call],
        data=result,
    )


def _handle_create(db: Session, *, session_id: str, message: str, user: CurrentUser) -> AgentResponse:
    customer_name = _extract_customer_name_for_create(message)
    tax_id = _extract_tax_id(message)
    payment_terms = _extract_payment_terms(message)
    missing_fields = []
    if not customer_name:
        missing_fields.append("customer_name")
    if not tax_id:
        missing_fields.append("tax_id")
    if missing_fields:
        return _store_assistant_response(
            db,
            session_id=session_id,
            message=f"新增客戶前還缺必要欄位：{', '.join(missing_fields)}。請補充後再送出。",
            tool_calls=[],
            data={"missing_fields": missing_fields},
        )

    payload = {
        "customer_code": f"AUTO-{tax_id}",
        "customer_name": customer_name,
        "customer_type": "customer",
        "tax_id": tax_id,
        "status": "active",
    }
    if payment_terms:
        payload["payment_terms"] = payment_terms
    result = customer_create_tool(db, payload=payload, user=user)
    tool_call = ToolCallResult(tool_name="customer.create", status="success", input=payload, output=result)
    _store_message(db, session_id=session_id, role="tool", content="Customer create executed", tool_name="customer.create", tool_args=payload, tool_result=result)
    return _store_assistant_response(
        db,
        session_id=session_id,
        message=f"已建立客戶 {result['customer_name']}。",
        tool_calls=[tool_call],
        data=result,
    )


def _handle_update(db: Session, *, session_id: str, message: str, user: CurrentUser) -> AgentResponse:
    search_result = _find_customer_candidates(db, message)
    if len(search_result["items"]) != 1:
        if len(search_result["items"]) > 1:
            return _store_assistant_response(
                db,
                session_id=session_id,
                message="查到多筆客戶，請提供更明確的客戶名稱或統編。",
                tool_calls=[],
                data=search_result,
            )
        return _store_assistant_response(
            db,
            session_id=session_id,
            message="找不到要修改的客戶，請指定目標客戶。",
            tool_calls=[],
            data=search_result,
        )

    customer = search_result["items"][0]
    payment_terms = _extract_payment_terms(message)
    if payment_terms:
        reason = _extract_reason(message)
        if not reason:
            return _store_assistant_response(
                db,
                session_id=session_id,
                message="高風險變更需要提供原因。請補充原因後，我會先整理送審內容給你確認。",
                tool_calls=[],
                data={"required_reason_for": "payment_terms"},
            )
        preview = (
            "我將建立一張審核申請，不會直接修改資料。\n"
            "變更內容如下：\n"
            "- 欄位：payment_terms\n"
            f"- 新值：{payment_terms}\n"
            f"- 原因：{reason}\n"
            "請確認是否送出審核？"
        )
        _queue_pending_action(
            db,
            session_id=session_id,
            action_type="customer.update_sensitive",
            payload={"customer_id": customer["id"], "payload": {"payment_terms": payment_terms}, "reason": reason},
            preview_message=preview,
        )
        return _store_assistant_response(db, session_id=session_id, message=preview, tool_calls=[], data={"pending_confirmation": True})

    phone = _extract_phone(message)
    if phone:
        payload = {"phone": phone}
        result = customer_update_tool(db, customer_id=customer["id"], payload=payload, user=user)
        tool_call = ToolCallResult(tool_name="customer.update", status="success", input=payload, output=result)
        _store_message(db, session_id=session_id, role="tool", content="Customer update executed", tool_name="customer.update", tool_args=payload, tool_result=result)
        return _store_assistant_response(
            db,
            session_id=session_id,
            message="已更新客戶電話。",
            tool_calls=[tool_call],
            data=result,
        )

    raise bad_request("目前僅支援以自然語言更新電話或付款條件欄位，其他欄位可走 API")


def _handle_disable(db: Session, *, session_id: str, message: str) -> AgentResponse:
    search_result = _find_customer_candidates(db, message)
    if len(search_result["items"]) != 1:
        if len(search_result["items"]) > 1:
            return _store_assistant_response(
                db,
                session_id=session_id,
                message="查到多筆客戶，請提供更明確的客戶名稱或統編。",
                tool_calls=[],
                data=search_result,
            )
        return _store_assistant_response(
            db,
            session_id=session_id,
            message="找不到要停用的客戶，請指定目標客戶。",
            tool_calls=[],
            data=search_result,
        )

    reason = _extract_reason(message)
    if not reason:
        return _store_assistant_response(
            db,
            session_id=session_id,
            message="停用客戶屬於高風險操作，請先提供原因。",
            tool_calls=[],
            data={"required_reason_for": "disable"},
        )

    customer = search_result["items"][0]
    preview = (
        "我將建立一張審核申請，不會直接停用客戶資料。\n"
        f"變更內容如下：\n- 客戶：{customer['customer_name']}\n- 欄位：status\n- 原值：active\n- 新值：inactive\n- 原因：{reason}\n"
        "請確認是否送出審核？"
    )
    _queue_pending_action(
        db,
        session_id=session_id,
        action_type="customer.disable",
        payload={"customer_id": customer["id"], "reason": reason},
        preview_message=preview,
    )
    return _store_assistant_response(db, session_id=session_id, message=preview, tool_calls=[], data={"pending_confirmation": True})


def _execute_rule_based_message(
    db: Session,
    *,
    session_id: str,
    message: str,
    user: CurrentUser,
    store_user_message: bool = True,
) -> AgentResponse:
    session = db.get(AgentSession, uuid.UUID(session_id))
    if not session or str(session.user_id) != user.id:
        raise not_found("Session not found")

    if store_user_message:
        _store_message(db, session_id=session_id, role="user", content=message)

    pending = _get_active_pending_action(db, session_id=session_id)
    if pending and _is_confirmation(message):
        return _execute_pending_action(db, session_id=session_id, pending=pending, user=user)
    if pending and not _is_confirmation(message):
        _mark_pending_action_resolved(db, session_id=session_id, pending=pending)

    lowered = message.lower()
    if "查詢" in message or "search" in lowered or "找" in message:
        return _handle_search(db, session_id=session_id, message=message)
    if "新增" in message:
        return _handle_create(db, session_id=session_id, message=message, user=user)
    if "停用" in message:
        return _handle_disable(db, session_id=session_id, message=message)
    if "改成" in message or "修改" in message:
        return _handle_update(db, session_id=session_id, message=message, user=user)

    return _store_assistant_response(
        db,
        session_id=session_id,
        message="目前可協助查詢客戶、建立客戶、修改一般欄位，或建立高風險變更的審核申請。",
        tool_calls=[],
        data=None,
    )


def handle_message(db: Session, *, session_id: str, message: str, user: CurrentUser) -> AgentResponse:
    session = db.get(AgentSession, uuid.UUID(session_id))
    if not session or str(session.user_id) != user.id:
        raise not_found("Session not found")

    pending = _get_active_pending_action(db, session_id=session_id)
    if pending:
        return _execute_rule_based_message(db, session_id=session_id, message=message, user=user)

    _store_message(db, session_id=session_id, role="user", content=message)
    db.commit()

    return invoke_agent_graph(
        session_id=session_id,
        message=message,
        executor=lambda canonical_message: _execute_rule_based_message(
            db,
            session_id=session_id,
            message=canonical_message,
            user=user,
            store_user_message=False,
        ),
    )
