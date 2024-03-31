import base64
import os
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, IngredientDetail, Recipe,
                            ShoppingCart, Tag)

User = get_user_model()


class CustomUserSerializer(UserSerializer):

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['is_subscribed'] = False
        user = self.context.get('request').user
        if user.is_authenticated and instance in user.subscriptions.all():
            data['is_subscribed'] = True
        return data


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для категорий."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для категорий."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeReadSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True)
    tags = TagSerializer(many=True)
    author = CustomUserSerializer()

    def validate_cooking_time(self, cook_time):
        if cook_time < 1:
            raise serializers.ValidationError(
                "Минимальное время приготовления - 1 минута."
            )
        return cook_time

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for ingredient in data['ingredients']:
            ingredient['amount'] = IngredientDetail.objects.get(
                ingredient_id=ingredient['id'], recipe_id=data['id']).amount
        if self.context.get('request').user.is_authenticated:
            try:
                ShoppingCart.objects.get(recipe=instance,
                                         user=self.context.get('request').user)
                data['is_in_shopping_cart'] = True
            except ShoppingCart.DoesNotExist:
                data['is_in_shopping_cart'] = False
            try:
                Favorite.objects.get(recipe=instance,
                                     user=self.context.get('request').user)
                data['is_favorited'] = True
            except Favorite.DoesNotExist:
                data['is_favorited'] = False
        else:
            data['is_favorited'] = False
            data['is_in_shopping_cart'] = False
        return data

    class Meta:
        model = Recipe
        fields = '__all__'


class IngredientDetailSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(),
                                            source='ingredient')

    class Meta:
        model = IngredientDetail
        fields = ('id', 'amount')


class Base64ImageField(serializers.ImageField):
    """
    Пользовательское поле для обработки изображений в формате base64.
    """

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            decoded_image = base64.b64decode(data.split(';base64,')[1])
            filename = str(uuid.uuid4()) + '.jpg'
            with open(os.path.join(settings.MEDIA_ROOT, filename), 'wb') as f:
                f.write(decoded_image)
            return filename
        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientDetailSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    image = Base64ImageField()

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Рецепт должен содержать ингредиенты и теги.', code=400)
        if len(set(map(lambda ingredient: ingredient['ingredient'],
                       ingredients))) != len(ingredients):
            raise serializers.ValidationError(
                'Рецепт не может содержать '
                'повторяющиеся теги или ингредиенты.',
                code=400)
        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                'Рецепт должен содержать ингредиенты и теги.', code=400)
        if len(set(tags)) != len(tags):
            raise serializers.ValidationError(
                'Рецепт не может содержать '
                'повторяющиеся теги или ингредиенты.',
                code=400
            )
        return tags

    class Meta:
        model = Recipe
        exclude = ('author',)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context={
            'request': self.context.get('request')}).data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data)

        for ingredient in ingredients:
            IngredientDetail.objects.create(
                ingredient=ingredient['ingredient'], recipe=recipe,
                amount=ingredient['amount'])
        for tag in tags:
            recipe.tags.add(tag)

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        instance.ingredients.clear()
        for ingredient_data in ingredients_data:
            IngredientDetail.objects.create(
                ingredient=ingredient_data['ingredient'],
                recipe=instance,
                amount=ingredient_data['amount']
            )

        tags_data = validated_data.pop('tags', [])
        instance.tags.clear()
        for tag_data in tags_data:
            instance.tags.add(tag_data)

        instance.save()
        super().update(instance, validated_data)
        return instance
