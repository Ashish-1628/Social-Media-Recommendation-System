from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.post import Post
from app.models.user import User
from app.repositories.like_repository import LikeRepository
from app.repositories.post_repository import PostRepository
from app.schemas.post import PostCreate, PostUpdate


class PostService:
    def __init__(self, db: Session):
        self.post_repo = PostRepository(db)
        self.like_repo = LikeRepository(db)

    def _enrich(self, post: Post, current_user_id: int) -> dict:
        """Build a dict that matches PostResponse shape with computed fields."""
        return {
            "id": post.id,
            "content": post.content,
            "image_url": post.image_url,
            "author_id": post.author_id,
            "author": post.author,
            "likes_count": self.like_repo.get_likes_count(post.id),
            "comments_count": len(post.comments),
            "is_liked": self.like_repo.is_liked(current_user_id, post.id),
            "created_at": post.created_at,
            "updated_at": post.updated_at,
        }

    def create_post(self, data: PostCreate, author: User) -> Post:
        return self.post_repo.create(data, author.id)

    def get_post(self, post_id: int) -> Post:
        post = self.post_repo.get_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        return post

    def update_post(self, post_id: int, data: PostUpdate, current_user: User) -> Post:
        post = self.get_post(post_id)
        if post.author_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to edit this post")
        return self.post_repo.update(
            post,
            content=data.content,
            image_url=data.image_url,
        )

    def delete_post(self, post_id: int, current_user: User) -> None:
        post = self.get_post(post_id)
        if post.author_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this post")
        self.post_repo.delete(post)

    def get_feed(self, user_id: int, skip: int = 0, limit: int = 20) -> List[Post]:
        return self.post_repo.get_feed_for_user(user_id, skip, limit)

    def like_post(self, post_id: int, user: User) -> None:
        self.get_post(post_id)  # validate existence
        if self.like_repo.is_liked(user.id, post_id):
            raise HTTPException(status_code=400, detail="Post already liked")
        self.like_repo.like_post(user.id, post_id)

    def unlike_post(self, post_id: int, user: User) -> None:
        self.get_post(post_id)  # validate existence
        if not self.like_repo.unlike_post(user.id, post_id):
            raise HTTPException(status_code=400, detail="Post was not liked")

    def enrich(self, post: Post, current_user_id: int) -> dict:
        return self._enrich(post, current_user_id)
