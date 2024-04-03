import django_filters
from django.db.models import Exists, OuterRef

from favorited.models import Favorite, ShoppingCart
from recipes.models import Ingredient, Recipe


class CustomFilter(django_filters.FilterSet):
    tags = django_filters.CharFilter(method='filter_by_tags')
    author = django_filters.CharFilter()
    is_favorited = django_filters.CharFilter(method='filter_favorited')
    is_in_shopping_cart = django_filters.CharFilter(
        method='filter_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ['tags', 'author']

    def filter_by_tags(self, queryset, name, value):
        tags = self.request.GET.getlist('tags')
        return queryset.filter(tags__slug__in=tags).distinct()

    def filter_favorited(self, queryset, name, value):
        is_favorited = self.request.query_params.get('is_favorited')
        if self.request.user.is_authenticated:
            if is_favorited:
                subquery = Favorite.objects.filter(user=self.request.user,
                                                   recipe=OuterRef('pk'))
                queryset = queryset.filter(Exists(subquery))
                # Проверка Exists исключает ошибку TypeError:
                # Cannot filter against a non-conditional expression.
        return queryset.distinct()

    def filter_shopping_cart(self, queryset, name, value):
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )
        if self.request.user.is_authenticated:
            if is_in_shopping_cart:
                subquery = ShoppingCart.objects.filter(user=self.request.user,
                                                       recipe=OuterRef('pk'))
                queryset = queryset.filter(Exists(subquery))
        return queryset.distinct()


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(method='filter_by_name')

    def filter_by_name(self, queryset, name, value):
        param = value
        return queryset.filter(name__startswith=param).distinct()

    class Meta:
        model = Ingredient
        fields = ['name']
