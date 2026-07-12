from typing import Any

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI

from app.utils.config import settings


class LocalFallbackLLM(RunnableLambda):
    def __init__(self, provider: str = "openai") -> None:
        self.provider = provider
        super().__init__(self._invoke)

    def _extract_text(self, prompt: Any) -> str:
        if hasattr(prompt, "to_messages"):
            messages = prompt.to_messages()
        elif isinstance(prompt, (list, tuple)):
            messages = list(prompt)
        else:
            return str(prompt)

        for message in reversed(messages):
            content = getattr(message, "content", "")
            if isinstance(content, list):
                parts = []
                for item in content:
                    if isinstance(item, dict):
                        parts.append(str(item.get("text", "")))
                    else:
                        parts.append(str(item))
                content = "".join(parts)
            if not isinstance(content, str):
                continue

            if "Customer Query:" in content:
                return content.split("Customer Query:", 1)[1].split("\n", 1)[0].strip()
            if "Agent Draft Response:" in content:
                return content.split("Agent Draft Response:", 1)[1].split("\n", 1)[0].strip()
            if "Human:" in content:
                return content.split("Human:", 1)[1].strip()
            if content.strip():
                return content.strip()
        return ""

    def _build_response(self, prompt_text: str) -> str:
        text = prompt_text.lower()
        if any(keyword in text for keyword in ["refund", "cancel", "cancellation", "compensation", "closure", "escalat"]):
            return (
                "I understand your request and I have routed it for careful review. "
                "Because this involves a financial or account-impacting action, it will be handled with human approval."
            )
        if "password" in text or "login" in text or "forgot" in text:
            return "Please use the password reset link or contact support for account verification before resetting your credentials."
        if any(keyword in text for keyword in ["pricing", "plan", "price", "basic", "pro", "enterprise"]):
            return "Our plans are Basic at ₹999/month, Pro at ₹2,999/month, and Enterprise at ₹8,999/month."
        if any(keyword in text for keyword in ["crash", "upload", "file", "error", "bug"]):
            return "Please verify that the file is under 50MB and uses a supported format such as PDF, PNG, JPEG, or ZIP."
        if any(keyword in text for keyword in ["previous", "history", "last issue"]):
            return "I can help retrieve your previous support issue from the conversation history."
        return "Thank you for contacting ABC Technologies support. I can help with sales, technical, billing, or account requests."

    def _invoke(self, prompt: Any, config: Any = None, **kwargs: Any) -> AIMessage:
        return AIMessage(content=self._build_response(self._extract_text(prompt)))

    async def ainvoke(self, prompt: Any, config: Any = None, **kwargs: Any) -> AIMessage:
        return self._invoke(prompt, config=config, **kwargs)


def get_llm(provider: str = None):
    provider = provider or settings.LLM_PROVIDER

    if provider == "openai" and settings.OPENAI_API_KEY:
        return ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.OPENAI_TEMPERATURE,
            api_key=settings.OPENAI_API_KEY,
        )

    if provider == "ibm":
        try:
            from ibm_watsonx_ai.foundation_models import Model
            from ibm_watsonx_ai.metanames import GenTextParamsMetaNames
            from langchain_ibm import WatsonxLLM

            parameters = {
                GenTextParamsMetaNames.MAX_NEW_TOKENS: 1024,
                GenTextParamsMetaNames.TEMPERATURE: 0.0,
            }

            return WatsonxLLM(
                model_id=settings.IBM_MODEL,
                url=settings.IBM_URL,
                apikey=settings.IBM_API_KEY,
                project_id=settings.IBM_PROJECT_ID,
                params=parameters,
            )
        except ImportError:
            raise ImportError(
                "IBM Watsonx dependencies not installed. "
                "Install with: pip install ibm-watsonx-ai langchain-ibm"
            )

    if provider == "ibm" and not settings.IBM_API_KEY:
        return LocalFallbackLLM(provider=provider)

    if provider == "openai" and not settings.OPENAI_API_KEY:
        return LocalFallbackLLM(provider=provider)

    raise ValueError(
        f"Unsupported LLM provider: '{provider}'. "
        f"Supported providers: 'openai', 'ibm'"
    )
