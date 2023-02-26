from django.urls import include, re_path, path
from rest_framework import routers
from . import views


app_name = 'api'

router_v1 = routers.DefaultRouter()
# router_v1.register(r'users', views.CustomUserViewSet, basename='users')
router_v1.register(
    r'ingredients', views.IngredientViewSet, basename='ingredients'
)
router_v1.register(r'recipes', views.RecipeViewSet, basename='recipes')
router_v1.register(r'tags', views.TagViewSet, basename='tags')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path(
        'api-auth/', include('rest_framework.urls', namespace='rest_framework')
    )
]
