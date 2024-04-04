from api.recipes.serializers import ShortRecipeReadSerializer
from django.contrib.auth import get_user_model
from recipes.models import Recipe
from rest_framework import exceptions, serializers

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

    def validate_user_following_add(self, user, following):
        if following == user:
            raise exceptions.ValidationError(
                {'errors': 'Нельзя подписаться на самого себя'}
            )
        if following in user.subscriptions.all():
            raise exceptions.ValidationError(
                {'errors': 'Вы уже подписаны!'}
            )

    def validate_user_following_remove(self, user, following):
        if following not in user.subscriptions.all():
            raise exceptions.ValidationError(
                {'errors': 'Вы не подписаны!'}
            )

    def save(self):
        user = self.context['request'].user
        following = self.instance
        self.validate_user_following_add(user, following)
        user.subscriptions.add(following)
        return self.to_representation(self.instance)

    def destroy(self):
        user = self.context['request'].user
        following = self.instance
        self.validate_user_following_remove(user, following)
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
