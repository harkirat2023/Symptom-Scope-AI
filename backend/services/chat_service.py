"""
Chat Service — uses LangChain + Gemini via LLMService.

Preserves the exact same API contract as the previous implementation
so no route changes are needed.
"""

from services.llm_service import LLMService

SYSTEM_PROMPT_TEMPLATE = """You are a helpful health education assistant for SymptomScope AI.

You provide educational information only. You NEVER diagnose, prescribe medication, or replace professional medical advice.

Context about the user's current prediction (if available):
- Predicted Disease: {disease}
- Confidence: {confidence}%
- Severity: {severity}
- Selected Symptoms: {symptoms}
- Precautions: {precautions}

Rules:
1. Always remind users to consult a healthcare professional for medical advice.
2. Explain medical terms in simple language.
3. Do not ask for or store personal health information.
4. If asked about emergencies, tell them to call emergency services immediately.
5. Keep responses concise and educational.
6. Do not provide dosage recommendations for any medication.
7. If unsure, say "I cannot provide that information — please consult your doctor."

Medical Disclaimer: This information is for educational purposes only."""


class LlmClient:
    """Compatibility wrapper — delegates to LLMService."""

    def __init__(self):
        self._service = LLMService()

    async def send_message(
        self, messages: list[dict], system_prompt: str
    ) -> str:
        user_content = messages[-1]["content"] if messages else ""
        return await self._service.invoke(system_prompt, user_content)


class ChatService:
    def __init__(self):
        self.llm_client = LlmClient()
        self._llm = LLMService()

    def build_system_prompt(self, prediction_context: dict | None = None) -> str:
        if prediction_context:
            return SYSTEM_PROMPT_TEMPLATE.format(
                disease=prediction_context.get("disease", "unknown"),
                confidence=prediction_context.get("confidence", "N/A"),
                severity=prediction_context.get("severity", "unknown"),
                symptoms=", ".join(
                    prediction_context.get("symptoms", [])
                ) or "none specified",
                precautions="; ".join(
                    prediction_context.get("precautions", [])
                ) or "none specified",
            )
        return SYSTEM_PROMPT_TEMPLATE.format(
            disease="unknown",
            confidence="N/A",
            severity="unknown",
            symptoms="none specified",
            precautions="none specified",
        )

    def build_welcome_message(
        self, prediction_context: dict | None = None
    ) -> str:
        if prediction_context:
            disease = prediction_context.get("disease", "")
            return (
                f"I see you're looking at results for **{disease}**. "
                "I can help explain this condition, the symptoms involved, "
                "or what the precautions mean. What would you like to know?"
            )
        return (
            "Hello! I'm your SymptomScope health assistant. "
            "I can help answer questions about symptoms, conditions, and health information. "
            "How can I help you today?"
        )

    def _add_disclaimer(self, content: str) -> str:
        if "disclaimer" not in content.lower():
            content += (
                "\n\n---\n"
                "*This information is for educational purposes only and does not "
                "constitute medical advice. Always consult a qualified healthcare "
                "professional for medical concerns.*"
            )
        return content

    async def process_message(
        self,
        message: str,
        session_history: list[dict],
        prediction_context: dict | None = None,
    ) -> str:
        system_prompt = self.build_system_prompt(prediction_context)
        messages = [
            {"role": m["role"], "content": m["content"]}
            for m in session_history
        ]
        messages.append({"role": "user", "content": message})

        response = await self.llm_client.send_message(messages, system_prompt)
        return self._add_disclaimer(response)

    def validate_message(self, content: str) -> tuple[bool, str]:
        if len(content) > 500:
            return False, "Message is too long (max 500 characters)."
        if len(content.strip()) < 1:
            return False, "Message cannot be empty."
        return True, ""

    def build_context(
        self,
        disease: str = "",
        confidence: float = 0,
        severity: str = "",
        symptoms: list[str] = None,
        precautions: list[str] = None,
    ) -> dict:
        return {
            "disease": disease,
            "confidence": confidence,
            "severity": severity,
            "symptoms": symptoms or [],
            "precautions": precautions or [],
        }

    # --- New: LLMService-powered features ---

    async def explain_prediction(
        self,
        disease: str,
        confidence: float,
        severity: str,
        symptoms: list[str],
        precautions: list[str],
        alternatives: list[str],
    ) -> str:
        return await self._llm.explain_prediction(
            disease=disease,
            confidence=confidence,
            severity=severity,
            symptoms=symptoms,
            precautions=precautions,
            alternatives=alternatives,
        )

    async def generate_follow_up_questions(
        self,
        disease: str,
        confidence: float,
        severity: str,
        symptoms: list[str],
    ) -> list[str]:
        return await self._llm.generate_follow_up_questions(
            disease=disease,
            confidence=confidence,
            severity=severity,
            symptoms=symptoms,
        )

    async def answer_medical_question(
        self,
        question: str,
        context: str | None = None,
    ) -> str:
        return await self._llm.answer_medical_question(
            question=question,
            context=context,
        )
