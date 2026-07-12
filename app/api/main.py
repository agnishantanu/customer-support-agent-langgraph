from fastapi import FastAPI
from pydantic import BaseModel

from app.graphs.workflow_graph import run_support_workflow

app = FastAPI(title="ABC Technologies Support Agent")


class ChatRequest(BaseModel):
    customer_name: str = "Valued Customer"
    query: str
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    intent: str
    department: str
    approval_status: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    result = run_support_workflow(
        customer_name=request.customer_name,
        query=request.query,
        conversation_id=request.conversation_id,
    )
    return ChatResponse(
        conversation_id=result.get("conversation_id", ""),
        response=result.get("response", ""),
        intent=result.get("intent", ""),
        department=result.get("department", ""),
        approval_status=result.get("approval_status", "not_required"),
    )
