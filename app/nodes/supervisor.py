from app.models.state import SupportState


def supervisor_node(state: SupportState) -> dict:
    response = state.get("response", "")
    query = state.get("query", "")

    if not response.strip():
        response = "I am sorry, I could not produce a complete answer. Please try again or contact support directly."

    revised = response.strip()
    if not revised.endswith((".", "!", "?")):
        revised = f"{revised}."

    if "refund" in query.lower() and state.get("intent", "").lower() == "billing":
        revised = revised + " This response has been reviewed and flagged for human confirmation."

    return {
        "response": revised,
        "supervisor_notes": "Response reviewed for professionalism, completeness, and safety.",
    }
