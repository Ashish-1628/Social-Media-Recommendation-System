from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.models.follow import Follow
from app.models.like import Like
from app.models.post import Post
from app.schemas.post import PostCreate


class PostRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, post_id: int) -> Optional[Post]:
        return self.db.query(Post).filter(Post.id == post_id).first()

    def create(self, data: PostCreate, author_id: int) -> Post:
        post = Post(content=data.content, image_url=data.image_url, author_id=author_id)
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post

    def update(self, post: Post, **kwargs) -> Post:
        for key, value in kwargs.items():
            if value is not None:
                setattr(post, key, value)
        self.db.commit()
        self.db.refresh(post)
        return post

    def delete(self, post: Post) -> None:
        self.db.delete(post)
        self.db.commit()

    def get_by_author(self, author_id: int, skip: int = 0, limit: int = 20) -> List[Post]:
        return (
            self.db.query(Post)
            .filter(Post.author_id == author_id)
            .order_by(desc(Post.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_feed_for_user(self, user_id: int, skip: int = 0, limit: int = 20) -> List[Post]:
        """Posts from users that user_id follows, newest first."""
        following_ids = (
            self.db.query(Follow.followed_id)
            .filter(Follow.follower_id == user_id)
            .subquery()
        )
        return (
            self.db.query(Post)
            .filter(Post.author_id.in_(following_ids))
            .order_by(desc(Post.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_trending(self, hours: int = 24, limit: int = 20) -> List[Post]:
        """Posts with most likes in the last N hours."""
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        return (
            self.db.query(Post)
            .outerjoin(Like, Post.id == Like.post_id)
            .filter(Post.created_at >= since)
            .group_by(Post.id)
            .order_by(desc(func.count(Like.id)))
            .limit(limit)
            .all()
        )

    def count_by_author(self, author_id: int) -> int:
        return self.db.query(Post).filter(Post.author_id == author_id).count()
