from langchain_core.prompts import ChatPromptTemplate
from app.models.state import SupportState
from app.models.llm_factory import get_llm

# System prompt for Sales Agent
SALES_PROMPT = ChatPromptTemplate.from_messages([
    ("system", (
        "You are a professional Sales Agent for ABC Technologies. Your customer's name is {customer_name}.\n"
        "Your goal is to handle product information inquiries, pricing questions, subscription plan details, and feature walkthroughs.\n"
        "Provide a welcoming, engaging, and professional response that highlights the value of our SaaS product.\n"
        "Encourage them to explore our plans (Basic, Pro, Enterprise) or schedule a demo if appropriate.\n"
        "Maintain a helpful sales posture. If you need specific pricing details that you do not know, make a draft response that can be grounded by company documents in the next step."
    )),
    ("placeholder", "{chat_history}"),
    ("human", "{query}")
])

def sales_agent_node(state: SupportState) -> dict:
    """
    Generates a draft sales response based on the customer query and history.
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

    prompt = SALES_PROMPT.partial(
        customer_name=state.get("customer_name", "Valued Customer"),
        chat_history=chat_history
    )
    
    chain = prompt | llm
    response = chain.invoke({"query": state.get("query", "")})
    
    return {
        "response": response.content,
        "department": "Sales"
    }
