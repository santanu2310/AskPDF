from fastapi import APIRouter

from app.api.user import router as user_router

router = APIRouter()
router.include_router(router=user_router.router, prefix="/users")
