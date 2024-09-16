from rest_framework import status
from .documents import ProductDocument
from rest_framework.response import Response
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from django_elasticsearch_dsl_drf.filter_backends import FilteringFilterBackend, CompoundSearchFilterBackend
from rest_framework.pagination import PageNumberPagination
from parts.serializers import ProductoneSerializer
from parts.models.models import Product
import json

class CustomPagination(PageNumberPagination):
    page_size = 9
    page_size_query_param = 'size'

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
        search = search.extra(size=1000)
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

    def get_vehicle_data_from_cookie(self):
        cookie_vehicle_data = self.request.COOKIES.get('vehicle')
        if cookie_vehicle_data:
            return json.loads(cookie_vehicle_data)
        return []

    def filter_queryset_by_vehicle_data(self, queryset, vehicle_data):
        matched_ids = []
        for product in queryset:
            product_fits = product.this_parts_fits.all()
            for vehicle in vehicle_data:
                for fit in product_fits:
                    if (vehicle.get('vehicle_name') == fit.vehicle_name and
                        vehicle.get('vehicle_model') == fit.vehicle_model and
                        vehicle.get('vehicle_year') == fit.vehicle_year and
                        vehicle.get('vehicle_type') == fit.vehicle_type):
                        matched_ids.append(product.id)
                        break
        return queryset.filter(id__in=matched_ids)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        response = queryset.execute()

        if not response.hits:
            return Response({"detail": "No Product found matching the criteria."}, status=status.HTTP_404_NOT_FOUND)

        hit_ids = [hit.meta.id for hit in response.hits]
        queryset = Product.objects.filter(id__in=hit_ids)

        vehicle_data = self.get_vehicle_data_from_cookie()
        if vehicle_data:
            queryset = self.filter_queryset_by_vehicle_data(queryset, vehicle_data)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
