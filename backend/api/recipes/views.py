import csv

from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef
from django.db.utils import IntegrityError
from django.http import Http404, HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import exceptions, mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from api.filters import CustomFilter, IngredientFilter
from api.mixins import NoPatchMixin
from api.pagination import CustomPagination
from api.permissions import IsAdminIsAuthorReadOnly
from recipes.models import (Favorite, Ingredient, IngredientDetail, Recipe,
                            ShoppingCart, Tag)

from .serializers import (CustomUserSerializer, IngredientSerializer,
                          RecipeReadSerializer, RecipeSerializer,
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

    def get_queryset(self):
        queryset = super().get_queryset()
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart')

        if self.request.user.is_authenticated:
            if is_favorited == '1':
                subquery = Favorite.objects.filter(user=self.request.user,
                                                   recipe=OuterRef('pk'))
                queryset = queryset.filter(Exists(subquery))
            elif is_favorited == '0':
                subquery = Favorite.objects.filter(user=self.request.user,
                                                   recipe=OuterRef('pk'))
                queryset = queryset.exclude(Exists(subquery))

            if is_in_shopping_cart == '1':
                subquery = ShoppingCart.objects.filter(user=self.request.user,
                                                       recipe=OuterRef('pk'))
                queryset = queryset.filter(Exists(subquery))
            elif is_in_shopping_cart == '0':
                subquery = ShoppingCart.objects.filter(user=self.request.user,
                                                       recipe=OuterRef('pk'))
                queryset = queryset.exclude(Exists(subquery))

        return queryset.distinct()

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeReadSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        try:
            serializer.save(author=self.request.user)
        except IntegrityError:
            raise exceptions.ValidationError('This recipe already exists',
                                             code=400)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def shopping_cart(self, request, pk=None):
        user = request.user
        try:
            recipe = self.get_object()
        except Http404:
            if request.method == "POST":
                return Response({"reason": "Рецепта не существует."},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"reason": "Рецепта не существует."},
                                status=status.HTTP_404_NOT_FOUND)
        if request.method == "POST":
            try:
                ShoppingCart.objects.create(user=user, recipe=recipe)
                data = RecipeReadSerializer(recipe,
                                            context={'request': request}).data
                del data['ingredients']
                del data['tags']
                del data['author']
                del data['text']
                del data['is_favorited']
                del data['is_in_shopping_cart']
                return Response(data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({"reason": "Рецепт уже в списке покупок"},
                                status=status.HTTP_400_BAD_REQUEST)
        elif request.method == "DELETE":
            try:
                ShoppingCart.objects.get(user=user, recipe=recipe).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except ShoppingCart.DoesNotExist:
                return Response({"reason": "Рецепта нет в списке покупок"},
                                status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def favorite(self, request, pk=None):
        user = request.user
        try:
            recipe = self.get_object()
        except Http404:
            if request.method == "POST":
                return Response({"reason": "Рецепта не существует."},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"reason": "Рецепта не существует."},
                                status=status.HTTP_404_NOT_FOUND)
        if request.method == "POST":
            try:
                Favorite.objects.create(user=user, recipe=recipe)
                data = RecipeReadSerializer(recipe,
                                            context={'request': request}).data
                del data['ingredients']
                del data['tags']
                del data['author']
                del data['text']
                del data['is_favorited']
                del data['is_in_shopping_cart']
                return Response(data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({"reason": "Рецепт уже в избранном"},
                                status=status.HTTP_400_BAD_REQUEST)
        elif request.method == "DELETE":
            try:
                Favorite.objects.get(user=user, recipe=recipe).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Favorite.DoesNotExist:
                return Response({"reason": "Рецепта нет в избранном"},
                                status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def download_recipe(request):
    cart_list = []
    carts = ShoppingCart.objects.filter(user=request.user)
    for cart in carts:
        for ingredient in cart.recipe.ingredients.all():
            amount = IngredientDetail.objects.get(recipe=cart.recipe,
                                                  ingredient=ingredient).amount
            data = IngredientSerializer(ingredient).data
            data['amount'] = amount
            added = False
            for ingr in cart_list:
                if ingr['id'] == data['id']:
                    ingr['amount'] += data['amount']
                    added = True
            if not added:
                cart_list.append(data)
    response = HttpResponse(content_type='text/csv; charset=windows-1251')
    response[
        'Content-Disposition'] = 'attachment; filename="shopping_list.csv"'
    writer = csv.writer(response)
    writer.writerow(['Ингредиент', 'Количество', 'Единица измерения'])
    for ingredient in cart_list:
        writer.writerow([ingredient['name'], ingredient['amount'],
                         ingredient['measurement_unit']])
    return response


class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer

    def permission_denied(self, request, **kwargs):
        if request.method not in ['GET'] or self.action == 'me':
            super().permission_denied(request, **kwargs)

    @action(detail=False, methods=['GET'])
    def subscriptions(self, request):
        subscriptions = request.user.subscriptions.all()
        all_data = []
        for subscription in subscriptions:
            user_data = CustomUserSerializer(subscription,
                                             context={'request': request}).data
            recipes = Recipe.objects.filter(author=subscription)
            all_recipes = []
            for recipe in recipes:
                recipe_data = RecipeReadSerializer(recipe, context={
                    "request": request}).data
                del recipe_data['ingredients']
                del recipe_data['tags']
                del recipe_data['author']
                del recipe_data['text']
                del recipe_data['is_favorited']
                del recipe_data['is_in_shopping_cart']
                all_recipes.append(recipe_data)
            recipes_limit = request.query_params.get('recipes_limit')
            if recipes_limit:
                all_recipes = all_recipes[:int(recipes_limit)]
            user_data['recipes'] = all_recipes
            user_data['recipes_count'] = len(all_recipes)
            all_data.append(user_data)
        paginator = CustomPagination()
        page = paginator.paginate_queryset(all_data, request)
        if page is not None:
            return paginator.get_paginated_response(page)
        return Response(all_data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, id):
        following = self.get_object()
        user = request.user
        if following == user:
            raise exceptions.ValidationError(
                "Нельзя подписаться на самого себя!", code=400)
        if request.method == "POST":
            if following not in user.subscriptions.all():
                user.subscriptions.add(following)
                user_data = CustomUserSerializer(following, context={
                    'request': request}).data
                recipes = Recipe.objects.filter(author=following)
                all_recipes = []
                for recipe in recipes:
                    recipe_data = RecipeReadSerializer(recipe, context={
                        "request": request}).data
                    del recipe_data['ingredients']
                    del recipe_data['tags']
                    del recipe_data['author']
                    del recipe_data['text']
                    del recipe_data['is_favorited']
                    del recipe_data['is_in_shopping_cart']
                    all_recipes.append(recipe_data)
                recipes_limit = request.query_params.get('recipes_limit')
                if recipes_limit:
                    all_recipes = all_recipes[:int(recipes_limit)]
                user_data['recipes'] = all_recipes
                user_data['recipes_count'] = len(all_recipes)
                return Response(user_data, status=status.HTTP_201_CREATED)
            else:
                return Response({"reason": "Вы уже подписаны!"},
                                status=status.HTTP_400_BAD_REQUEST)
        elif request.method == "DELETE":
            if following in user.subscriptions.all():
                user.subscriptions.remove(following)
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {"reason": "Вы не подписаны на этого пользователя!"},
                    status=status.HTTP_400_BAD_REQUEST)
