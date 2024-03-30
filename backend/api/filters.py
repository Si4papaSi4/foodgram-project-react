import django_filters

from recipes.models import Ingredient, Recipe


class CustomFilter(django_filters.FilterSet):
    tags = django_filters.CharFilter(method='filter_by_tags')
    author = django_filters.CharFilter(field_name='author__id')

    def filter_by_tags(self, queryset, name, value):
        tags = self.request.GET.getlist('tags')
        return queryset.filter(tags__slug__in=tags).distinct()

    class Meta:
        model = Recipe
        fields = ['tags', 'author']


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(method='filter_by_name')

    def filter_by_name(self, queryset, name, value):
        param = value
        return queryset.filter(name__startswith=param).distinct()

    class Meta:
        model = Ingredient
        fields = ['name']
