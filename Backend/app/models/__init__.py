# Re-export all models so Alembic and SQLAlchemy can discover them
# and so `import app.models` in main.py registers all tables with Base.metadata
from app.models.user import User
from app.models.post import Post
from app.models.follow import Follow
from app.models.like import Like
from app.models.comment import Comment
from app.models.tag import Tag, PostTag, UserInterest

__all__ = ["User", "Post", "Follow", "Like", "Comment", "Tag", "PostTag", "UserInterest"]
