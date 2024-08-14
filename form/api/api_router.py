from fastapi import APIRouter

from form.api.endpoints import chat, check, sessions, uuid, vectorstore

api_router = APIRouter()
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
api_router.include_router(
    vectorstore.router, prefix="/vectorstore", tags=["Vectorstore"]
)
api_router.include_router(uuid.router, prefix="/uuid", tags=["UUID"])
api_router.include_router(check.router, tags=["Checks"])
