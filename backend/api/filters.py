import django_filters
from django.db.models import Exists, OuterRef

from favorited.models import Favorite, ShoppingCart
from recipes.models import Ingredient, Recipe


class CustomFilter(django_filters.FilterSet):
    tags = django_filters.Filter(method='filter_by_tags')
    # ModelMultipleChoiceFilter не сработал, тк фильтр не по id
    # А to_field_name='slug' не работает
    is_favorited = django_filters.Filter(method='filter_favorited')
    is_in_shopping_cart = django_filters.Filter(method='filter_shopping_cart')

    # BooleanFilter работает только с True False, у нас 1 0 (

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']

    def filter_by_tags(self, queryset, name, value):
        tags = self.request.GET.getlist('tags')
        return queryset.filter(tags__slug__in=tags).distinct()

    def filter_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            subquery = Favorite.objects.filter(
                user=self.request.user,
                recipe=OuterRef('pk')
            )
            queryset = queryset.filter(Exists(subquery))
            # Ниче не понял, кого по юзеру, queryset же Recipe...
        return queryset

    def filter_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            subquery = ShoppingCart.objects.filter(
                user=self.request.user,
                recipe=OuterRef('pk')
            )
            queryset = queryset.filter(Exists(subquery))
        return queryset


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(method='filter_by_name')

    def filter_by_name(self, queryset, name, value):
        return queryset.filter(name__startswith=value)

    class Meta:
        model = Ingredient
        fields = ['name']
