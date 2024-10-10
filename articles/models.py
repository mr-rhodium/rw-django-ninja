import markdown
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db import models
from django.utils.text import slugify
from taggit.managers import TaggableManager

User = get_user_model()


class ArticleQuerySet(models.QuerySet):

    def with_favorites(self, user: AnonymousUser | User) -> models.QuerySet:
        return self.annotate(
            num_favorites=models.Count("favorites", distinct=True),
            is_favorite=(
                models.Exists(
                    User.objects.filter(pk=user.id, favorites=models.OuterRef("pk"))
                )
                if user.is_authenticated
                else models.Value(False, output_field=models.BooleanField())
            ),
        )


ArticleManager = models.Manager.from_queryset(ArticleQuerySet)


class Article(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(
        max_length=255, unique=True, blank=True, help_text="Title of the article"
    )
    summary = models.TextField(blank=True, help_text="Summary of the article")
    content = models.TextField(blank=True, help_text="Content of the article")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    tags = TaggableManager()
    favorites = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="favorites"
    )
    slug = models.SlugField(
        max_length=255, unique=True, blank=True, help_text="Slug of the article"
    )

    objects = ArticleManager()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def as_markdown(self) -> str:
        return markdown.markdown(self.content, safe_mode="escape", extensions=["extra"])
