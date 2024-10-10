import django_filters

from articles.models import Article


class ArticleFilter(django_filters.FilterSet):
    tag = django_filters.CharFilter(method="tag_filter")
    author = django_filters.CharFilter(method="author_filter")
    favorite = django_filters.BooleanFilter(
        field_name="favorites", method="is_favorites_filter", label="Favorites"
    )
    limit = django_filters.NumberFilter(method="limit_filter", label="Limit")
    offset = django_filters.NumberFilter(method="offset_filter", label="Offset")

    class Meta:
        model = Article
        fields = ["tag", "author", "favorite", "limit", "offset"]

    def tag_filter(self, queryset, field_name, value):
        return queryset.filter(tags__name_in=[value])

    def author_filter(self, queryset, field_name, value):
        return queryset.filter(author__username__icontains=value)

    def is_favorites_filter(self, queryset, field_name, value):
        return queryset.filter(favorites__username__icontains=value)

    def limit_filter(self, queryset, field_name, value):
        return queryset[:value]

    def offset_filter(self, queryset, field_name, value):
        return queryset[:value]
