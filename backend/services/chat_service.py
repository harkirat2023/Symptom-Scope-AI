import json
import httpx
from utils.settings import settings

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
    def __init__(self):
        self.api_url = settings.llm_api_url
        self.api_key = settings.llm_api_key
        self.model = settings.llm_model or "gpt-3.5-turbo"
        self.timeout = 15.0

    async def send_message(
        self, messages: list[dict], system_prompt: str
    ) -> str:
        if not self.api_url or not self.api_key:
            return (
                "I'm sorry, the health assistant is not configured. "
                "Please contact support to enable this feature."
            )

        full_messages = [{"role": "system", "content": system_prompt}]
        full_messages.extend(messages)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": full_messages,
                        "max_tokens": 500,
                        "temperature": 0.7,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
        except httpx.TimeoutException:
            return "I'm sorry, the response took too long. Please try again."
        except Exception as e:
            return (
                "I apologize, but I encountered an error processing your request. "
                "Please try again later."
            )


class ChatService:
    def __init__(self):
        self.llm_client = LlmClient()

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
