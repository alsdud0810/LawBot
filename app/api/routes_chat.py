from fastapi import APIRouter

from app.models.request import ChatRequest
from app.models.response import ChatResponse
from app.rag.generator import DeterministicGenerator
from app.rag.pipeline import RagPipeline

pipeline = RagPipeline(None, DeterministicGenerator())

router = APIRouter(prefix="/api/v1", tags=["chat"])


def set_pipeline(new_pipeline: RagPipeline) -> None:
    global pipeline
    pipeline = new_pipeline


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    return pipeline.answer(request.question, request.language)
