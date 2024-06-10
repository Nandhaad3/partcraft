import django_filters
from .models import *

class OfferfilterSet(django_filters.FilterSet):
    parts_offer = django_filters.CharFilter(field_name='parts_offer', lookup_expr='in', method='filter_parts_offer')

    class Meta:
        model = Product
        fields = ['parts_offer']

    def filter_parts_offer(self, queryset, subcategory_name, value):
        values = value.split(',')
        return queryset.filter(parts_offer__in=values)