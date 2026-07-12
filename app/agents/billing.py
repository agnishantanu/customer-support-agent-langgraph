from langchain_core.prompts import ChatPromptTemplate
from app.models.state import SupportState
from app.models.llm_factory import get_llm

# System prompt for Billing Agent
BILLING_PROMPT = ChatPromptTemplate.from_messages([
    ("system", (
        "You are a Billing and Accounts Receivable Specialist at ABC Technologies. Your customer's name is {customer_name}.\n"
        "Your role is to address invoices, charges, payment failures, subscription tiers, refunds, and cancellations.\n"
        "Be extremely polite, clear, and professional. Explain billing terms and procedures clearly.\n"
        "IMPORTANT: If the user is requesting a refund, subscription cancellation, or compensation, draft a response that outlines the request details, "
        "states our refund/cancellation policies in general, and clearly informs the customer that their request is being routed for manager approval. "
        "Keep the tone reassuring and professional."
    )),
    ("placeholder", "{chat_history}"),
    ("human", "{query}")
])

def billing_agent_node(state: SupportState) -> dict:
    """
    Generates a draft billing support response based on the customer query and history.
    """
    llm = get_llm()
    memory = state.get("memory", [])
    
    # Format memory for ChatPromptTemplate placeholder
    chat_history = []
    for msg in memory:
        role = msg.get("role", "human")
        content = msg.get("content", "")
        if role == "human":
            chat_history.append(("human", content))
        else:
            chat_history.append(("assistant", content))

    prompt = BILLING_PROMPT.partial(
        customer_name=state.get("customer_name", "Valued Customer"),
        chat_history=chat_history
    )
    
    chain = prompt | llm
    response = chain.invoke({"query": state.get("query", "")})
    
    return {
        "response": response.content,
        "department": "Billing"
    }
