from django_filters.rest_framework import CharFilter, FilterSet
from recipes.models import Recipe
from rest_framework import filters
from rest_framework.exceptions import ValidationError


class IngredientFilter(filters.BaseFilterBackend):
    '''
    Фильтр для поиска ингредиента по начальным буквам. Регистронезависимый.
    '''
    allowed_fields = ('name',)

    def filter_queryset(self, request, queryset, view):
        if 'search' not in request.query_params:
            return queryset
        desired = request.query_params['search']
        return queryset.filter(name__istartswith=desired).order_by('name')


class IsFavoritedFilter(filters.BaseFilterBackend):
    '''
    Фильтр для выборки рецептов по критерию добавлен/не добавлен
    в избранное.
    '''

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
    '''
    Фильтр для выборки рецептов по критерию добавлен/не добавлен
    в список покупок.
    '''

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


class TagFilter(filters.BaseFilterBackend):
    '''
    Фильтр по тегам
    '''

    def filter_queryset(self, request, queryset, view):
        if 'tags' not in request.query_params:
            return queryset
        return queryset.filter(
            tags__slug__in=request.query_params.getlist('tags')
        ).distinct()


class AuthorFilter(FilterSet):
    '''
    Фильтр для поиска по автору
    '''
    # tags = CharFilter(field_name='tags__slug')
    author = CharFilter(field_name='author__id')

    class Meta:
        model = Recipe
        fields = ('author',)
