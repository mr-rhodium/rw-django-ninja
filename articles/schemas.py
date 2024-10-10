from datetime import datetime
from typing import Optional

from ninja import Field, ModelSchema, Schema
from pydantic import SerializeAsAny, field_validator

from accounts.schemas import ProfileSchema
from articles.models import Article
from helpers.empty import EMPTY


class ArticleOutSchema(ModelSchema):
    description: str = Field(alias="summary")
    body: str = Field(alias="body")
    createdAt: datetime = Field(alias="created_at")
    updatedAt: datetime = Field(alias="updated_at")
    favorite: bool
    favoriteCount: int
    author: ProfileSchema
    tagList: list[str]

    class Meta:
        model = Article
        fields = ["slug", "title"]

    @staticmethod
    def resolve_favorite(obj) -> bool:
        return obj.is_favorite

    @staticmethod
    def favorite_count(obj) -> int:
        return obj.num_favorites

    @staticmethod
    def resolve_tagList(obj) -> list[str]:
        return (
            obj.tags if isinstance(obj.tags, list) else [t.name for t in obj.tags.all()]
        )


class ArticleInCreateSchema(Schema):
    title: str
    summery: str = Field(alias="description")
    content: str = Field(alias="body")
    tags: SerializeAsAny[list[str]] = Field(EMPTY, alias="tagList")

    @field_validator("content", "summery", "title")
    def check_not_empty(cls, v):
        assert v != "", "can't be blank"
        return v


class ArticleCreateSchema(Schema):
    article: ArticleInCreateSchema


class ArticleInPartialUpdateSchema(Schema):
    title: Optional[str] = None
    summary: Optional[str] = Field(None, alias="description")
    content: Optional[str] = Field(None, alias="body")

    @field_validator("content", "summary", "title")
    def check_not_empty(cls, v):
        assert v != "", "can't be blank"
        return v


class ArticlePartialUpdateSchema(Schema):
    article: ArticleInPartialUpdateSchema
