from djoser.views import UserViewSet
from rest_framework import exceptions, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.pagination import CustomPagination
from api.recipes.serializers import ShortRecipeReadSerializer
from api.users.serializers import CustomUserSerializer
from recipes.models import Recipe


class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer

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
                recipe_data = ShortRecipeReadSerializer(recipe).data
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

    @action(detail=True, methods=['post'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, id):
        following = self.get_object()
        user = request.user
        if following == user:
            raise exceptions.ValidationError(
                "Нельзя подписаться на самого себя!", code=400)
        if following not in user.subscriptions.all():
            user.subscriptions.add(following)
            user_data = CustomUserSerializer(following, context={
                'request': request}).data
            recipes = Recipe.objects.filter(author=following)
            all_recipes = []
            for recipe in recipes:
                recipe_data = ShortRecipeReadSerializer(recipe).data
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

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        following = self.get_object()
        user = request.user
        if following == user:
            raise exceptions.ValidationError(
                "Нельзя подписаться на самого себя!", code=400)
        if following in user.subscriptions.all():
            user.subscriptions.remove(following)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"reason": "Вы не подписаны на этого пользователя!"},
                status=status.HTTP_400_BAD_REQUEST)
