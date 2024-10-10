from __future__ import annotations

from uuid import uuid4, UUID

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(
        self, email: str, password: str | None = None, **extra_fields
    ) -> User:
        user = User(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def create_superuser(
        self, email: str, password: str | None = None, **extra_fields
    ) -> User:
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    first_name = None
    last_name = None

    id: UUID = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    email: str = models.EmailField(unique=True, help_text="Email address")
    username: str = models.CharField(unique=True, max_length=90, help_text="Username")
    bio: str = models.TextField(help_text="Bio")
    image: str = models.URLField(null=True, blank=True, help_text="Image url")

    following = models.ManyToManyField("self", blank=True, symmetrical=False)

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    objects = UserManager()

    def get_full_name(self) -> str:
        return (
            f"{self.first_name} {self.last_name}"
            if self.first_name and self.last_name
            else self.email
        )

    def get_short_name(self) -> str:
        return (
            f"{self.first_name} {self.last_name}"
            if self.first_name and self.last_name
            else self.email
        )

    def is_following(self, other_user):
        return (
            other_user.followers.filter(pk=self.id).exists()
            if self.is_authenticated
            else False
        )
