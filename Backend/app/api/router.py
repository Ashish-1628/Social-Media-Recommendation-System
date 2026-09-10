from fastapi import APIRouter

from app.api.v1 import auth, follows, posts, recommendations, users

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/api/v1")
api_router.include_router(users.router, prefix="/api/v1")
api_router.include_router(posts.router, prefix="/api/v1")
api_router.include_router(follows.router, prefix="/api/v1")
api_router.include_router(recommendations.router, prefix="/api/v1")
