import os

from app.graphs.workflow_graph import build_workflow_graph
from app.memory import load_history, retrieve_previous_issue, save_conversation
from app.models.state import create_initial_state
from app.nodes.intent_classifier import classify_intent_with_keywords
from app.nodes.router import check_approval_needed


def test_classify_sales_and_account_queries():
    assert classify_intent_with_keywords("What are your pricing plans?") == "sales"
    assert classify_intent_with_keywords("I forgot my password") == "account"
    assert classify_intent_with_keywords("My application crashes while uploading a file") == "technical"


def test_memory_helpers_round_trip(tmp_path):
    db_path = tmp_path / "memory.db"
    state = create_initial_state("Ada", "I forgot my password", conversation_id="conv-1")

    save_conversation(
        conversation_id=state["conversation_id"],
        customer_name=state["customer_name"],
        query=state["query"],
        response="Please reset your password using the reset link.",
        intent="account",
        department="Account",
        db_path=str(db_path),
    )

    history = load_history(conversation_id="conv-1", db_path=str(db_path))
    assert len(history) == 1
    assert history[0]["intent"] == "account"

    previous_issue = retrieve_previous_issue(customer_name="Ada", db_path=str(db_path))
    assert "password" in previous_issue.lower()


def test_approval_is_only_for_refund_requests():
    state = create_initial_state("Ada", "I forgot my password")
    state["intent"] = "account"
    assert check_approval_needed(state) == "no_approval"

    refund_state = create_initial_state("Ada", "I need a refund")
    refund_state["intent"] = "billing"
    assert check_approval_needed(refund_state) == "needs_approval"


def test_workflow_graph_compiles():
    graph = build_workflow_graph()
    assert graph is not None
