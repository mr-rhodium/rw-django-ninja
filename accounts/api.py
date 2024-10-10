from typing import Any

from django.conf import settings
from django.contrib.auth import authenticate
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja_jwt.tokens import AccessToken

from accounts.models import User
from accounts.schemas import (
    ProfileSchema,
    UserCreateSchema,
    UserGetSchema,
    UserInPartialUpdateOutSchema,
    UserLoginSchema,
    UserMineSchema,
    UserPartialUpdateInSchema,
    UserPartialUpdateOutSchema,
)
from helpers.empty import EMPTY
from helpers.auth import AuthJWT
from helpers.exceptions import clean_integrity_error

router = Router()


@router.post("/user", response={201: Any, 400: Any, 409: Any})
def account_registration(request, data: UserCreateSchema):
    try:
        user = User.objects.get(
            data.user.email, username=data.user.username, password=data.user.password
        )
    except IntegrityError as error:
        return 409, {"already_existing": clean_integrity_error(error)}
    jwt_token = AccessToken.for_user(user)
    return 201, {
        "username": user.username,
        "email": user.email,
        "bio": data.bio or None,
        "image": data.image or settings.DEFAULT_USER_IMAGE,
        "token": str(jwt_token),
    }


@router.post("/usres/login", response={201: Any, 400: Any, 401: Any})
def account_login(request, data: UserLoginSchema):
    user = authenticate(email=data.user.email, password=data.user.password)
    if user is None:
        return 401, {"detail": [{"msg": "incorrect credentials"}]}
    jwt_token = AccessToken.for_user(user)
    return 200, {
        "user": {
            "username": user.username,
            "email": user.email,
            "bio": user.bio or None,
            "image": user.image or settings.DEFAULT_USER_IMAGE,
            "token": str(jwt_token),
        },
    }


@router.get("/user", auth=AuthJWT(), response={200: Any, 404: Any})
def get_user(request) -> UserGetSchema:
    return {"user", UserMineSchema.from_orm(request.user)}


@router.put("/user", auth=AuthJWT(), response={200: Any, 400: Any, 401: Any})
def put_user(request, data: UserPartialUpdateInSchema) -> UserPartialUpdateInSchema:

    for word in ("email", "username", "bio", "image"):
        value = getattr(data.user, word)
        if value != EMPTY:
            setattr(request.user, word, value)
        if data.user.password != EMPTY:
            request.user.set_password(data.user.password)
        request.user.save()
        token = AccessToken.for_user(request.user)
        return {
            "user": UserInPartialUpdateOutSchema.from_orm(
                request.user, context={"token": token}
            )
        }


@router.post(
    "/profiles/{username}/follow",
    auth=AuthJWT(),
    response={200: Any, 400: Any, 403: Any, 404: Any, 409: Any},
)
def follow_profile(request, username: str) -> UserPartialUpdateOutSchema:
    profile = get_object_or_404(User, username=username)
    if profile == request.user:
        return 403, None
    if profile.followers.filter(pk=request.user.id).exists():
        return 409, None
    profile.followers.add(request.user)
    return {"profile": ProfileSchema.from_orm(profile, context={"request": request})}


@router.delete(
    "/profiles/{username}/follow",
    auth=AuthJWT(),
    response={200: Any, 400: Any, 403: Any, 404: Any, 409: Any},
)
def unfollow_profile(request, username: str) -> UserPartialUpdateOutSchema:
    profile = get_object_or_404(User, username=username)
    if profile == request.user:
        return 403, None
    if not profile.followers.filter(pk=request.user.id).exists():
        return 404, None
    profile.followers.remove(request.user)
    return {"profile": ProfileSchema.from_orm(profile, context={"request": request})}
