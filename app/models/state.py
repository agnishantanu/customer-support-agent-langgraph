from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime
import uuid


class SupportState(TypedDict):
    customer_name: str
    query: str
    intent: str
    department: str
    retrieved_documents: List[str]
    memory: List[Dict[str, Any]]
    approval_status: str
    supervisor_notes: str
    response: str
    conversation_id: str
    metadata: Dict[str, Any]


def create_initial_state(
    customer_name: str,
    query: str,
    conversation_id: str = None
) -> SupportState:
    if conversation_id is None:
        conversation_id = str(uuid.uuid4())

    return SupportState(
        customer_name=customer_name,
        query=query,
        intent="",
        department="",
        retrieved_documents=[],
        memory=[],
        approval_status="not_required",
        supervisor_notes="",
        response="",
        conversation_id=conversation_id,
        metadata={
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "turn_count": 0,
            "escalated": False,
            "rag_sources": [],
            "llm_provider": "",
            "processing_time_ms": 0,
        }
    )


VALID_INTENTS = ["sales", "technical", "billing", "account"]

VALID_DEPARTMENTS = ["Sales", "Technical Support", "Billing", "Account"]

VALID_APPROVAL_STATUSES = [
    "not_required",
    "pending",
    "approved",
    "rejected",
]

APPROVAL_TRIGGER_KEYWORDS = [
    "refund",
    "cancel",
    "cancellation",
    "close account",
    "account closure",
    "compensation",
    "escalat",
    "escalation",
    "escalate",
]

INTENT_TO_DEPARTMENT = {
    "sales": "Sales",
    "technical": "Technical Support",
    "billing": "Billing",
    "account": "Account",
}
