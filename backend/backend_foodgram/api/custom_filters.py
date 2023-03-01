from rest_framework import filters


class IngredientFilter(filters.BaseFilterBackend):
    allowed_fields = ('name',)

    def filter_queryset(self, request, queryset, view):
        desired = request.query_params['search']
        queryset = queryset.filter(name__istartswith=desired).order_by('name')
        return queryset
