from app.models.state import (
    SupportState,
    VALID_INTENTS,
)


def route_to_department(state: SupportState) -> str:
    intent = state.get("intent", "").lower().strip()
    if intent in VALID_INTENTS:
        return intent
    return "sales"


def check_approval_needed(state: SupportState) -> str:
    query_lower = state.get("query", "").lower().strip()
    response_lower = state.get("response", "").lower()
    intent_lower = state.get("intent", "").lower().strip()

    is_refund_request = (
        "refund" in query_lower or "refund" in response_lower
    ) and intent_lower == "billing"

    if is_refund_request:
        return "needs_approval"
    return "no_approval"
