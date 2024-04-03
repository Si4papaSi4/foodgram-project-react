from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from rest_framework import serializers

from favorited.models import Favorite, ShoppingCart

User = get_user_model()


class FavoriteSerializer(serializers.Serializer):
    def create(self):
        user = self.context['request'].user
        try:
            Favorite.objects.create(user=user, recipe=self.instance)
        except IntegrityError:
            raise serializers.ValidationError(
                {"reason": "Рецепт уже в избранном"},
                code=400)

    def destroy(self):
        user = self.context['request'].user
        try:
            Favorite.objects.get(user=user, recipe=self.instance).delete()
        except Favorite.DoesNotExist:
            raise serializers.ValidationError(
                {"reason": "Рецепта нет избранном"},
                code=400)


class ShoppingCartSerializer(serializers.Serializer):
    def create(self):
        user = self.context['request'].user
        try:
            ShoppingCart.objects.create(user=user, recipe=self.instance)
        except IntegrityError:
            raise serializers.ValidationError(
                {"reason": "Рецепт уже в списке покупок"},
                code=400)

    def destroy(self):
        user = self.context['request'].user
        try:
            ShoppingCart.objects.get(user=user, recipe=self.instance).delete()
        except ShoppingCart.DoesNotExist:
            raise serializers.ValidationError(
                {"reason": "Рецепта нет в списке покупок"},
                code=400)
