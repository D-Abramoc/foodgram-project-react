from django_filters.rest_framework import CharFilter, FilterSet
from rest_framework import filters
from rest_framework.exceptions import ValidationError

from recipes.models import Recipe


class IngredientFilter(filters.BaseFilterBackend):
    allowed_fields = ('name',)

    def filter_queryset(self, request, queryset, view):
        if 'search' not in request.query_params:
            return queryset
        desired = request.query_params['search']
        return queryset.filter(name__istartswith=desired).order_by('name')


class IsFavoritedFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        if 'is_favorited' not in request.query_params:
            return queryset
        if int(request.query_params.get('is_favorited')) not in (0, 1):
            raise ValidationError(
                'Параметр is_favorited должен быть равен 0 или 1'
            )
        if int(request.query_params.get('is_favorited')) == 0:
            queryset = queryset.exclude(users__user=request.user)
            return queryset
        return queryset.filter(users__user=request.user)


class IsInShoppingcartFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        if 'is_in_shopping_cart' not in request.query_params:
            return queryset
        if int(request.query_params.get('is_in_shopping_cart')) not in (0, 1):
            raise ValidationError(
                'Параметр is_in_shoppingcart должен быть равен 0 или 1'
            )
        if int(request.query_params.get('is_in_shopping_cart')) == 0:
            queryset = queryset.exclude(shopping_carts__user=request.user)
            return queryset
        return queryset.filter(shopping_carts__user=request.user)


class TagFilter(FilterSet):
    tags = CharFilter(field_name='tags__slug')
    author = CharFilter(field_name='author__id')

    class Meta:
        model = Recipe
        fields = ('tags', 'author')
