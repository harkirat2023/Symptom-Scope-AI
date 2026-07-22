"""
Centralized LLM Service — LangChain + Gemini 2.5 Flash.

Provides:
- AI Medical Report Explainer
- AI Follow-up Symptom Assistant
- Medical Knowledge Assistant (RAG-aware)

All LLM calls go through this service. Prompts are loaded from ml/prompts/.
"""

from pathlib import Path
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from utils.settings import settings

PROMPTS_DIR = Path(__file__).parent.parent / "ml" / "prompts"


def _load_prompt(name: str) -> str:
    path = PROMPTS_DIR / name
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


class LLMService:
    """Centralized LLM service using LangChain + Gemini 2.5 Flash."""

    def __init__(self):
        self._llm = None

    @property
    def llm(self) -> ChatGoogleGenerativeAI:
        if self._llm is None:
            api_key = settings.gemini_api_key
            if not api_key:
                raise RuntimeError(
                    "GEMINI_API_KEY is not configured. "
                    "Set GEMINI_API_KEY in environment variables."
                )
            self._llm = ChatGoogleGenerativeAI(
                model=settings.gemini_model,
                google_api_key=api_key,
                temperature=settings.gemini_temperature,
                max_tokens=settings.gemini_max_tokens,
            )
        return self._llm

    async def invoke(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Send a message to the LLM and return the response."""
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message),
        ]
        kwargs: dict[str, Any] = {}
        if temperature is not None:
            kwargs["temperature"] = temperature
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens
        result = await self.llm.ainvoke(messages, **kwargs)
        return result.content

    # --- Feature-specific methods ---

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

    async def chat(self, message: str, history: list[dict], prediction_context: dict | None = None) -> str:
        """General chat with prediction context."""
        prompt = _load_prompt("chat.txt")
        if not prompt:
            prompt = _default_chat_prompt()

        ctx_lines = []
        if prediction_context:
            ctx_lines.append("Prediction Context:")
            for k, v in prediction_context.items():
                ctx_lines.append(f"- {k}: {v}")
        context_str = "\n".join(ctx_lines) if ctx_lines else "No active prediction."

        filled_prompt = prompt.replace("{prediction_context}", context_str)

        messages = [SystemMessage(content=filled_prompt)]
        for msg in history[-10:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                messages.append(HumanMessage(content=content))
            else:
                messages.append(SystemMessage(content=content))
        messages.append(HumanMessage(content=message))

        result = await self.llm.ainvoke(messages)
        return result.content


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


def _default_chat_prompt() -> str:
    return (
        "You are a helpful health education assistant for SymptomScope AI. "
        "You provide educational information only. You NEVER diagnose, "
        "prescribe medication, or replace professional medical advice.\n\n"
        "{prediction_context}\n\n"
        "Rules:\n"
        "1. Always remind users to consult a healthcare professional.\n"
        "2. Explain medical terms in simple language.\n"
        "3. Do not ask for or store personal health information.\n"
        "4. If asked about emergencies, tell them to call emergency services immediately.\n"
        "5. Keep responses concise and educational.\n"
        "6. Do not provide dosage recommendations.\n"
        "7. If unsure, say 'I cannot provide that information — please consult your doctor.'\n"
        "8. If the question is not health-related, politely refuse.\n\n"
        "Medical Disclaimer: This information is for educational purposes only."
    )
