from typing import List

# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.database import get_db
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.user import UserPublic, UserResponse, UserStats, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/search", response_model=List[UserPublic])
def search_users(
    q: str = Query(..., min_length=1, description="Search term"),
    db: Session = Depends(get_db),
):
    """Search users by username or bio."""
    return UserService(db).search(q)


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_active_user)):
    """Get the authenticated user's full profile."""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update bio and/or avatar URL."""
    return UserService(db).update_profile(current_user, data)


@router.delete("/me", response_model=MessageResponse)
def delete_account(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Permanently delete the authenticated user's account."""
    UserService(db).delete_account(current_user)
    return MessageResponse(message="Account deleted successfully")


@router.get("/{username}", response_model=UserPublic)
def get_user_profile(username: str, db: Session = Depends(get_db)):
    """Get a public profile by username."""
    return UserService(db).get_profile(username)


@router.get("/{username}/stats", response_model=UserStats)
def get_user_stats(username: str, db: Session = Depends(get_db)):
    """Get follower/following/post counts for a user."""
    svc = UserService(db)
    user = svc.get_profile(username)
    return svc.get_stats(user.id)


@router.get("/{username}/followers", response_model=List[UserPublic])
def get_followers(username: str, db: Session = Depends(get_db)):
    return UserService(db).get_followers(username)


@router.get("/{username}/following", response_model=List[UserPublic])
def get_following(username: str, db: Session = Depends(get_db)):
    return UserService(db).get_following(username)
