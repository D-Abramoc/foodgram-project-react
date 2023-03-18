from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, get_list_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from djoser.serializers import UserSerializer
from django.core import serializers as dj_serializers

from .serializers import (IngredientSerializer, AnonimusRecipeSerializer,
                          FavoritePostDeleteSerializer, MeSerializer,
                          CustomUserCreateSerializer,
                          RecipeSerializer, TagSerializer,
                          SubscribeSerializer, SubscriptionsSerializer,
                          RecipeCreateSerializer, SimpleRecipeSerializer,
                          ShoppingCartPostDeleteSerializer,
                          SpecialUserSerializer)
from .custom_pagination import PageLimitPagination
from .custom_filters import (IngredientFilter, IsFavoritedFilter,
                             IsINShoppingcartFilter, TagFilter)
from .permissions import IsOwnerOrAdminOrReadOnly
from recipes.models import Ingredient, Recipe, Tag
from users.models import CustomUser


class CustomUserViewSet(UserViewSet):

    @action(
        methods=['GET', ],
        detail=False,
        url_path='me',
        permission_classes=[IsAuthenticated, ]
    )
    def me(self, request):

        if request.method == 'GET':
            serializer = SpecialUserSerializer(request.user, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if self.request.user.is_anonymous:
            if self.request.method == 'POST':
                return CustomUserCreateSerializer
            return UserSerializer
        return super().get_serializer_class()


class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubscriptionsSerializer
    pagination_class = PageLimitPagination
    permission_classes = (IsAuthenticated,)
    # filter_backends = (DjangoFilterBackend, RecipeLimitFilter)

    def get_queryset(self):
        authors = self.request.user.authors.all()
        authors_pk = [author.author.pk for author in authors]
        queryset = (
            CustomUser.objects.filter(pk__in=authors_pk)
            .annotate(recipes_count=Count('recipes')).order_by('username')
        )
        return queryset


@api_view(['GET',])
@permission_classes([IsAuthenticated,])
def download_shopping_cart(request):
    result = (Ingredient.objects.values('name')
              .filter(recipes__in=request.user.shoppingcart.recipes.all())
              .annotate(ingredient_sum=Sum('quantity__amount')))
    return Response(result)


@api_view(['POST', 'DELETE'])
@permission_classes([AllowAny,])
def subscribe(request, id):
    if request.method == 'DELETE':
        request.user.authors.filter(author__pk=id).delete()
        return Response('Подписка отменена', status=status.HTTP_204_NO_CONTENT)
    data = {}
    data['subscriber'] = get_object_or_404(CustomUser, pk=request.user.pk).pk
    data['author'] = get_object_or_404(CustomUser, pk=id).pk
    serializer = SubscribeSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    # data = CustomUser.objects.get(pk=serializer.data['author'])
    # serializer = SubscriptionsSerializer(data=data)
    # serializer.is_valid(raise_exception=True)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST', 'DELETE'])
@permission_classes([AllowAny,])
def favorite(request, id):
    if request.method == 'DELETE':
        request.user.favorite_recipes.filter(recipe__pk=id).delete()
        return Response('Подписка отменена', status=status.HTTP_204_NO_CONTENT)
    request.data.clear()
    request.data['recipe'] = id
    serializer = FavoritePostDeleteSerializer(
        data=request.data, context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    data = Recipe.objects.filter(pk=serializer.data.get('recipe'))
    serializer = SimpleRecipeSerializer(many=True, data=data)
    serializer.is_valid()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST', 'DELETE'])  # сериалайзер одинаковый, надо рефачить
@permission_classes([AllowAny,])
def shopping_cart(request, id):
    request.data.clear()
    request.data['recipes'] = [
        recipe.pk for recipe in get_list_or_404(Recipe, pk=id)
    ]
    if request.method == 'DELETE':
        request.data['recipes'] = [
            recipe.pk for recipe in
            Recipe.objects.filter(shopping_carts__user=request.user)
            .exclude(pk=id)
        ]
        serializer = ShoppingCartPostDeleteSerializer(
            request.user.shoppingcart, data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response('Рецепт успешно удалён из списка',
                        status=status.HTTP_204_NO_CONTENT)
    serializer = ShoppingCartPostDeleteSerializer(
        request.user.shoppingcart, data=request.data,
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    data = Recipe.objects.filter(pk__in=serializer.data.get('recipes'))
    serializer = SimpleRecipeSerializer(many=True, data=data)
    serializer.is_valid()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all().order_by('name')
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (IngredientFilter,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = PageLimitPagination
    permission_classes = (IsOwnerOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, IsFavoritedFilter,
                       IsINShoppingcartFilter)
    filterset_class = TagFilter

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return RecipeCreateSerializer
        if self.request.user.is_anonymous:
            return AnonimusRecipeSerializer
        return RecipeSerializer

    # def get_queryset(self):
    #     if self.request.method in ('PATCH',):
    #         return Recipe.objects.filter(pk=self.kwargs.get('pk'))
    #     return super().get_queryset()


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer
    pagination_class = None
