from django.contrib.auth import get_user_model
from rest_framework import serializers

from favorited.models import Favorite, ShoppingCart

User = get_user_model()


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = '__all__'

    def validate(self, attrs):
        if self.context.get(
                'request'
        ).method == 'POST' and ShoppingCart.objects.filter(
            recipe=attrs.get('recipe'),
            user=attrs.get('user')
        ).exists():
            raise serializers.ValidationError(
                {'errors': 'Рецепт уже в списке покупок'}
            )
        elif not ShoppingCart.objects.filter(
            recipe=attrs.get('recipe'),
            user=attrs.get('user')
        ).exists() and self.context.get('request').method != 'POST':
            raise serializers.ValidationError(
                {'errors': 'Рецепта нет в списке покупок'}
            )
        return attrs

    def destroy(self, validated_data):
        ShoppingCart.objects.filter(
            user=validated_data.get('user'),
            recipe=validated_data.get('recipe')
        ).delete()


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'

    def validate(self, attrs):
        if self.context.get(
                'request'
        ).method == 'POST' and Favorite.objects.filter(
            recipe=attrs.get('recipe'),
            user=attrs.get('user')
        ).exists():
            raise serializers.ValidationError(
                {'errors': 'Рецепт уже в избранном'}
            )
        elif not Favorite.objects.filter(
            recipe=attrs.get('recipe'),
            user=attrs.get('user')
        ).exists() and self.context.get('request').method != 'POST':
            raise serializers.ValidationError(
                {'errors': 'Рецепта нет в избранном'}
            )
        return attrs

    def destroy(self, validated_data):
        Favorite.objects.filter(
            user=validated_data.get('user'),
            recipe=validated_data.get('recipe')
        ).delete()
