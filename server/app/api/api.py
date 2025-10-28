from fastapi import APIRouter

from app.api.user import router as user_router
from app.api.document import router as docs_router
from app.api.conversation import router as conv_router

router = APIRouter()
router.include_router(router=user_router.router, prefix="/auth")
router.include_router(router=docs_router.router, prefix="/docs")
router.include_router(router=conv_router.router, prefix="/conversation")
