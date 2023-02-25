from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import (CustomUserSerializer, CustomUserPOSTSerializer,
                          ChangePasswordSerializer, IngredientSerializer,
                          RecipeSerializer, TagSerializer,
                          CreateUserSerializer)
from .custom_pagination import PageLimitPagination
from recipes.models import Ingredient, Recipe, Tag
from users.models import CustomUser


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all().order_by('username')
    serializer_class = CustomUserSerializer
    # permission_classes = (IsAuthenticated,)
    pagination_class = PageLimitPagination

    def get_serializer_class(self):
        if self.request.method in ('POST',):
            return CustomUserPOSTSerializer
        return CustomUserSerializer

    @action(
        methods=['GET', 'PATCH', ],
        detail=False,
        url_path='me',
        permission_classes=[IsAuthenticated, ]
    )
    def me_page(self, request):

        if request.method == 'GET':
            serializer = CustomUserSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = CustomUserSerializer(
                request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=('POST',), detail=False, url_name='set_password',
            permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        serializer = ChangePasswordSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.instance.set_password(request.data.get('new_password'))
        serializer.instance.save()
        return Response('Пароль успешно изменён',
                        status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all().order_by('name')
    serializer_class = IngredientSerializer


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
