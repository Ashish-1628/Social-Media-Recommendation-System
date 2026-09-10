from typing import List

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.database import get_db
from app.models.comment import Comment
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.common import MessageResponse
from app.schemas.post import PostCreate, PostResponse, PostUpdate
from app.services.post_service import PostService

router = APIRouter(prefix="/posts", tags=["Posts"])


def _respond(post, svc: PostService, uid: int) -> PostResponse:
    return PostResponse(**svc.enrich(post, uid))


@router.get("/feed", response_model=List[PostResponse])
def get_feed(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Personalised feed: posts from users you follow, newest first."""
    svc = PostService(db)
    posts = svc.get_feed(current_user.id, skip, limit)
    return [_respond(p, svc, current_user.id) for p in posts]


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    data: PostCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    svc = PostService(db)
    post = svc.create_post(data, current_user)
    return _respond(post, svc, current_user.id)


@router.get("/{post_id}", response_model=PostResponse)
def get_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    svc = PostService(db)
    post = svc.get_post(post_id)
    return _respond(post, svc, current_user.id)


@router.put("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    data: PostUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    svc = PostService(db)
    post = svc.update_post(post_id, data, current_user)
    return _respond(post, svc, current_user.id)


@router.delete("/{post_id}", response_model=MessageResponse)
def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    PostService(db).delete_post(post_id, current_user)
    return MessageResponse(message="Post deleted successfully")


@router.post("/{post_id}/like", response_model=MessageResponse)
def like_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    PostService(db).like_post(post_id, current_user)
    return MessageResponse(message="Post liked")


@router.delete("/{post_id}/like", response_model=MessageResponse)
def unlike_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    PostService(db).unlike_post(post_id, current_user)
    return MessageResponse(message="Post unliked")


@router.get("/{post_id}/comments", response_model=List[CommentResponse])
def get_comments(post_id: int, db: Session = Depends(get_db)):
    return PostService(db).get_post(post_id).comments


@router.post(
    "/{post_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_comment(
    post_id: int,
    data: CommentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    PostService(db).get_post(post_id)  # validate existence
    comment = Comment(content=data.content, author_id=current_user.id, post_id=post_id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment
