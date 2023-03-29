from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path, re_path
from rest_framework import routers

from . import views
from .custom_routers import OnlyGetRouter

app_name = 'api'

router_v1 = routers.DefaultRouter()
router_only_get = OnlyGetRouter()
router_only_get.register(
    r'ingredients', views.IngredientViewSet, basename='ingredients'
)
router_v1.register(r'recipes', views.RecipeViewSet, basename='recipes')
router_only_get.register(r'tags', views.TagViewSet, basename='tags')
router_v1.register(r'users', views.CustomUserViewSet)

urlpatterns = [
    re_path(
        r'^users/subscriptions/',
        views.SubscriptionViewSet.as_view({'get': 'list'}),
    ),
    path('', include(router_v1.urls)),
    path('', include(router_only_get.urls)),
    path('', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path(
        'api-auth/', include('rest_framework.urls', namespace='rest_framework')
    )
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
