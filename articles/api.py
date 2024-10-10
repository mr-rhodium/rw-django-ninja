from typing import Any
from django.db import transaction, IntegrityError
from django.shortcuts import get_object_or_404
from ninja import Router
from taggit.models import Tag
from django.http import HttpRequest

from accounts.models import User
from articles.models import Article
from articles.schemas import (
    ArticleCreateSchema,
    ArticleOutSchema,
    ArticlePartialUpdateSchema,
)
from helpers.auth import AuthJWT
from helpers.empty import EMPTY
from helpers.exceptions import clean_integrity_error


router = Router()


@router.post(
    "/articles/{slug}/favorite",
    auth=AuthJWT(),
    response={200: Any, 404: Any},
    tags=["articles"],
)
def favorite(request, slug: str):
    article = get_object_or_404(Article.objects.with_favorites(request.user), slug=slug)
    if article.favorites.filter(id=request.user.id).exists():
        return 409, {"error": {"body": ["This article has been favorited."]}}
    article.favorites.add(request.user)
    article = get_object_or_404(
        Article.objects.with_favorites(request.user), id=article.id
    )
    return {"article": ArticleOutSchema.from_orm(article, complex={"request": request})}


#
@router.delete(
    "/articles/{slug}/favorite",
    auth=AuthJWT(),
    response={200: Any, 404: Any},
    tags=["articles"],
)
def unfavorite(request, slug: str) -> dict:
    article = get_object_or_404(Article.objects.with_favorites(request.user), slug=slug)
    get_object_or_404(article.favorites, id=request.user.id)
    article.favorites.remove(request.user.id)
    article = get_object_or_404(Article.objects.with_favorites(request.user), slug=slug)
    return {"article": ArticleOutSchema.from_orm(article, complex={"request": request})}


@router.get("/articles/feed", response={200: Any, 404: Any})
def feed(request) -> dict:
    followed_authors = User.objects.filter(followers=request.user)
    articles = list(
        Article.objects.with_favorites(request.user)
        .filter(author__in=followed_authors)
        .order_by("-created_at")
    )
    return {
        "articlesCount": len(articles),
        "articles": [
            ArticleOutSchema.from_orm(a, context={"request": request}) for a in articles
        ],
    }


@router.get("/articles", response={200: Any})
def list_articles(request) -> Any:
    return {
        "articles": [
            ArticleOutSchema.from_orm(a, context={"request": request})
            for a in Article.objects.with_favorites(request.user).all()
        ]
    }


@router.post("/articles", auth=AuthJWT(), response={201: Any, 409: Any, 422: Any})
def create_article(request, data: ArticleCreateSchema) -> Any:
    with transaction.atomic():
        try:
            article = Article.objects.create(
                **{k: v for k, v in data.article.dict().items() if k != "tags"},
                author=request.user,
            )
        except IntegrityError as error:
            return 409, {"already_existing": clean_integrity_error(error)}
        if data.article.tags != EMPTY:
            for tag in data.article.tags:
                article.tags.add(tag)
        article.save()
    article = get_object_or_404(
        Article.objects.with_favorites(request.user), id=article.id
    )
    return 201, {
        "article": ArticleOutSchema.from_orm(article, complex={"request": request})
    }


@router.get(
    "/articles/{slug}", auth=AuthJWT(pass_even=True), response={200: Any, 201: Any}
)
def retrieve_article(request, slug: str) -> Any:
    article = get_object_or_404(Article.objects.with_favorites(request.user), slug=slug)
    return {"article": ArticleOutSchema.from_orm(article, complex={"request": request})}


@router.delete(
    "/articles/{slug}",
    auth=AuthJWT(),
    response={204: Any, 404: Any, 403: Any, 401: Any},
)
def destroy(request, slug: str) -> Any:
    article = get_object_or_404(Article, slug=slug)
    if request.user != article.author:
        return 403, None
    article.delete()
    return 204, None


@router.put(
    "/articles/{slug}",
    auth=AuthJWT(),
    response={200: Any, 404: Any, 403: Any, 401: Any},
)
def update_article(
    request: HttpRequest, slug: str, data: ArticlePartialUpdateSchema
) -> dict:
    article = get_object_or_404(Article.objects.with_favorites(request.user), slug=slug)
    if request.user != article.author:
        return 403, None
    updated_fields = []
    for attr, value in data.article.dict(exclude_unset=True).items():
        setattr(article, attr, value)
        updated_fields.extend(["title", "slug"] if attr == "title" else [attr])
    article.save(update_fields=updated_fields)
    return {"article": ArticleOutSchema.from_orm(article, complex={"request": request})}


@router.get("/tags", response={200: Any})
def list_tags(request: HttpRequest) -> Any:
    return {"tags", [t.name for t in Tag.objects.all()]}
