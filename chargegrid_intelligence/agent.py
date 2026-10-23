from __future__ import annotations

import os
import re

from dotenv import load_dotenv
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI

from .guardrails import ScopeGuardAgent
from .knowledge import build_context
from .memory import update_facts
from .models import estimate_tokens, system_prompt


class ChargeGridAgent:
    """Agente conversacional do ChargeGrid Intelligence usando LangChain e Gemini."""

    def __init__(self, model_name: str | None = None, temperature: float | None = None):
        load_dotenv()
        gemini_key = os.getenv("GEMINI_API_KEY")
        google_key = os.getenv("GOOGLE_API_KEY")
        api_key = gemini_key or google_key
        if not api_key:
            raise RuntimeError(
                "A chave do Gemini não foi configurada. No Colab, configure a chave antes de criar o agente."
            )

        os.environ["GOOGLE_API_KEY"] = api_key
        os.environ.pop("GEMINI_API_KEY", None)

        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
        self.scope_guard = ScopeGuardAgent()
        self._facts_by_session: dict[str, dict[str, str]] = {}
        self._history_by_session: dict[str, InMemoryChatMessageHistory] = {}

        llm_config: dict[str, object] = {"model": self.model_name, "google_api_key": api_key}
        if temperature is not None:
            llm_config["temperature"] = temperature
        self._llm = ChatGoogleGenerativeAI(**llm_config)
        self._prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "{system_prompt}"),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}"),
            ]
        )

    def ask(self, message: str, session_id: str = "default") -> dict[str, object]:
        facts = self._facts_by_session.get(session_id, {})
        history = self._get_history(session_id)
        has_context = bool(facts or history.messages)
        guardrail = self.scope_guard.evaluate(message, has_context=has_context)

        if not guardrail.allowed:
            return {
                "answer": guardrail.message,
                "facts": facts,
                "guardrail_category": guardrail.category,
                "model": "guardrail",
                "estimated_tokens": estimate_tokens(guardrail.message),
            }

        facts = update_facts(message, facts)
        self._facts_by_session[session_id] = facts
        context = build_context(facts)

        prompt_value = self._prompt.invoke(
            {
                "input": message,
                "history": history.messages,
                "system_prompt": system_prompt(context=context, facts=facts),
            }
        )
        response = self._llm.invoke(prompt_value)
        answer = _extract_text(response).strip()
        answer = _clean_answer(answer, message, facts)
        history.add_user_message(message)
        history.add_ai_message(answer)

        if guardrail.message:
            answer = f"{guardrail.message}\n\n{answer}"

        return {
            "answer": answer,
            "facts": facts,
            "guardrail_category": guardrail.category,
            "model": self.model_name,
            "estimated_tokens": estimate_tokens(answer),
        }

    def _get_history(self, session_id: str) -> InMemoryChatMessageHistory:
        if session_id not in self._history_by_session:
            self._history_by_session[session_id] = InMemoryChatMessageHistory()
        return self._history_by_session[session_id]


def _extract_text(response: object) -> str:
    content = getattr(response, "content", response)
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
        if parts:
            return "\n".join(parts)

    return str(content)


def _clean_answer(answer: str, user_message: str, facts: dict[str, str]) -> str:
    cleaned = answer
    cleaned = re.sub(r"sk-[A-Za-z0-9_-]+", "[chave ocultada]", cleaned)
    cleaned = re.sub(r"AIza[A-Za-z0-9_-]+", "[chave ocultada]", cleaned)
    cleaned = re.sub(r"[A-Za-z]:\\[^\n\r\t]+", "[caminho local ocultado]", cleaned)
    cleaned = re.sub(r"/(?:content|tmp|usr|home)/[^\n\r\t]+", "[caminho local ocultado]", cleaned)

    blocked_terms = [
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "getpass",
        "variável de ambiente",
        "variavel de ambiente",
    ]
    lines = [
        line
        for line in cleaned.splitlines()
        if not any(term.lower() in line.lower() for term in blocked_terms)
    ]
    cleaned = "\n".join(lines).strip()

    user_lower = user_message.lower()
    has_user_location = "local_mencionado" in facts or any(
        term in user_lower for term in ["campus", "fiap", "unidade", "local", "eletroposto"]
    )
    if not has_user_location:
        cleaned = re.sub(
            r"\b(?:Campus\s+(?:da\s+)?)?FIAP(?:\s*-\s*unidade demonstrativa|\s+Paulista)?\b",
            "ambiente de demonstração",
            cleaned,
            flags=re.IGNORECASE,
        )

    return cleaned.strip()
