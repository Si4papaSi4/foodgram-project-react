from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework import routers

from api.recipes.views import (CustomUserViewSet, IngredientViewSet,
                               RecipeViewSet, TagViewSet, download_recipe)

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
    path('recipes/download_shopping_cart/', download_recipe),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router_v1.urls))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
