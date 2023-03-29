from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class PageLimitPagination(PageNumberPagination):
    '''
    Пагинатор
    '''
    page_size = settings.PAGE_SIZE_CUSTOM_PAGINATOR
    page_size_query_param = 'limit'
    max_page_size = settings.MAX_PAGE_SIZE_CUSTOM_PAGINATOR
