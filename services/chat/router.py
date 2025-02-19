from fastapi import APIRouter
from openai import OpenAI

from models.http_params import QueryRequest
from services.chat.handler import ask_llm_with_tracing


def get_router(llm: OpenAI) -> APIRouter:
    chat_router = APIRouter(prefix="/chat", tags=["chat"])

    @chat_router.get('/query')
    def query(request: QueryRequest):
        return ask_llm_with_tracing(request.question, llm)

    return chat_router
