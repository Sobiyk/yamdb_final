import django_filters
from reviews.models import Title


class TitleFilter(django_filters.FilterSet):
    """Фильтр по полям объекта модели произведения"""
    genre = django_filters.CharFilter(lookup_expr='slug')
    category = django_filters.CharFilter(lookup_expr='slug')

    class Meta:
        model = Title
        fields = ['year', 'name']
