import uuid
from datetime import datetime
from app.models.state import SupportState


def intake_node(state: SupportState) -> dict:
    updates = {}

    if not state.get("conversation_id"):
        updates["conversation_id"] = str(uuid.uuid4())

    metadata = state.get("metadata", {})
    metadata["created_at"] = metadata.get("created_at", datetime.utcnow().isoformat())
    metadata["updated_at"] = datetime.utcnow().isoformat()
    metadata["turn_count"] = metadata.get("turn_count", 0) + 1
    updates["metadata"] = metadata

    return updates
