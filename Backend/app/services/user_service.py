from typing import List

# pyrefly: ignore [missing-import]
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.follow_repository import FollowRepository
from app.repositories.post_repository import PostRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserUpdate, UserStats


class UserService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.follow_repo = FollowRepository(db)
        self.post_repo = PostRepository(db)

    def get_profile(self, username: str) -> User:
        user = self.user_repo.get_by_username(username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def get_stats(self, user_id: int) -> UserStats:
        return UserStats(
            followers_count=self.follow_repo.count_followers(user_id),
            following_count=self.follow_repo.count_following(user_id),
            posts_count=self.post_repo.count_by_author(user_id),
        )

    def update_profile(self, user: User, data: UserUpdate) -> User:
        return self.user_repo.update(user, bio=data.bio, avatar_url=data.avatar_url)

    def delete_account(self, user: User) -> None:
        self.user_repo.delete(user)

    def search(self, query: str) -> List[User]:
        return self.user_repo.search(query)

    def get_followers(self, username: str) -> List[User]:
        user = self.get_profile(username)
        return self.follow_repo.get_followers(user.id)

    def get_following(self, username: str) -> List[User]:
        user = self.get_profile(username)
        return self.follow_repo.get_following(user.id)
