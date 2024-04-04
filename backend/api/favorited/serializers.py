from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from favorited.models import Favorite, ShoppingCart
from recipes.models import Recipe
from rest_framework import exceptions, serializers

User = get_user_model()


class FavoriteSerializer(serializers.Serializer):
    def validate_and_get_object(self):
        try:
            recipe = Recipe.objects.get(id=self.context.get('pk'))
        except Recipe.DoesNotExist:
            if self.context.get('request').method == 'POST':
                raise serializers.ValidationError(
                    {'errors': 'Рецепта не существует.'})
            else:
                raise exceptions.NotFound(
                    {'errors': 'Рецепта не существует.'})
        return recipe

    def create(self):
        instance = self.validate_and_get_object()
        user = self.context['request'].user
        try:
            Favorite.objects.create(user=user, recipe=instance)
        except IntegrityError:
            raise serializers.ValidationError(
                {'errors': 'Рецепт уже в избранном'})

    def destroy(self):
        instance = self.validate_and_get_object()
        user = self.context['request'].user
        try:
            Favorite.objects.get(user=user, recipe=instance).delete()
        except Favorite.DoesNotExist:
            raise serializers.ValidationError(
                {'errors': 'Рецепта нет избранном'})


class ShoppingCartSerializer(serializers.Serializer):
    def validate_and_get_object(self):
        try:
            recipe = Recipe.objects.get(id=self.context.get('pk'))
        except Recipe.DoesNotExist:
            if self.context.get('request').method == 'POST':
                raise serializers.ValidationError(
                    {'errors': 'Рецепта не существует.'})
            else:
                raise exceptions.NotFound(
                    {'errors': 'Рецепта не существует.'})
        return recipe

    def create(self):
        instance = self.validate_and_get_object()
        try:
            ShoppingCart.objects.create(
                user=self.context['request'].user,
                recipe=instance
            )
        except IntegrityError:
            raise serializers.ValidationError(
                {'errors': 'Рецепт уже в списке покупок'})

    def destroy(self):
        instance = self.validate_and_get_object()
        try:
            ShoppingCart.objects.get(
                user=self.context['request'].user,
                recipe=instance
            ).delete()
        except ShoppingCart.DoesNotExist:
            raise serializers.ValidationError(
                {'errors': 'Рецепта нет в списке покупок'})
