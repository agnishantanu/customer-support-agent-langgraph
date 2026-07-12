from datetime import datetime
from app.models.state import SupportState


def final_response_node(state: SupportState) -> dict:
    metadata = state.get("metadata", {})
    metadata["updated_at"] = datetime.utcnow().isoformat()
    metadata["completed"] = True

    response = state.get("response", "")
    if not response.strip():
        response = (
            "Thank you for contacting ABC Technologies support. "
            "We were unable to generate a specific response to your query. "
            "Please try again or contact us directly."
        )

    return {
        "response": response,
        "metadata": metadata,
    }
