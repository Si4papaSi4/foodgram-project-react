import csv

from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.http import Http404, HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.filters import CustomFilter, IngredientFilter
from api.mixins import NoPatchMixin
from api.permissions import IsAdminIsAuthorReadOnly
from favorited.models import Favorite, ShoppingCart
from recipes.models import Ingredient, IngredientDetail, Recipe, Tag

from .serializers import (IngredientSerializer, RecipeReadSerializer,
                          RecipeSerializer, ShortRecipeReadSerializer,
                          TagSerializer)

User = get_user_model()


class TagViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.RetrieveModelMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(NoPatchMixin):
    queryset = Recipe.objects.all().order_by('-id')
    serializer_class = RecipeSerializer
    permission_classes = (IsAdminIsAuthorReadOnly,
                          permissions.IsAuthenticatedOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CustomFilter

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeReadSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=['post'],
            permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def shopping_cart(self, request, pk=None):
        user = request.user
        try:
            recipe = self.get_object()
        except Http404:
            return Response({"reason": "Рецепта не существует."},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            ShoppingCart.objects.create(user=user, recipe=recipe)
            data = ShortRecipeReadSerializer(recipe).data
            return Response(data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({"reason": "Рецепт уже в списке покупок"},
                            status=status.HTTP_400_BAD_REQUEST)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        user = request.user
        try:
            recipe = self.get_object()
        except Http404:
            return Response({"reason": "Рецепта не существует."},
                            status=status.HTTP_404_NOT_FOUND)
        try:
            ShoppingCart.objects.get(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ShoppingCart.DoesNotExist:
            return Response({"reason": "Рецепта нет в списке покупок"},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'],
            permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def favorite(self, request, pk=None):
        user = request.user
        try:
            recipe = self.get_object()
        except Http404:
            return Response({"reason": "Рецепта не существует."},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            Favorite.objects.create(user=user, recipe=recipe)
            data = ShortRecipeReadSerializer(recipe).data
            return Response(data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({"reason": "Рецепт уже в избранном"},
                            status=status.HTTP_400_BAD_REQUEST)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        user = request.user
        try:
            recipe = self.get_object()
        except Http404:
            return Response({"reason": "Рецепта не существует."},
                            status=status.HTTP_404_NOT_FOUND)
        try:
            Favorite.objects.get(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Favorite.DoesNotExist:
            return Response({"reason": "Рецепта нет в избранном"},
                            status=status.HTTP_400_BAD_REQUEST)

    def get_shopping_list_ingredients(self):
        shopping_list = ShoppingCart.objects.filter(user_id=self.request.user)
        ingredients_dict = {}
        # Не смог придумать как логично использовать ORM "фишки"...

        for item in shopping_list:
            recipe = item.recipe_id
            ingredient_details = IngredientDetail.objects.filter(
                recipe=recipe)
            for detail in ingredient_details:
                ingredient = detail.ingredient
                key = (ingredient.name, ingredient.measurement_unit)
                if key in ingredients_dict:
                    ingredients_dict[key] += detail.amount
                else:
                    ingredients_dict[key] = detail.amount

        ingredients_list = [[name, amount, unit] for (name, unit), amount
                            in ingredients_dict.items()]
        return ingredients_list

    @action(methods=['get'],
            detail=False,
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        cart_list = self.get_shopping_list_ingredients()
        response = HttpResponse(content_type='text/txt; charset=utf-8')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping_list.txt"')
        writer = csv.writer(response)
        writer.writerow(['Ингредиент', 'Количество', 'Единица измерения'])
        for ingredient in cart_list:
            writer.writerow(ingredient)
        return response
