import csv

from api.favorited.serializers import (FavoriteSerializer,
                                       ShoppingCartSerializer)
from api.filters import CustomFilter, IngredientFilter
from api.mixins import NoPatchMixin
from api.permissions import IsAdminIsAuthorReadOnly
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from favorited.models import ShoppingCart
from recipes.models import Ingredient, IngredientDetail, Recipe, Tag
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import (IngredientSerializer, RecipeReadSerializer,
                          RecipeSerializer, TagSerializer)

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(NoPatchMixin):
    queryset = Recipe.objects.all()
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
        data = {
            'recipe': self.kwargs.get('pk'),
            'user': request.user.id
        }
        serializer = ShoppingCartSerializer(
            data=data,
            context={
                'request': request
            }
        )
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(data=serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        data = {
            'recipe': self.get_object().id,
            'user': request.user.id
        }
        serializer = ShoppingCartSerializer(
            data=data,
            context={
                'request': request
            }
        )
        if serializer.is_valid():
            serializer.destroy(serializer.validated_data)
        else:
            return Response(data=serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'],
            permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def favorite(self, request, pk=None):
        data = {
            'recipe': self.kwargs.get('pk'),
            'user': request.user.id
        }
        serializer = FavoriteSerializer(
            data=data,
            context={
                'request': request
            }
        )
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(data=serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        data = {
            'recipe': self.get_object().id,
            'user': request.user.id
        }
        serializer = FavoriteSerializer(
            data=data,
            context={
                'request': request
            }
        )
        if serializer.is_valid():
            serializer.destroy(serializer.validated_data)
        else:
            return Response(data=serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_shopping_list_ingredients(self):
        shopping_list = ShoppingCart.objects.filter(
            user_id=self.request.user
        ).values('recipe_id')
        ingredient_details = IngredientDetail.objects.filter(
            recipe_id__in=shopping_list
        ).values('ingredient__name',
                 'ingredient__measurement_unit').annotate(
            total_amount=Sum('amount'))
        ingredients_list = [
            [ingredient['ingredient__name'], ingredient['total_amount'],
             ingredient['ingredient__measurement_unit']]
            for ingredient in ingredient_details
        ]
        return ingredients_list

    @action(methods=['get'],
            detail=False,
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        cart_list = self.get_shopping_list_ingredients()
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping_list.txt"')
        writer = csv.writer(response)
        writer.writerow(['Ингредиент', 'Количество', 'Единица измерения'])
        for ingredient in cart_list:
            writer.writerow(ingredient)
        return response
