# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from app.models.like import Like


class LikeRepository:
    def __init__(self, db: Session):
        self.db = db

    def like_post(self, user_id: int, post_id: int) -> Like:
        like = Like(user_id=user_id, post_id=post_id)
        self.db.add(like)
        self.db.commit()
        self.db.refresh(like)
        return like

    def unlike_post(self, user_id: int, post_id: int) -> bool:
        like = (
            self.db.query(Like)
            .filter(Like.user_id == user_id, Like.post_id == post_id)
            .first()
        )
        if like:
            self.db.delete(like)
            self.db.commit()
            return True
        return False

    def is_liked(self, user_id: int, post_id: int) -> bool:
        return (
            self.db.query(Like)
            .filter(Like.user_id == user_id, Like.post_id == post_id)
            .first()
            is not None
        )

    def get_likes_count(self, post_id: int) -> int:
        return self.db.query(Like).filter(Like.post_id == post_id).count()
