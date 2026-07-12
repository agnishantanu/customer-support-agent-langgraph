import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from langgraph.graph import StateGraph, END

from app.agents import (
    sales_agent_node,
    technical_agent_node,
    billing_agent_node,
    account_agent_node,
)
from app.models.state import SupportState, create_initial_state
from app.nodes.final_response import final_response_node
from app.nodes.intake import intake_node
from app.nodes.intent_classifier import intent_classifier_node
from app.nodes.memory import memory_store_node
from app.nodes.memory_recall import memory_recall_node
from app.nodes.router import route_to_department, check_approval_needed
from app.nodes.human_approval import human_approval_node
from app.nodes.supervisor import supervisor_node
from app.rag import rag_node as rag_pipeline_node


def build_workflow_graph(
    sales_agent=None,
    technical_agent=None,
    billing_agent=None,
    account_agent=None,
    rag_node_handler=None,
    human_approval_handler=None,
    supervisor_handler=None,
    memory_handler=None,
) -> StateGraph:
    workflow = StateGraph(SupportState)

    workflow.add_node("intake", intake_node)
    workflow.add_node("intent_classifier", intent_classifier_node)
    workflow.add_node("sales_agent", sales_agent or sales_agent_node)
    workflow.add_node("technical_agent", technical_agent or technical_agent_node)
    workflow.add_node("billing_agent", billing_agent or billing_agent_node)
    workflow.add_node("account_agent", account_agent or account_agent_node)
    workflow.add_node("rag", rag_node_handler or rag_pipeline_node)
    workflow.add_node("human_approval", human_approval_handler or human_approval_node)
    workflow.add_node("supervisor", supervisor_handler or supervisor_node)
    workflow.add_node("memory_store", memory_handler or memory_store_node)
    workflow.add_node("memory_recall", memory_recall_node)
    workflow.add_node("final_response", final_response_node)

    workflow.set_entry_point("intake")
    workflow.add_edge("intake", "intent_classifier")

    workflow.add_conditional_edges(
        "intent_classifier",
        route_to_department,
        {
            "sales": "sales_agent",
            "technical": "technical_agent",
            "billing": "billing_agent",
            "account": "account_agent",
        }
    )

    workflow.add_conditional_edges(
        "account_agent",
        lambda state: "memory_recall" if "previous" in state.get("query", "").lower() or "history" in state.get("query", "").lower() else "rag",
        {
            "memory_recall": "memory_recall",
            "rag": "rag",
        },
    )

    workflow.add_edge("sales_agent", "rag")
    workflow.add_edge("technical_agent", "rag")
    workflow.add_edge("billing_agent", "rag")
    workflow.add_edge("memory_recall", "final_response")

    workflow.add_conditional_edges(
        "rag",
        check_approval_needed,
        {
            "needs_approval": "human_approval",
            "no_approval": "supervisor",
        }
    )

    workflow.add_edge("human_approval", "supervisor")
    workflow.add_edge("supervisor", "memory_store")
    workflow.add_edge("memory_store", "final_response")
    workflow.add_edge("final_response", END)

    return workflow


def compile_graph(**kwargs):
    workflow = build_workflow_graph(**kwargs)
    return workflow.compile()


def run_support_workflow(customer_name: str, query: str, conversation_id: str = None) -> dict:
    graph = compile_graph()
    state = create_initial_state(customer_name=customer_name, query=query, conversation_id=conversation_id)
    return graph.invoke(state)


def generate_graph_image(output_path: str = None):
    if output_path is None:
        output_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "workflow", "workflow_graph.png"
        )
        output_path = os.path.normpath(output_path)

    workflow = build_workflow_graph()
    compiled = workflow.compile()

    try:
        png_bytes = compiled.get_graph().draw_mermaid_png()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(png_bytes)
        print(f"Workflow graph saved to: {output_path}")
        return output_path
    except Exception as e:
        print(f"PNG generation requires optional dependencies.")
        print(f"Install with: pip install grandalf")
        print(f"Error: {e}")

        mermaid_output = output_path.replace(".png", "_mermaid.md")
        mermaid_str = compiled.get_graph().draw_mermaid()
        with open(mermaid_output, "w") as f:
            f.write("```mermaid\n")
            f.write(mermaid_str)
            f.write("\n```\n")
        print(f"Mermaid diagram saved to: {mermaid_output}")
        return mermaid_output


def print_graph_ascii():
    workflow = build_workflow_graph()
    compiled = workflow.compile()
    print("\n=== LangGraph Workflow Structure ===\n")
    try:
        mermaid_str = compiled.get_graph().draw_mermaid()
        print(mermaid_str)
    except Exception as e:
        print(f"Could not generate graph visualization: {e}")
    print("\n=== Nodes ===")
    print("1.  intake           — Captures query, assigns conversation_id")
    print("2.  intent_classifier — LLM + keyword fallback classification")
    print("3.  sales_agent       — Handles sales/product/pricing queries")
    print("4.  technical_agent   — Handles technical/bug/error queries")
    print("5.  billing_agent     — Handles billing/refund/payment queries")
    print("6.  account_agent     — Handles account/password/login queries")
    print("7.  rag               — Retrieves relevant documents from ChromaDB")
    print("8.  human_approval    — Pauses for human sign-off on risky requests")
    print("9.  supervisor        — Validates response quality and safety")
    print("10. memory_store      — Persists conversation to SQLite")
    print("11. final_response    — Returns completed response")
    print("\n=== Conditional Edges ===")
    print("intent_classifier → [sales_agent | technical_agent | billing_agent | account_agent]")
    print("rag               → [human_approval | supervisor]")


if __name__ == "__main__":
    print_graph_ascii()
    print("\n--- Generating PNG ---")
    result = generate_graph_image()
    print(f"Result: {result}")
