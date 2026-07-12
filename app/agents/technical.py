from langchain_core.prompts import ChatPromptTemplate
from app.models.state import SupportState
from app.models.llm_factory import get_llm

# System prompt for Technical Support Agent
TECHNICAL_PROMPT = ChatPromptTemplate.from_messages([
    ("system", (
        "You are a Senior Technical Support Specialist at ABC Technologies. Your customer's name is {customer_name}.\n"
        "Your role is to diagnose, troubleshoot, and solve technical issues, bugs, error messages, and crashes.\n"
        "Offer clear, step-by-step technical guidance in a professional, patient, and logical manner.\n"
        "If they are reporting an application crash or upload issue, provide technical debugging suggestions.\n"
        "If you lack specific details about the technical manual or faq, create a structured draft response which will be enriched by the technical documentation in the next step."
    )),
    ("placeholder", "{chat_history}"),
    ("human", "{query}")
])

def technical_agent_node(state: SupportState) -> dict:
    """
    Generates a draft technical support response based on the customer query and history.
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

    prompt = TECHNICAL_PROMPT.partial(
        customer_name=state.get("customer_name", "Valued Customer"),
        chat_history=chat_history
    )
    
    chain = prompt | llm
    response = chain.invoke({"query": state.get("query", "")})
    
    return {
        "response": response.content,
        "department": "Technical Support"
    }
