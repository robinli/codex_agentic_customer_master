import json
from typing import Any, Callable, TypedDict

from app.agent.prompts import INTENT_CLASSIFIER_PROMPT, SYSTEM_RULES
from app.config import get_settings

try:
    from langgraph.graph import END, START, StateGraph
    from openai import OpenAI
except ImportError:  # pragma: no cover
    StateGraph = None
    START = END = None
    OpenAI = None


class AgentGraphState(TypedDict, total=False):
    session_id: str
    message: str
    canonical_message: str
    action: str
    confidence: float
    notes: str
    response: Any


def is_llm_agent_available() -> bool:
    settings = get_settings()
    return bool(settings.openai_api_key and StateGraph and OpenAI)


def _classify_message(message: str) -> dict[str, Any]:
    settings = get_settings()
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.responses.create(
        model=settings.agent_model,
        reasoning={"effort": settings.agent_reasoning_effort},
        instructions=f"{SYSTEM_RULES}\n\n{INTENT_CLASSIFIER_PROMPT}",
        input=message,
    )
    text = getattr(response, "output_text", None)
    if not text:
        raise ValueError("LLM returned empty classifier output")
    parsed = json.loads(text)
    return {
        "action": parsed.get("action", "chat"),
        "canonical_message": parsed.get("canonical_message", message),
        "confidence": float(parsed.get("confidence", 0)),
        "notes": parsed.get("notes", ""),
    }


def invoke_agent_graph(
    *,
    session_id: str,
    message: str,
    executor: Callable[[str], Any],
) -> Any:
    if not is_llm_agent_available():
        return executor(message)

    def classify_node(state: AgentGraphState) -> AgentGraphState:
        return _classify_message(state["message"])

    def execute_node(state: AgentGraphState) -> AgentGraphState:
        canonical_message = state.get("canonical_message") or state["message"]
        return {"response": executor(canonical_message)}

    builder = StateGraph(AgentGraphState)
    builder.add_node("classify", classify_node)
    builder.add_node("execute", execute_node)
    builder.add_edge(START, "classify")
    builder.add_edge("classify", "execute")
    builder.add_edge("execute", END)
    try:
        graph = builder.compile()
        result = graph.invoke({"session_id": session_id, "message": message})
        return result["response"]
    except Exception:
        return executor(message)
