from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from rest_framework import exceptions, serializers

from api.fields import Base64ImageField
from api.users.serializers import CustomUserSerializer
from favorited.models import Favorite, ShoppingCart
from recipes.models import Ingredient, IngredientDetail, Recipe, Tag

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientDetailSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )

    class Meta:
        model = IngredientDetail
        fields = ('id', 'amount')


class ShortRecipeReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeReadSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True)
    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_in_shopping_cart(self, obj):
        if self.context['request'].user.is_authenticated:
            return ShoppingCart.objects.filter(
                recipe=obj, user=self.context['request'].user
            ).exists()
        return False

    def get_is_favorited(self, obj):
        if self.context['request'].user.is_authenticated:
            return Favorite.objects.filter(
                recipe=obj, user=self.context['request'].user
            ).exists()
        return False

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for ingredient in data['ingredients']:
            ingredient['amount'] = IngredientDetail.objects.get(
                ingredient_id=ingredient['id'], recipe_id=data['id']).amount
        return data
    # Не смог избавиться от этого, не понял... Задаю вопрос. КАК?


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientDetailSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        exclude = ('author',)

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Рецепт должен содержать ингредиенты.', code=400)
        if len(set(map(lambda ingredient: ingredient['ingredient'],
                       ingredients))) != len(ingredients):
            raise serializers.ValidationError(
                'Рецепт не может содержать '
                'повторяющиеся ингредиенты.',
                code=400)
        return ingredients

    def validate_cooking_time(self, cook_time):
        if cook_time < 1:
            raise serializers.ValidationError(
                "Минимальное время приготовления - 1 минута."
            )
        return cook_time

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                'Рецепт должен содержать теги.', code=400)
        if len(set(tags)) != len(tags):
            raise serializers.ValidationError(
                'Рецепт не может содержать '
                'повторяющиеся теги.',
                code=400
            )
        return tags

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context={
            'request': self.context.get('request')}).data

    def ingredients_create(self, ingredients, recipe):
        ingredients_instance = [
            IngredientDetail(
                ingredient=ingredient['ingredient'], recipe=recipe,
                amount=ingredient['amount']) for ingredient in ingredients
        ]
        IngredientDetail.objects.bulk_create(ingredients_instance)

    def tags_create(self, recipe, tags):
        for tag in tags:
            recipe.tags.add(tag)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        try:
            recipe = Recipe.objects.create(**validated_data,
                                           author=self.context.get(
                                               'request').user)
        except IntegrityError:
            raise exceptions.ValidationError('This recipe already exists',
                                             code=400)
        self.ingredients_create(ingredients, recipe)
        self.tags_create(recipe, tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        tags_data = validated_data.pop('tags', [])
        instance.ingredients.clear()
        instance.tags.clear()

        self.ingredients_create(ingredients_data, instance)
        self.tags_create(instance, tags_data)
        instance.save()
        super().update(instance, validated_data)
        return instance
