from typing import Optional

from app.core.base.filter_set import FilterSet
from .models import Post, Comment


class PostFilter(FilterSet):
    model = Post

    class Parameters(FilterSet.Parameters):
        category: Optional[int] = None
        creator: Optional[int] = None
        author_club: Optional[int] = None

    class SearchFields(FilterSet.SearchFields):
        title: str
        content: str


class CommentFilter(FilterSet):
    model = Comment

    class Parameters(FilterSet.Parameters):
        creator: Optional[int] = None
        post: Optional[int] = None
        reply_to: Optional[int] = None

    class SearchFields(FilterSet.SearchFields):
        content: str
