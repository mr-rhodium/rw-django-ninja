from django.db import models
from django.conf import settings
from articles.models import Article


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]
        # unique_together = (("user", "article"),)
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
