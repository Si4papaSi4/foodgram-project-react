from django.urls import include, path
from rest_framework import routers

from api.recipes.views import IngredientViewSet, RecipeViewSet, TagViewSet
from api.users.views import CustomUserViewSet

router_v1 = routers.DefaultRouter()

router_v1.register(
    r'tags',
    TagViewSet
)
router_v1.register(
    'ingredients',
    IngredientViewSet
)
router_v1.register(
    'recipes',
    RecipeViewSet
)
router_v1.register("users", CustomUserViewSet)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router_v1.urls))
]
