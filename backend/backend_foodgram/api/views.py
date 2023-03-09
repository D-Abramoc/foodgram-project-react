from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Count
from django.shortcuts import get_object_or_404, get_list_or_404

from .serializers import (IngredientSerializer, FavoriteSerializer,
                          RecipeSerializer, TagSerializer,
                          SubscribeSerializer, SubscriptionsSerializer,
                          ShoppingCartSerializer, RecipeCreateSerializer)
from .custom_pagination import PageLimitPagination
from .custom_filters import IngredientFilter
from recipes.models import Ingredient, Recipe, Tag
from users.models import CustomUser

from rest_framework.parsers import MultiPartParser, FormParser


# class ShoppingCartViewSet(viewsets.ModelViewSet):
#     queryset = ShoppingCart.objects.all().order_by('pk')
#     serializer_class = ShoppingCartSerializer


# class SubscribeUnsubscribeViewSet(viewsets.ModelViewSet):
#     queryset = Subscribe.objects.all()
#     serializer_class = SubscribeSerializer


class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubscriptionsSerializer
    pagination_class = PageLimitPagination

    def get_queryset(self):
        authors = self.request.user.authors.all()
        authors_pk = [author.author.pk for author in authors]
        queryset = (
            CustomUser.objects.filter(pk__in=authors_pk)
            .annotate(recipes_count=Count('recipes')).order_by('username')
        )
        return queryset


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
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST', 'DELETE'])
@permission_classes([AllowAny,])
def favorite(request, id):
    if request.method == 'DELETE':
        request.user.favorite_recipes.filter(recipe__pk=id).delete()
        return Response('Подписка отменена', status=status.HTTP_204_NO_CONTENT)
    data = {}
    data['user'] = get_object_or_404(CustomUser, pk=request.user.pk).pk
    data['recipe'] = get_object_or_404(Recipe, pk=id).pk
    serializer = FavoriteSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
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
        serializer = ShoppingCartSerializer(
            request.user.shoppingcart, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response('Подписка отменена', status=status.HTTP_204_NO_CONTENT)
    serializer = ShoppingCartSerializer(
        request.user.shoppingcart, data=request.data
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all().order_by('name')
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (IngredientFilter,)


class RecipeViewSet(viewsets.ModelViewSet):
    # parser_classes = (MultiPartParser, FormParser)
    queryset = Recipe.objects.all()
    pagination_class = PageLimitPagination
    filterset_fields = ('author', 'tags')

    def get_serializer_class(self):
        if self.request.method in ('POST'):
            return RecipeCreateSerializer
        return RecipeSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer
    pagination_class = None
