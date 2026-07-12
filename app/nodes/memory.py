from app.memory import save_conversation
from app.models.state import SupportState


def memory_store_node(state: SupportState) -> dict:
    save_conversation(
        conversation_id=state.get("conversation_id", ""),
        customer_name=state.get("customer_name", "Valued Customer"),
        query=state.get("query", ""),
        response=state.get("response", ""),
        intent=state.get("intent", ""),
        department=state.get("department", ""),
        metadata=state.get("metadata", {}),
    )
    return {
        "memory": [
            {"role": "human", "content": state.get("query", "")},
            {"role": "assistant", "content": state.get("response", "")},
        ]
    }
