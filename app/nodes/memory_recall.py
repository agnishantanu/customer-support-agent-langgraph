from app.memory import retrieve_previous_issue
from app.models.state import SupportState


def memory_recall_node(state: SupportState) -> dict:
    customer_name = state.get("customer_name", "Valued Customer")
    previous_issue = retrieve_previous_issue(customer_name=customer_name)
    return {
        "response": previous_issue,
        "approval_status": "not_required",
    }
