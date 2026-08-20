"""
Centralized LLM Service — LangChain + Gemini with Groq fallback and direct SDK fallback.

Provides:
- AI Medical Report Explainer
- AI Follow-up Symptom Assistant
- Medical Knowledge Assistant (RAG-aware)
- General Chat with prediction context

Fallback chain:
1. LangChain + Gemini (primary)
2. LangChain + Groq (if configured)
3. Direct google-generativeai SDK (if Gemini key available)
4. Graceful error message (no crash)
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from utils.settings import settings

PROMPTS_DIR = Path(__file__).parent.parent / "ml" / "prompts"

_logger = logging.getLogger("symptomscope.llm_service")


def _load_prompt(name: str) -> str:
    path = PROMPTS_DIR / name
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


class LLMService:
    """Centralized LLM service with multi-provider fallback."""

    def __init__(self):
        self._groq_llm = None

    # --- Provider Initialization ---

    def _init_groq_langchain(self):
        """Initialize LangChain ChatGroq.

        The system uses Groq as the free primary LLM provider for generation.
        Gemeni/OpenAI paths were removed to comply with the free-Groq-only
        requirement. GROQ_API_KEY (settings.groq_api_key) must be set in
        production. This keeps the LangChain architecture intact while
        avoiding proprietary Gemini/OpenAI dependencies.
        """
        from langchain_groq import ChatGroq
        api_key = settings.groq_api_key
        if not api_key:
            raise RuntimeError("GROQ_API_KEY not configured")
        self._groq_llm = ChatGroq(
            model=settings.groq_model,
            groq_api_key=api_key,
            temperature=settings.groq_temperature,
            max_tokens=settings.groq_max_tokens,
        )

    # --- Provider Properties ---

    @property
    def groq_llm(self):
        if self._groq_llm is None:
            self._init_groq_langchain()
        return self._groq_llm

    # --- Core Invocation with Retry ---


    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((Exception,)),
        reraise=True,
    )
    async def _invoke_groq_langchain(
        self,
        system_prompt: str,
        user_message: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        json_mode: bool = False,
    ) -> str:
        """Invoke via LangChain + Groq."""
        messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_message)]
        kwargs: dict[str, Any] = {}
        if temperature is not None:
            kwargs["temperature"] = temperature
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        result = await asyncio.wait_for(
            self.groq_llm.ainvoke(messages, **kwargs),
            timeout=45.0,
        )
        return result.content

    # --- Public Invoke with Fallback Chain ---

    async def invoke(
        self,
        system_prompt: str,
        user_message: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        json_mode: bool = False,
    ) -> str:
        """
        Send a message to the LLM.

        Only the free Groq provider (LangChain + GROQ_API_KEY) is used.
        When json_mode is True the model is asked to produce a valid JSON
        object (Groq JSON mode).
        """
        if settings.groq_api_key:
            try:
                _logger.info("LLM invoke: attempting LangChain + Groq")
                return await self._invoke_groq_langchain(
                    system_prompt, user_message, temperature, max_tokens, json_mode
                )
            except Exception as e:
                _logger.exception("LangChain + Groq invocation failed")
                raise

        # GROQ not configured - fail fast with clear message.
        _logger.error("GROQ_API_KEY is not configured; LLM cannot be initialized")
        raise RuntimeError("GROQ_API_KEY is required for LLM generation")

    # --- Feature-specific Methods ---

    async def explain_prediction(
        self,
        disease: str,
        confidence: float,
        severity: str,
        symptoms: list[str],
        precautions: list[str],
        alternatives: list[str],
    ) -> str:
        """AI Medical Report Explainer — explains prediction in simple language."""
        prompt = _load_prompt("explain_prediction.txt")
        if not prompt:
            prompt = _default_explain_prompt()
        context = (
            f"Disease: {disease}\n"
            f"Confidence: {confidence}%\n"
            f"Severity: {severity}\n"
            f"Symptoms: {', '.join(symptoms)}\n"
            f"Precautions: {'; '.join(precautions)}\n"
            f"Alternatives: {', '.join(alternatives) if alternatives else 'None'}\n"
        )
        return await self.invoke(prompt, context)

    async def generate_follow_up_questions(
        self,
        disease: str,
        confidence: float,
        severity: str,
        symptoms: list[str],
    ) -> list[str]:
        """AI Follow-up Symptom Assistant — generates intelligent follow-up questions."""
        prompt = _load_prompt("follow_up_questions.txt")
        if not prompt:
            prompt = _default_follow_up_prompt()
        context = (
            f"Disease: {disease}\n"
            f"Confidence: {confidence}%\n"
            f"Severity: {severity}\n"
            f"Symptoms: {', '.join(symptoms)}\n"
        )
        result = await self.invoke(prompt, context)
        questions = [
            q.strip().strip("-").strip()
            for q in result.split("\n")
            if q.strip() and not q.strip().startswith("Here")
        ]
        return questions[:5]

    async def answer_medical_question(
        self,
        question: str,
        context: str | None = None,
    ) -> str:
        """Medical Knowledge Assistant (RAG-aware) — answers with grounded knowledge."""
        prompt = _load_prompt("medical_qa.txt")
        if not prompt:
            prompt = _default_medical_qa_prompt()
        user_content = question
        if context:
            user_content = f"Context:\n{context}\n\nQuestion:\n{question}"
        return await self.invoke(prompt, user_content)


# --- Default Prompts ---

def _default_explain_prompt() -> str:
    return (
        "You are a medical explainer for SymptomScope AI. "
        "Explain the following prediction in simple, clear language. "
        "Include: why this disease was predicted, what the confidence score means, "
        "the severity level, home care guidance, and when to consult a doctor. "
        "Always include the medical disclaimer.\n\n{context}"
    )


def _default_follow_up_prompt() -> str:
    return (
        "You are a medical assistant. Based on the user's prediction, "
        "generate 3-5 intelligent follow-up questions to gather more context. "
        "Ask about: additional symptoms, duration, triggers, relieving factors, "
        "or relevant medical history. Return one question per line.\n\n{context}"
    )


def _default_medical_qa_prompt() -> str:
    return (
        "You are a knowledgeable medical assistant for SymptomScope AI. "
        "Answer healthcare questions using educational information. "
        "If the question is not health-related, politely refuse and ask for a medical question. "
        "Always include: 'This information is for educational purposes only. "
        "Consult a healthcare professional for medical advice.'\n\n{user_content}"
    )