from django.contrib.auth import get_user_model
from rest_framework import exceptions, serializers

from api.recipes.serializers import ShortRecipeReadSerializer
from recipes.models import Recipe

User = get_user_model()


class SubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField(default=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribed', 'recipes',
                  'recipes_count')

    def create(self):
        user = self.context['request'].user
        following = self.instance
        if following == user:
            raise exceptions.ValidationError(
                {"reason": "Нельзя подписаться на самого себя"}, code=400)
        if following in user.subscriptions.all():
            raise exceptions.ValidationError(
                {"reason": "Вы уже подписаны!"}, code=400)
        user.subscriptions.add(following)
        return self.to_representation(self.instance)

    def destroy(self):
        user = self.context['request'].user
        following = self.instance
        if following not in user.subscriptions.all():
            raise exceptions.ValidationError(
                {"reason": "Вы не подписаны!"}, code=400)
        user.subscriptions.remove(following)
        return self.to_representation(self.instance)

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj)
        all_recipes = []
        for recipe in recipes:
            recipe_data = ShortRecipeReadSerializer(recipe).data
            all_recipes.append(recipe_data)
        recipes_limit = self.context.get(
            'request'
        ).query_params.get('recipes_limit')
        if recipes_limit:
            all_recipes = all_recipes[:int(recipes_limit)]
        return all_recipes

    def get_recipes_count(self, obj):
        return len(self.get_recipes(obj))
