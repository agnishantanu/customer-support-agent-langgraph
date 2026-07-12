from app.models.state import SupportState


def human_approval_node(state: SupportState) -> dict:
    query = state.get("query", "").lower()
    if "refund" in query and state.get("intent", "").lower() == "billing":
        return {
            "approval_status": "pending",
            "response": state.get("response", "") + "\n\nThis request requires human approval before it can be finalized.",
        }

    return {
        "approval_status": "approved",
        "response": state.get("response", ""),
    }
