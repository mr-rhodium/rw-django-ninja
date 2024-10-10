from typing import Optional, Annotated
from django.conf import settings
from ninja import ModelSchema, Schema
from pydantic import AfterValidator, EmailStr, ValidationInfo, field_validator

from accounts.models import User
from helpers.empty import EMPTY


def none_to_blank(value: Optional[str], info: ValidationInfo) -> str:
    return "" if value is None else value


class ProfileSchema(ModelSchema):
    following: bool
    bio: Optional[str]
    image: Optional[str]

    class Meta:
        model = User
        fields = ["username"]

    @staticmethod
    def resolve_following(obj, context) -> bool:
        user = context.get("request").user
        return (
            obj.followers.filter(id=user.id).exists()
            if user and user.is_authenticated
            else False
        )

    @staticmethod
    def resolve_bio(obj, context) -> str | None:
        return obj.bio or None

    @staticmethod
    def resolve_image(obj, context) -> str:
        return obj.image or settings.DEFAULT_USER_IMAGE


class UserInCreateSchema(ModelSchema):
    email: EmailStr

    class Meta:
        model = User
        fields = ["username", "password", "email"]

    @field_validator("email", "password", "username", check_fields=False)
    @classmethod
    def non_empty(cls, v: str) -> str:
        if not v:
            raise ValueError("can't be blank")
        return v


class UserCreateSchema(Schema):
    user: UserInCreateSchema


class UserInLoginSchema(ModelSchema):

    class Meta:
        model = User
        fields = ["username", "password"]

    @field_validator("email", "password", check_fields=False)
    @classmethod
    def non_empty(cls, v: str) -> str:
        if not v:
            raise ValueError("can't be blank")
        return v


class UserLoginSchema(Schema):
    user: UserInLoginSchema


class UserMineSchema(ModelSchema):
    email: EmailStr

    class Meta:
        model = User
        fields = ["username", "bio", "image", "username"]


class UserGetSchema(Schema):
    user: UserMineSchema


class UserInPartialUpdateInSchema(Schema):
    email: Annotated[EmailStr, AfterValidator(none_to_blank)] = EMPTY
    bio: Annotated[Optional[str], AfterValidator(none_to_blank)] = EMPTY
    image: Annotated[Optional[str], AfterValidator(none_to_blank)] = EMPTY
    username: Annotated[Optional[str], AfterValidator(none_to_blank)] = EMPTY
    password: Annotated[Optional[str], AfterValidator(none_to_blank)] = EMPTY


class UserPartialUpdateInSchema(Schema):
    user: UserInPartialUpdateInSchema


class UserInPartialUpdateOutSchema(UserMineSchema):
    token: str

    @staticmethod
    def resolve_token(obj, context) -> str:
        return str(context.get("token") if context is not None else "")


class UserPartialUpdateOutSchema(Schema):
    user: UserInPartialUpdateOutSchema
