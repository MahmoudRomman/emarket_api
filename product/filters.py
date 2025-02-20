import django_filters
from . import models


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='iexact')
    keyword = django_filters.CharFilter(field_name="description", lookup_expr='icontains')
    minprice = django_filters.filters.NumberFilter(field_name='price' or 0, lookup_expr='gte')
    maxprice = django_filters.filters.NumberFilter(field_name='price' or 100000, lookup_expr='lte')

    class Meta:
        model = models.Product
        fields = ['category', 'brand', 'keyword', 'minprice', 'maxprice']
