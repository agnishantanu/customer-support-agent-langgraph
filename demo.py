from app.graphs.workflow_graph import run_support_workflow


if __name__ == "__main__":
    sample_queries = [
        "What are your pricing plans?",
        "I forgot my password.",
        "My application crashes while uploading a file.",
        "I need a refund.",
        "What was my previous support issue?",
    ]

    for query in sample_queries:
        result = run_support_workflow("Ada", query)
        print(f"Query: {query}")
        print(f"Intent: {result.get('intent')}")
        print(f"Department: {result.get('department')}")
        print(f"Approval: {result.get('approval_status')}")
        print(f"Response: {result.get('response', '')[:220]}\n")
