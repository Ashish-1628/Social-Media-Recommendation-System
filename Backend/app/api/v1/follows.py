from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.database import get_db
from app.models.user import User
from app.repositories.follow_repository import FollowRepository
from app.repositories.user_repository import UserRepository
from app.schemas.follow import FollowResponse

router = APIRouter(prefix="/follows", tags=["Follows"])


@router.post("/{username}", response_model=FollowResponse)
def follow_user(
    username: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Follow a user by username."""
    user_repo = UserRepository(db)
    follow_repo = FollowRepository(db)

    target = user_repo.get_by_username(username)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    if follow_repo.is_following(current_user.id, target.id):
        raise HTTPException(status_code=400, detail="Already following this user")

    follow_repo.follow(current_user.id, target.id)
    return FollowResponse(message=f"Now following @{username}", is_following=True)


@router.delete("/{username}", response_model=FollowResponse)
def unfollow_user(
    username: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Unfollow a user by username."""
    user_repo = UserRepository(db)
    follow_repo = FollowRepository(db)

    target = user_repo.get_by_username(username)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    if not follow_repo.unfollow(current_user.id, target.id):
        raise HTTPException(status_code=400, detail="Not following this user")

    return FollowResponse(message=f"Unfollowed @{username}", is_following=False)
