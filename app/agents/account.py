from langchain_core.prompts import ChatPromptTemplate

from app.memory import retrieve_previous_issue
from app.models.state import SupportState
from app.models.llm_factory import get_llm

# System prompt for Account Management Agent
ACCOUNT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", (
        "You are an Account Security and User Management Specialist at ABC Technologies. Your customer's name is {customer_name}.\n"
        "Your role is to assist with login issues, password resets, profile updates, MFA setup, and account status/settings.\n"
        "Maintain high security standards, be polite, and protect user data.\n"
        "IMPORTANT: If the user is requesting an account closure or deletion, draft a response explaining the steps and "
        "clearly inform them that the final account closure must be routed to our compliance and management team for human approval.\n"
        "Provide direct, clear guidelines to help the user resolve their issue."
    )),
    ("placeholder", "{chat_history}"),
    ("human", "{query}")
])


def account_agent_node(state: SupportState) -> dict:
    """
    Generates a draft account support response based on the customer query and history.
    """
    query = state.get("query", "")
    if any(keyword in query.lower() for keyword in ["previous support issue", "previous issue", "what was my previous"]):
        previous_issue = retrieve_previous_issue(state.get("customer_name", "Valued Customer"))
        return {
            "response": f"{previous_issue}",
            "department": "Account",
        }

    llm = get_llm()
    memory = state.get("memory", [])

    chat_history = []
    for msg in memory:
        role = msg.get("role", "human")
        content = msg.get("content", "")
        if role == "human":
            chat_history.append(("human", content))
        else:
            chat_history.append(("assistant", content))

    prompt = ACCOUNT_PROMPT.partial(
        customer_name=state.get("customer_name", "Valued Customer"),
        chat_history=chat_history
    )

    chain = prompt | llm
    response = chain.invoke({"query": query})

    return {
        "response": response.content,
        "department": "Account"
    }
