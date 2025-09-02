from fastapi import APIRouter

from app.api.user import router as user_router
from app.api.conversation import router as conversation_router

router = APIRouter()
router.include_router(router=user_router.router, prefix="/auth")
router.include_router(router=conversation_router.router, prefix="/conversation")
