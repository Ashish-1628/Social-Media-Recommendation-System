import math
from typing import Generic, List, Type, TypeVar

from sqlalchemy.orm import Query

from app.schemas.common import PaginatedResponse

T = TypeVar("T")


def paginate(query: Query, page: int, size: int, schema: Type) -> PaginatedResponse:
    """
    Paginate a SQLAlchemy query and return a PaginatedResponse.

    Args:
        query:  Unexecuted SQLAlchemy query object.
        page:   1-based page number.
        size:   Number of items per page.
        schema: Pydantic schema class to serialise each item.
    """
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    pages = math.ceil(total / size) if size > 0 else 0
    return PaginatedResponse(
        items=[schema.model_validate(item) for item in items],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )
