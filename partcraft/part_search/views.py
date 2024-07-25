from rest_framework import status
from .documents import ProductDocument
from rest_framework.response import Response
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from django_elasticsearch_dsl_drf.filter_backends import FilteringFilterBackend, CompoundSearchFilterBackend
from rest_framework.pagination import PageNumberPagination
from parts.serializers import ProductoneSerializer

from parts.models import Product


class CustomPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'size'
    max_page_size = 10

class partslistsDocumentView(DocumentViewSet):
    document = ProductDocument
    serializer_class = ProductoneSerializer
    filter_backends = [FilteringFilterBackend, CompoundSearchFilterBackend]
    query_backends = [CompoundSearchFilterBackend]
    filter_fields = {
        'parts_brand': 'parts_brand',
        'parts_category': 'parts_category',
        'subcategory_name': 'subcategory_name',
        'parts_no': 'parts_no',
        'parts_fits': 'parts_fits',
        'parts_type': 'parts_type',
    }
    search_fields = ['parts_brand', 'parts_category', 'subcategory_name', 'parts_no', 'parts_fits', 'parts_type']
    multi_match_search_fields = ['parts_brand', 'parts_category', 'subcategory_name', 'parts_no', 'parts_fits', 'parts_type']
    pagination_class = CustomPagination

    def get_queryset(self):
        search_query = self.request.query_params.get('search', '').strip()
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        min_offer = self.request.query_params.get('min_offer')
        max_offer = self.request.query_params.get('max_offer')

        search = self.document.search()
        if search_query:
            search = search.query('bool', should=[
            {'match': {'parts_brand': search_query}},
            {'match': {'parts_category': search_query}},
            {'match': {'subcategory_name': search_query}},
            {'match': {'parts_no': search_query}},
            {'match': {'parts_fits': search_query}},
            {'match': {'parts_type': search_query}}
        ])

        if min_offer or max_offer:
            offer_filter = {}
            if min_offer:
                offer_filter['gte'] = int(min_offer)
            if max_offer:
                offer_filter['lte'] = int(max_offer)
            search = search.filter('range', parts_offer=offer_filter)

        if min_price or max_price:
            price_filter = {}
            if min_price:
                price_filter['gte'] = float(min_price)
            if max_price:
                price_filter['lte'] = float(max_price)
            search = search.filter('range', final_price=price_filter)

        return search

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        response = queryset.execute()
        if not response.hits:
            return Response({"detail": "No Product found matching the criteria."}, status=status.HTTP_404_NOT_FOUND)
        hit_ids = [hit.meta.id for hit in response.hits]
        queryset = Product.objects.filter(id__in=hit_ids)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
