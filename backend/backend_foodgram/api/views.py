from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Count
from django.shortcuts import get_object_or_404

from .serializers import (IngredientSerializer, FavoriteSerializer,
                          RecipeSerializer, TagSerializer,
                          SubscribeSerializer, SubscriptionsSerializer,
                          ShoppingCartSerializer)
from .custom_pagination import PageLimitPagination
from .custom_filters import IngredientFilter
from recipes.models import Ingredient, Recipe, Tag, ShoppingCart
from users.models import CustomUser, Subscribe


class ShoppingCartViewSet(viewsets.ModelViewSet):
    queryset = ShoppingCart.objects.all().order_by('pk')
    serializer_class = ShoppingCartSerializer


class SubscribeUnsubscribeViewSet(viewsets.ModelViewSet):
    queryset = Subscribe.objects.all()
    serializer_class = SubscribeSerializer


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


# class CustomUserViewSet(UserViewSet):

#     @action(methods=('get',), detail=True, url_path='subscriptions')
#     def subscriptions(self, request, pk):
#         return Response('Response from action')


# class CustomUserViewSet(viewsets.ModelViewSet):
#     queryset = CustomUser.objects.all().order_by('username')
#     serializer_class = CustomUserSerializer
#     # permission_classes = (IsAuthenticated,)
#     pagination_class = PageLimitPagination

#     def get_serializer_class(self):
#         if self.request.method in ('POST',):
#             return CustomUserPOSTSerializer
#         return CustomUserSerializer

#     @action(
#         methods=['GET', 'PATCH', ],
#         detail=False,
#         url_path='me',
#         permission_classes=[IsAuthenticated, ]
#     )
#     def me_page(self, request):

#         if request.method == 'GET':
#             serializer = CustomUserSerializer(request.user)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         if request.method == 'PATCH':
#             serializer = CustomUserSerializer(
#                 request.user, data=request.data, partial=True)
#             serializer.is_valid(raise_exception=True)
#             serializer.save(role=request.user.role)
#             return Response(serializer.data, status=status.HTTP_200_OK)

#     @action(methods=('POST',), detail=False, url_name='set_password',
#             permission_classes=(IsAuthenticated,))
#     def set_password(self, request):
#         serializer = ChangePasswordSerializer(request.user,
#                                               data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.instance.set_password(request.data.get('new_password'))
#         serializer.instance.save()
#         return Response('Пароль успешно изменён',
#                         status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all().order_by('name')
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (IngredientFilter,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageLimitPagination
    filterset_fields = ('author', 'tags')

    # def create(self, request, *args, **kwargs):
    #     serializer = RecipeSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer
    pagination_class = None
