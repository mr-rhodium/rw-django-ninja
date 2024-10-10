from ninja import ModelSchema, Schema
from comments.models import Comment
from datetime import datetime
from typing import Optional


class CommentSchema(ModelSchema):
    user: Optional[str]
    article: Optional[str]
    text: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Meta:
        model = Comment
        fields = ["user", "article", "text", "created_at", "updated_at"]


class CommentsOutSchema(Schema):
    comments: list[CommentSchema]
