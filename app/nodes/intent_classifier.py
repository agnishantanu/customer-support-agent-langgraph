from langchain_core.prompts import ChatPromptTemplate
from app.models.state import SupportState, VALID_INTENTS, INTENT_TO_DEPARTMENT
from app.models.llm_factory import get_llm


INTENT_CLASSIFICATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", (
        "You are an intent classification engine for ABC Technologies customer support.\n"
        "Classify the customer query into exactly ONE of these intents:\n\n"
        "- sales: Product information, pricing plans, feature comparisons, demos, purchases\n"
        "- technical: Technical issues, bugs, errors, crashes, performance, how-to questions\n"
        "- billing: Invoices, payments, refunds, subscription changes, charges, billing disputes\n"
        "- account: Password resets, account settings, profile updates, account closure, login issues\n\n"
        "Respond with ONLY the intent label in lowercase. No explanation. No punctuation.\n"
        "Examples:\n"
        "Query: 'What are your pricing plans?' → sales\n"
        "Query: 'My app crashes on upload' → technical\n"
        "Query: 'I need a refund' → billing\n"
        "Query: 'I forgot my password' → account"
    )),
    ("human", "Query: '{query}'"),
])


KEYWORD_MAP = {
    "sales": [
        "pricing", "price", "cost", "plan", "plans", "subscription",
        "buy", "purchase", "demo", "feature", "features", "product",
        "upgrade", "downgrade", "trial", "offer", "discount", "quote",
        "package", "packages", "tier", "tiers", "enterprise",
    ],
    "technical": [
        "error", "bug", "crash", "crashes", "crashing", "slow",
        "not working", "broken", "issue", "problem", "fix", "debug",
        "install", "installation", "update", "upload", "download",
        "integrate", "integration", "api", "sdk", "performance",
        "timeout", "connection", "fail", "failed", "failure",
        "technical", "troubleshoot", "log", "logs", "configure",
    ],
    "billing": [
        "invoice", "invoices", "payment", "charge", "charged",
        "refund", "billing", "bill", "receipt", "transaction",
        "credit", "debit", "overcharged", "prorate", "proration",
        "cancel subscription", "renew", "renewal", "compensation",
    ],
    "account": [
        "password", "login", "log in", "sign in", "account",
        "profile", "email change", "username", "reset", "locked",
        "locked out", "two-factor", "2fa", "mfa", "authentication",
        "deactivate", "close account", "delete account", "settings",
        "previous issue", "previous support", "past issue",
        "history", "my last",
    ],
}


def classify_intent_with_keywords(query: str) -> str:
    query_lower = query.lower().strip()

    if any(phrase in query_lower for phrase in ["previous support issue", "previous issue", "what was my previous", "my previous support", "my last issue", "history"]):
        return "account"

    if any(phrase in query_lower for phrase in ["refund", "billing", "invoice", "payment", "charge", "compensation"]):
        return "billing"

    scores = {intent: 0 for intent in VALID_INTENTS}

    for intent, keywords in KEYWORD_MAP.items():
        for keyword in keywords:
            if keyword in query_lower:
                scores[intent] += 1

    max_score = max(scores.values())
    if max_score > 0:
        for intent in VALID_INTENTS:
            if scores[intent] == max_score:
                return intent

    return "sales"


def classify_intent_with_llm(query: str) -> str:
    try:
        llm = get_llm()
        chain = INTENT_CLASSIFICATION_PROMPT | llm
        result = chain.invoke({"query": query})

        intent = result.content.strip().lower().replace(".", "").replace("'", "").replace('"', '')

        if intent in VALID_INTENTS:
            return intent

        return classify_intent_with_keywords(query)

    except Exception:
        return classify_intent_with_keywords(query)


def intent_classifier_node(state: SupportState) -> dict:
    query = state.get("query", "")

    if not query.strip():
        return {
            "intent": "sales",
            "department": INTENT_TO_DEPARTMENT["sales"],
        }

    intent = classify_intent_with_llm(query)
    department = INTENT_TO_DEPARTMENT.get(intent, "Sales")

    return {
        "intent": intent,
        "department": department,
    }
