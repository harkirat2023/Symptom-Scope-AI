from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from schemas.chat_schema import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatSessionListResponse,
    ChatMessageResponse,
    MessageSend,
)
from services.chat_service import ChatService
from services.llm_service import LLMService
from services.rag_service import RAGService
from repositories.chat_repository import ChatRepository
from auth.dependency import get_current_user
from utils.rate_limit import limiter

import logging

router = APIRouter()

# Module-level dependency defaults (avoid calling Depends() in function arg defaults per ruff B008)
_user_dep = Depends(get_current_user)
_chat_service_dep = Depends()
_chat_repository_dep = Depends()
_llm_service_dep = Depends()

_logger = logging.getLogger("symptomscope.api.chat")


class ExplainRequest(BaseModel):
    disease: str
    confidence: float
    severity: str
    symptoms: list[str] = []
    precautions: list[str] = []
    alternatives: list[str] = []


class FollowUpRequest(BaseModel):
    disease: str
    confidence: float
    severity: str
    symptoms: list[str] = []


class MedicalQuestion(BaseModel):
    question: str


@router.post("/chat/session", response_model=ChatSessionResponse)
@limiter.limit("10/minute")
async def create_chat_session(
    request: Request,
    input_data: ChatSessionCreate,
    user_id: str = _user_dep,
    chat_service: ChatService = _chat_service_dep,
    chat_repository: ChatRepository = _chat_repository_dep,
):
    prediction_context = None
    if input_data.prediction_id:
        from repositories.prediction_repository import PredictionRepository
        from bson.objectid import ObjectId

        pred_repo = PredictionRepository()
        pred = await pred_repo.find_by_id(input_data.prediction_id)
        if pred:
            prediction_context = chat_service.build_context(
                disease=pred.prediction,
                confidence=pred.confidence,
                severity=pred.severity,
                symptoms=pred.symptoms,
            )

    await chat_repository.deactivate_stale_sessions(user_id)

    session = await chat_repository.create_session(
        user_id, prediction_context
    )

    session_id = str(session.pop("_id"))
    return ChatSessionResponse(
        _id=session_id,
        user_id=user_id,
        started_at=session["startedAt"],
        last_activity_at=session["lastActivityAt"],
        is_active=session["isActive"],
        prediction_context=session.get("predictionContext"),
    )


@router.get("/chat/sessions", response_model=ChatSessionListResponse)
@limiter.limit("10/minute")
async def list_chat_sessions(
    request: Request,
    user_id: str = _user_dep,
    chat_repository: ChatRepository = _chat_repository_dep,
):
    sessions = await chat_repository.get_user_sessions(user_id)
    results = []
    for s in sessions:
        sid = str(s.pop("_id"))
        results.append(
            ChatSessionResponse(
                _id=sid,
                user_id=s["userId"],
                started_at=s["startedAt"],
                last_activity_at=s["lastActivityAt"],
                is_active=s["isActive"],
                prediction_context=s.get("predictionContext"),
            )
        )
    return ChatSessionListResponse(sessions=results, total=len(results))


@router.post("/chat/message", response_model=ChatMessageResponse)
@limiter.limit("5/minute")
async def send_message(
    request: Request,
    input_data: MessageSend,
    user_id: str = _user_dep,
    chat_service: ChatService = _chat_service_dep,
    chat_repository: ChatRepository = _chat_repository_dep,
):
    session = await chat_repository.get_session(input_data.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    if session.get("userId") != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    if not session.get("isActive", True):
        raise HTTPException(status_code=400, detail="Session is closed")

    is_valid, error_msg = chat_service.validate_message(input_data.content)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    user_msg = await chat_repository.add_message(
        input_data.session_id, "user", input_data.content
    )

    history = await chat_repository.get_session_messages(input_data.session_id)

    try:
        response = await chat_service.process_message(
            input_data.content,
            history,
            prediction_context=session.get("predictionContext"),
        )
    except Exception as e:
        import logging
        _logger = logging.getLogger("symptomscope.api.chat")
        _logger.warning("Chat message processing failed: %s", e)
        # LLMService already has fallback built-in, but catch any unexpected errors
        response = (
            "I'm sorry, I couldn't process that request right now. "
            "Please try again later or consult a healthcare professional."
        )

    assistant_msg = await chat_repository.add_message(
        input_data.session_id, "assistant", response
    )

    return ChatMessageResponse(
        _id=str(assistant_msg.pop("_id")),
        session_id=input_data.session_id,
        role="assistant",
        content=response,
        created_at=assistant_msg["createdAt"],
    )


@router.get(
    "/chat/messages/{session_id}",
    response_model=list[ChatMessageResponse],
)
@limiter.limit("10/minute")
async def get_messages(
    request: Request,
    session_id: str,
    user_id: str = _user_dep,
    chat_repository: ChatRepository = _chat_repository_dep,
):
    session = await chat_repository.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    if session.get("userId") != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    messages = await chat_repository.get_session_messages(session_id)
    return [
        ChatMessageResponse(
            _id=str(m.pop("_id")),
            session_id=m["sessionId"],
            role=m["role"],
            content=m["content"],
            created_at=m["createdAt"],
        )
        for m in messages
    ]


import logging
_logger = logging.getLogger("symptomscope.api.chat")


@router.post("/chat/explain")
@limiter.limit("10/minute")
async def explain_prediction(
    request: Request,
    input_data: ExplainRequest,
    _user_id: str = _user_dep,
    llm_service: LLMService = _llm_service_dep,
):
    result = await llm_service.explain_prediction(
        disease=input_data.disease,
        confidence=input_data.confidence,
        severity=input_data.severity,
        symptoms=input_data.symptoms,
        precautions=input_data.precautions,
        alternatives=input_data.alternatives,
    )
    return {"explanation": result}


@router.post("/chat/follow-up")
@limiter.limit("10/minute")
async def follow_up_questions(
    request: Request,
    input_data: FollowUpRequest,
    _user_id: str = _user_dep,
    llm_service: LLMService = _llm_service_dep,
):
    result = await llm_service.generate_follow_up_questions(
        disease=input_data.disease,
        confidence=input_data.confidence,
        severity=input_data.severity,
        symptoms=input_data.symptoms,
    )
    return {"follow_up_questions": result if isinstance(result, list) else [result]}


@router.post("/chat/ask")
@limiter.limit("10/minute")
async def ask_medical_question(
    request: Request,
    input_data: MedicalQuestion,
    _user_id: str = _user_dep,
    llm_service: LLMService = _llm_service_dep,
):
    from utils.settings import settings as app_settings
    if not app_settings.gemini_api_key:
        return {
            "answer": "The AI assistant is not configured. Please set GEMINI_API_KEY to enable AI features.",
            "rag_source": False,
        }
    try:
        rag = RAGService()
        answer = await rag.answer_with_rag(input_data.question, llm_service)
        return {"answer": answer, "rag_source": rag.has_documents()}
    except Exception as e:
        _logger.warning("RAG ask failed: %s", e)
        result = await llm_service.answer_medical_question(question=input_data.question)
        return {"answer": result, "rag_source": False}


@router.post("/chat/ask/basic")
@limiter.limit("10/minute")
async def ask_medical_question_basic(
    request: Request,
    input_data: MedicalQuestion,
    _user_id: str = _user_dep,
    llm_service: LLMService = _llm_service_dep,
):
    result = await llm_service.answer_medical_question(
        question=input_data.question,
    )
    return {"answer": result}