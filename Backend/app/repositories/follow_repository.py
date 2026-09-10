from typing import List

# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from app.models.follow import Follow
from app.models.user import User


class FollowRepository:
    def __init__(self, db: Session):
        self.db = db

    def follow(self, follower_id: int, followed_id: int) -> Follow:
        follow = Follow(follower_id=follower_id, followed_id=followed_id)
        self.db.add(follow)
        self.db.commit()
        self.db.refresh(follow)
        return follow

    def unfollow(self, follower_id: int, followed_id: int) -> bool:
        follow = (
            self.db.query(Follow)
            .filter(Follow.follower_id == follower_id, Follow.followed_id == followed_id)
            .first()
        )
        if follow:
            self.db.delete(follow)
            self.db.commit()
            return True
        return False

    def is_following(self, follower_id: int, followed_id: int) -> bool:
        return (
            self.db.query(Follow)
            .filter(Follow.follower_id == follower_id, Follow.followed_id == followed_id)
            .first()
            is not None
        )

    def get_followers(self, user_id: int) -> List[User]:
        return (
            self.db.query(User)
            .join(Follow, Follow.follower_id == User.id)
            .filter(Follow.followed_id == user_id)
            .all()
        )

    def get_following(self, user_id: int) -> List[User]:
        return (
            self.db.query(User)
            .join(Follow, Follow.followed_id == User.id)
            .filter(Follow.follower_id == user_id)
            .all()
        )

    def get_followers_ids(self, user_id: int) -> List[int]:
        rows = self.db.query(Follow.follower_id).filter(Follow.followed_id == user_id).all()
        return [r[0] for r in rows]

    def get_following_ids(self, user_id: int) -> List[int]:
        rows = self.db.query(Follow.followed_id).filter(Follow.follower_id == user_id).all()
        return [r[0] for r in rows]

    def count_followers(self, user_id: int) -> int:
        return self.db.query(Follow).filter(Follow.followed_id == user_id).count()

    def count_following(self, user_id: int) -> int:
        return self.db.query(Follow).filter(Follow.follower_id == user_id).count()
