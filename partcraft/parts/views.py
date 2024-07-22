import json
from django.db.migrations import serializer
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from elasticsearch import NotFoundError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import status, generics
from rest_framework.exceptions import NotFound
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view
from django.db.models import F, CharField, Value
from django.db.models.functions import Concat
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *
from collections import defaultdict
from .filter import OfferfilterSet
from account.emails import send_confirmation_email
import base64
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from django_elasticsearch_dsl_drf.filter_backends import FilteringFilterBackend, CompoundSearchFilterBackend
from .documents import ProductDocument

def adddict(serializer):
    last_data = []
    for i in serializer.data:
        data = {}
        data['id'] = i['id']
        data['parts_type'] = i['parts_type']
        data['main_image'] = i['main_image']
        data['brand_image'] = i['parts_brand']['brand_image']
        d = (f"{i['parts_brand']['brand_name']} "
             f"{i['parts_category']['category_name']} "
             f'{i["subcategory_name"]}'
             f"{i['parts_voltage']} "
             f"{i['parts_litre']}L ")
        data['parts__Name'] = d.replace('NoneL', '').strip()
        data['parts_no'] = i['parts_no']
        data['parts_offer'] = i['parts_offer']
        data['parts_price'] = i['parts_price']
        dis = i['parts_price'] * (i['parts_offer'] / 100)
        data['final_price'] = i['parts_price'] - dis
        data['product_full_detail'] = i['url']
        data['is_in_wishlist'] = i['is_in_wishlist']
        if i['is_in_wishlist'] is False:
            data['wishlist'] = i['wishlist']
            data['is_in_wishlist'] = i['is_in_wishlist']
        elif i['is_in_wishlist'] is True:
            data['is_in_wishlist'] = i['is_in_wishlist']

        last_data.append(data)
    return last_data


class CustomPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'size'
    max_page_size = 10


# def offerdata(queryset):
#     return queryset.values_list('parts_offer', flat=True).distinct()

class partslistview(generics.ListAPIView):
    # queryset = Product.objects.all()
    # print(queryset)
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Product.objects.annotate(
        parts_name=Concat(
            F('parts_brand__brand_name'),
            Value(' '),
            F('parts_category__category_name'),
            Value(' '),
            F('subcategory_name'),
            Value(' '),
            F('parts_voltage'),
            Value('V'),
            output_field=CharField()
        )
    )
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = OfferfilterSet
    search_fields = ['parts_brand__brand_name', 'parts_category__category_name', 'parts_name', 'subcategory_name']
    ordering_fields = ['parts_name', 'parts_price']
    pagination_class = CustomPagination

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        #print(queryset)
        if not queryset.exists():
            raise NotFound(detail="No Product found matching the criteria.")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            lastdata = adddict(serializer)
            return self.get_paginated_response(lastdata)
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        lastdata = adddict(serializer)
        # offer=offerdata(queryset)
        return Response(lastdata, status=status.HTTP_200_OK)


# localhost:9200/product/_search?pretty=
# localhost:9200/product/
# localhost:9200/product/_mapping?pretty
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
        print(search.to_dict())
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
        print(response)
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

class partsonedetail(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        product_id = self.kwargs.get('pk')
        queryset = Product.objects.filter(id=product_id)
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({'details': 'Product Not Found'}, status=status.HTTP_404_NOT_FOUND)

        product = queryset.first()
        serializer = self.get_serializer(product)
        data = serializer.data

        if data.get('is_in_wishlist'):
            data.pop('wishlist', None)

        return Response(data, status=status.HTTP_200_OK)


class categorylistview(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if not queryset.exists():
            raise NotFound(detail="No Category found matching the criteria.")
        serializer = self.get_serializer(queryset, many=True)
        print(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)


class categoryonedetail(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        category_id = self.kwargs.get('pk')
        cat = Category.objects.get(id=category_id)
        quaryset = Product.objects.all().filter(parts_category_id=cat.id)
        return quaryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        category_id = self.kwargs.get('pk')
        cat = Category.objects.get(id=category_id)
        if not queryset.exists():
            return Response({'details': 'Product Not Found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True)
        category_serializer = CategorySerializer(cat, context={'request': request})
        lastdata = adddict(serializer)
        return Response({'brand': category_serializer.data, 'parts': lastdata}, status=status.HTTP_200_OK)


class brandlistview(generics.ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if not queryset.exists():
            raise NotFound(detail="No Brand found matching the criteria.")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class brandonedetail(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        brand_id = self.kwargs.get('pk')
        brand = Brand.objects.get(id=brand_id)
        queryset = Product.objects.all().filter(parts_brand_id=brand)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        brand_id = self.kwargs.get('pk')
        brand = Brand.objects.get(id=brand_id)
        if not queryset.exists():
            return Response({'details': 'Product Not Found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True)
        brand_serializer = BrandSerializer(brand, context={'request': request})
        lastdata = adddict(serializer)
        return Response({'brand': brand_serializer.data, 'parts': lastdata}, status=status.HTTP_200_OK)


class vehiclelistview(generics.ListAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if not queryset.exists():
            raise NotFound(detail="No Vehicle found matching the criteria.")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST', 'GET'])
def vehicle_view(request):
    if request.method == 'POST':
        vehicleserializer = VehicleoneSerializer(data=request.data)
        if vehicleserializer.is_valid():
            try:
                vehicle = Vehicle.objects.get(
                    vehicle_name=vehicleserializer.validated_data['vehicle_name'],
                    vehicle_type=vehicleserializer.validated_data['vehicle_type'],
                    vehicle_model=vehicleserializer.validated_data['vehicle_model'],
                    vehicle_year=vehicleserializer.validated_data['vehicle_year'],
                )
                this_part = Product.objects.filter(this_parts_fits=vehicle)
                print(this_part)
                productserializer = ProductSerializer(this_part, context={'request': request}, many=True)
                lastdata = adddict(productserializer)
                return Response({
                    'vehicle': vehicleserializer.data,
                    'parts': lastdata
                }, status=status.HTTP_200_OK)
            except Vehicle.DoesNotExist:
                return Response({'detail': 'Vehicle not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(vehicleserializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        queryset = Vehicle.objects.all()
        serializer = VehicleSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class vehicleoneview(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        vehicle_id = self.kwargs.get('pk')
        vehicle = Vehicle.objects.get(id=vehicle_id)
        queryset = Product.objects.all().filter(this_parts_fits=vehicle)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        vehicle_id = self.kwargs.get('pk')
        vehicle = Vehicle.objects.get(id=vehicle_id)
        if not queryset.exists():
            return Response({'details': 'Product Not Found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        vehicle_serializer = VehicleSerializer(vehicle, context={'request': request})
        lastdata = adddict(serializer)
        return Response({'brand': vehicle_serializer.data, 'parts': lastdata}, status=status.HTTP_200_OK)


def category_offer(data):
    categorized_data = {}
    for item in data:
        parts_offer = item['parts_offer']
        if parts_offer not in categorized_data:
            categorized_data[parts_offer] = []
        categorized_data[parts_offer].append(item)
    return categorized_data


class allofferview(generics.ListAPIView):
    serializer_class = OfferSerializer
    queryset = Product.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if not queryset.exists():
            return Response({'details': 'Product Not Found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)
        categorized_data = category_offer(serializer.data)

        return Response({'Offer': categorized_data}, status=status.HTTP_200_OK)


# class allofferview(generics.ListAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#     def list(self, request, *args, **kwargs):
#         offer=self.queryset.values_list('parts_offer', flat=True).distinct()
#         return Response({'offer':offer}, status=status.HTTP_200_OK)

class WishlistCreateView(generics.ListCreateAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return the user's wishlist items
        queryset = Wishlist.objects.all().filter(wishlist_name=self.request.user)
        return queryset

    def get_product(self):
        product_id = self.kwargs.get('pk')
        try:
            return Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return None

    def create(self, request, *args, **kwargs):
        product = self.get_product()
        print('p', product)
        if not product:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the product is already in the user's wishlist
        if Wishlist.objects.filter(wishlist_name=request.user, wishlist_product=product).exists():
            return Response({"error": "Product already exists in the wishlist."}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare the data for serialization
        data = {
            'wishlist_name': self.request.user,
            'wishlist_product': product
        }
        print(data)
        s = self.get_serializer(data=data)
        # serializer.is_valid(raise_exception=True)
        self.perform_create(s)

        headers = self.get_success_headers(serializer)
        return Response({'message': 'Wishlist created successfully'}, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        if serializer.is_valid(raise_exception=True):
            serializer.save(wishlist_name=self.request.user, wishlist_product=self.get_product())


class WishallView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Filter the Wishlist items for the authenticated user
        wishlists = Wishlist.objects.filter(wishlist_name=self.request.user)

        # Initialize a list to hold serialized wishlist data

        categorized_data = defaultdict(list)
        # Serialize each wishlist item individually
        for wishlist in wishlists:
            # Serialize the wishlist item using WishlistSerializer
            wishlist_data = WishallSerializer(wishlist, context={'request': request}).data
            brand = wishlist_data['wishlist_name']
            # wishlist_delete_all=wishlist_data['wishlistdelall']
            product_info = {
                'wishlist_product': f"{wishlist_data['wishlist_product']['parts_brand']['brand_name']} {wishlist_data['wishlist_product']['parts_category']['category_name']} {wishlist_data['wishlist_product']['subcategory_name']}",
                'url': wishlist_data['wishlist_product']['url'],
                'Wishlistdel': wishlist_data['wishlist_delete']
            }

            categorized_data[brand].append(product_info)
            # Append serialized data to the list
        categorized_data = dict(categorized_data)
        if bool(categorized_data) is not False:
            return Response(categorized_data, status=status.HTTP_200_OK)
        else:
            return Response({'Message': 'No Wishlist '}, status=status.HTTP_400_BAD_REQUEST)


class DeleteWishlistItemView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        wishid = kwargs.get('pk')
        wishlistitem = get_object_or_404(Wishlist, pk=wishid, wishlist_name=self.request.user)
        wishlistitem.delete()
        return Response({'message': 'Item removed from wishlist successfully.'}, status=status.HTTP_204_NO_CONTENT)


class DeleteAllWishlistItemsView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        Wishlist.objects.filter(wishlist_name=self.request.user).delete()
        return Response({'message': 'All items removed from wishlist successfully.'}, status=status.HTTP_200_OK)


class BaseCartView(APIView):
    COOKIE_NAME = 'cart_items'

    def get_cart_items_from_cookie(self, request):
        cart_items_json = request.COOKIES.get(self.COOKIE_NAME, '[]')
        return json.loads(cart_items_json)

    def save_cart_items_to_cookie(self, response, cart_items):
        response.set_cookie(self.COOKIE_NAME, json.dumps(cart_items), httponly=True, secure=True, max_age=3600,
                            samesite='Lax')

    def set_cart_item_cookie(self, request, response, product_id, quantity):
        cookie_name = f'cart_product_{product_id}'
        existing_quantity = int(request.COOKIES.get(cookie_name, 0))
        new_quantity = existing_quantity + quantity
        response.set_cookie(cookie_name, new_quantity, httponly=True, max_age=3600, secure=True, samesite='Lax')

    def delete_cart_item_cookie(self, response, product_id):
        cookie_name = f'cart_product_{product_id}'
        response.delete_cookie(cookie_name, path='/')
        print(f'Deleting cookie: {cookie_name}')

    def delete_all_cart_item_cookies(self, request, response):
        cart_items = self.get_cart_items_from_cookie(request)
        print(f'cart_items: {cart_items}')
        for item in cart_items:
            product_id = item['product_id']
            self.delete_cart_item_cookie(response, product_id)
        response.delete_cookie(self.COOKIE_NAME, path='/')
        print(f'Deleting cookie: {self.COOKIE_NAME}')

    def clear_cart(self, request, response):
        self.delete_all_cart_item_cookies(request, response)


class ViewCartView(BaseCartView):

    def get(self, request):
        if request.user.is_authenticated:
            cart_items = Cart.objects.filter(user=request.user)
            serializer = CartSerializer(cart_items, many=True, context={'request': request})

            if not serializer.data:
                return Response({'message': 'No cart items found.'}, status=status.HTTP_404_NOT_FOUND)

            total_price = 0
            savings = 0
            print(total_price, savings)
            for item in serializer.data:
                product_id = item.get('product')
                quantity = item.get('quantity', 0)
                if product_id is None:
                    continue
                try:
                    product = Product.objects.get(id=product_id)
                except Product.DoesNotExist:
                    continue

                final_price = product.parts_price - (product.parts_price * product.parts_offer) / 100
                carousel_saving = 0

                if 'code' in item and item['code']:
                    for code in item['code']:
                        carousel = Carousel.objects.filter(carousel_code=code).first()
                        if carousel:
                            c_final_price = final_price - final_price * (carousel.carousel_offer / 100)
                            savings_per_unit = final_price - c_final_price
                            carousel_saving += savings_per_unit
                            final_price = c_final_price
                total_price += final_price * quantity
                savings += carousel_saving * quantity
            response = Response({'cart': serializer.data, 'total_price': total_price, 'save': savings},status=status.HTTP_200_OK)

            for item in serializer.data:
                self.set_cart_item_cookie(request, response, item["product"], item["quantity"])
            return response
        else:
            cart_items = self.get_cart_items_from_cookie(request)
            cart_data = []
            total_price = 0
            savings = 0
            for item in cart_items:
                product = Product.objects.get(id=item['product_id'])
                final_price = product.parts_price - (product.parts_price * product.parts_offer) / 100
                carousel_saving = 0
                if 'code' in item:
                    for code in item['code']:
                        carousel = Carousel.objects.filter(carousel_code=code).first()
                        if carousel:
                            c_final_price = final_price - final_price * (carousel.carousel_offer / 100)
                            carousel_saving += final_price - c_final_price
                            final_price = c_final_price

                total_price += final_price * item['quantity']
                savings += carousel_saving * item['quantity']
                cart_data.append({
                    'product': product.id,
                    'quantity': item['quantity'],
                    'parts_name': CartSerializer().arrangename(product),
                    'parts_price': product.parts_price,
                    'parts_offer': product.parts_offer,
                    'discount_amount': (product.parts_price * product.parts_offer) / 100,
                    'final_price': product.parts_price - (product.parts_price * product.parts_offer) / 100,
                    'main_image': product.main_image,
                    'code': item.get('code', []),
                })

            if not cart_data:
                return Response({'message': 'No cart items found.'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'cart': cart_data, 'total_price': total_price, 'save': savings}, status=status.HTTP_200_OK)

    def post(self, request):
        if request.user.is_authenticated:
            carouselserializer = Carouselpostserializer(data=request.data)
            user = request.user
            if carouselserializer.is_valid():
                c = Carousel.objects.get(carousel_code=carouselserializer.validated_data['carousel_code'])
                print(c)
                b = Brand.objects.get(brand_name=c.carousel_brand)
                print(b)
                ct = Category.objects.get(category_name=c.carousel_category)
                print(ct)
                p = Product.objects.filter(parts_brand=b, parts_category=ct)
                print(p)
                pro = None
                for i in p:
                    crt = Cart.objects.filter(user=user)
                    print(crt)
                    if crt:
                        for j in crt:
                            print(j.product)
                            if i == j.product:
                                j.code.add(c)
                                return Response(data='Add successfully', status=status.HTTP_201_CREATED)
                    else:
                        return Response(data='Cart not found', status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(carouselserializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(data='Add successfully', status=status.HTTP_201_CREATED)
        else:
            carouselserializer = Carouselpostserializer(data=request.data)
            if carouselserializer.is_valid():
                c = Carousel.objects.get(carousel_code=carouselserializer.validated_data['carousel_code'])
                print(f"carousel:{c}")
                b = Brand.objects.get(brand_name=c.carousel_brand)
                print(f"Brand:{b}")
                ct = Category.objects.get(category_name=c.carousel_category)
                print(f"Category:{ct}")
                p = Product.objects.filter(parts_brand=b, parts_category=ct)
                print(f"part:{p}")

                cart_items = self.get_cart_items_from_cookie(request)
                for i in p:
                    for item in cart_items:
                        if item['product_id'] == i.id:
                            if 'code' in item and c.carousel_code in item['code']:
                                return Response({'message': 'code is already applied'}, status=status.HTTP_200_OK)
                            item.setdefault('code', []).append(c.carousel_code)
                            cart_data = []
                            for item in cart_items:
                                product = Product.objects.get(id=item['product_id'])
                                cart_data.append({
                                    'product': product.id,
                                    'quantity': item['quantity'],
                                    'parts_name': CartSerializer().arrangename(product),
                                    'parts_price': product.parts_price,
                                    'parts_offer': product.parts_offer,
                                    'discount_amount': (product.parts_price * product.parts_offer) / 100,
                                    'final_price': product.parts_price - (
                                            product.parts_price * product.parts_offer) / 100,
                                    'main_image': product.main_image,
                                    'code': item.get('code', []),
                                })
                            response = Response({'message': 'Added successfully', 'cart': cart_data},
                                                status=status.HTTP_200_OK)
                            self.save_cart_items_to_cookie(response, cart_items)
                            return response
                return Response({'message': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(carouselserializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartItemsCreateView(BaseCartView):

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        quantity = int(request.data.get('quantity', 1))

        if request.user.is_authenticated:
            cart_item, created = Cart.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={'quantity': quantity}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            serializer = CartSerializer(cart_item, context={'request': request})
            response = Response({'message': 'Product added/incremented in cart', 'cart': serializer.data},
                                status=status.HTTP_200_OK)
            self.set_cart_item_cookie(request, response, pk, quantity)
            return response
        else:
            cart_items = self.get_cart_items_from_cookie(request)
            for item in cart_items:
                if item['product_id'] == pk:
                    item['quantity'] += quantity
                    break
            else:
                cart_items.append({'product_id': pk, 'quantity': quantity})

            cart_data = []
            for item in cart_items:
                product = Product.objects.get(id=item['product_id'])
                cart_data.append({
                    'product': product.id,
                    'quantity': item['quantity'],
                    'parts_name': CartSerializer().arrangename(product),
                    'parts_price': product.parts_price,
                    'parts_offer': product.parts_offer,
                    'discount_amount': (product.parts_price * product.parts_offer) / 100,
                    'final_price': product.parts_price - (product.parts_price * product.parts_offer) / 100,
                    'main_image': product.main_image,
                })
            response = Response({'message': 'Product added/incremented in cart', 'cart': cart_data},
                                status=status.HTTP_200_OK)
            self.save_cart_items_to_cookie(response, cart_items)
            self.set_cart_item_cookie(request, response, pk, quantity)
            return response

    def patch(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        decrement_quantity = int(request.data.get('quantity', 1))

        if request.user.is_authenticated:
            cart_item = Cart.objects.filter(user=request.user, product=product).first()
            if cart_item:
                if cart_item.quantity > decrement_quantity:
                    cart_item.quantity -= decrement_quantity
                    cart_item.save()
                    serializer = CartSerializer(cart_item, context={'request': request})
                    response = Response({'message': 'Product decremented in cart', 'cart': serializer.data},
                                        status=status.HTTP_200_OK)
                    self.set_cart_item_cookie(request, response, pk, -decrement_quantity)
                    return response
                else:
                    cart_item.delete()
                    return Response({'message': 'Product removed from cart'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Product not in cart'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            cart_items = self.get_cart_items_from_cookie(request)
            for item in cart_items:
                if item['product_id'] == pk:
                    if item['quantity'] > decrement_quantity:
                        item['quantity'] -= decrement_quantity
                    else:
                        cart_items.remove(item)
                    break
            else:
                return Response({'message': 'Product not in cart'}, status=status.HTTP_400_BAD_REQUEST)

            cart_data = []
            for item in cart_items:
                product = Product.objects.get(id=item['product_id'])
                cart_data.append({
                    'product': product.id,
                    'quantity': item['quantity'],
                    'parts_name': CartSerializer().arrangename(product),
                    'parts_price': product.parts_price,
                    'parts_offer': product.parts_offer,
                    'discount_amount': (product.parts_price * product.parts_offer) / 100,
                    'final_price': product.parts_price - (product.parts_price * product.parts_offer) / 100,
                    'main_image': product.main_image,
                })

            response = Response({'message': 'Product decremented in cart', 'cart': cart_data},
                                status=status.HTTP_200_OK)
            self.save_cart_items_to_cookie(response, cart_items)
            self.set_cart_item_cookie(request, response, pk, -decrement_quantity)
            return response

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)

        if request.user.is_authenticated:
            cart_item = Cart.objects.filter(user=request.user, product=product).first()
            if cart_item:
                cart_item.delete()
                return Response({'message': 'Product removed from cart'}, status=status.HTTP_200_OK)
            return Response({'error': 'Product not in cart'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            cart_items = self.get_cart_items_from_cookie(request)
            updated_cart_items = [item for item in cart_items if item['product_id'] != pk]
            if len(updated_cart_items) == len(cart_items):
                return Response({'error': 'Product not in cart'}, status=status.HTTP_400_BAD_REQUEST)
            response = Response({'message': 'Product removed from cart'}, status=status.HTTP_200_OK)
            self.save_cart_items_to_cookie(response, updated_cart_items)
            self.delete_cart_item_cookie(response, pk)
        return response


class RemoveFromCartView(BaseCartView):

    def delete(self, request):
        if request.user.is_authenticated:
            Cart.objects.filter(user=request.user).delete()
            response = Response({'message': 'Product removed from cart'}, status=status.HTTP_200_OK)
            response.delete_cookie('cart')
            return response

        else:
            cart_items = self.get_cart_items_from_cookie(request)
            if not cart_items:
                return Response({'error': 'Cart is already empty'}, status=status.HTTP_400_BAD_REQUEST)
            response = Response({'message': 'Product removed from cart'}, status=status.HTTP_200_OK)
            self.clear_cart(request, response)
            return response


class Carouselallview(generics.ListAPIView):
    serializer_class = Carouselserilizers
    queryset = Carousel.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if not queryset.exists():
            return Response({'details': 'Carousel Not Found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'Carousel': serializer.data}, status=status.HTTP_200_OK)


class Carouseloneview(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        carousel_id = self.kwargs.get('pk')
        c = Carousel.objects.get(id=carousel_id)
        cat = c.carousel_category
        ban = c.carousel_brand
        queryset = Product.objects.all().filter(parts_category=cat, parts_brand=ban)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        carousel_id = self.kwargs.get('pk')
        c = Carousel.objects.get(id=carousel_id)
        if not queryset.exists():
            return Response({'details': 'Product Not Found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        carousel_serilizer = Carouselserilizers(c, context={'request': request})
        lastdata = adddict(serializer)
        return Response({'Carousel': carousel_serilizer.data, 'parts': lastdata}, status=status.HTTP_200_OK)


class BuyNowAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        product = get_object_or_404(Product, pk=pk)
        serializer = Buynowserilizers(data=request.data, context={'request': request})
        if serializer.is_valid():
            result = serializer.save()
            response_data = {
                "message": "Addresses saved successfully.",
                "billing_address": Billaddressserializer(result["billing_address"]).data,
                "shipping_address": Shippingaddressserializer(result["shipping_address"]).data if result[
                    "shipping_address"] else None
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderSummaryAPIView(BaseCartView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_profile = Profile.objects.filter(user=user).first()
        if not user_profile:
            return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

        preferred_billing_address = user_profile.preferred_billing_address
        preferred_shipping_address = user_profile.preferred_shipping_address

        products_data = request.query_params.getlist('products')
        order_items = []
        grand_total = 0

        # Debugging print to check the cookies and query parameters
        print(f"Request COOKIES: {request.COOKIES}")
        print(f"Request query params: {products_data}")

        def parse_cookie_data():
            items = []
            for key, value in request.COOKIES.items():
                if key.startswith('cart_product_'):
                    try:
                        product_id = int(key.split('_')[2])
                        quantity = int(value)
                        items.append({"product_id": product_id, "quantity": quantity})
                    except (IndexError, ValueError):
                        continue
            return items

        def parse_url_parameter_data(products_data):
            items = []
            for product_data in products_data:
                try:
                    product_id, quantity = map(int, product_data.split(','))
                    items.append({"product_id": product_id, "quantity": quantity})
                except ValueError:
                    continue
            return items

        order_items.extend(parse_cookie_data())
        if products_data:
            order_items.extend(parse_url_parameter_data(products_data))

        # Debugging print to check parsed order items
        print(f"Order items after parsing: {order_items}")

        if not order_items:
            return Response({"detail": "No products."}, status=status.HTTP_400_BAD_REQUEST)

        detailed_order_items = []

        for item in order_items:
            try:
                product = Product.objects.get(id=item["product_id"])
            except Product.DoesNotExist:
                continue

            product_serializer = ProductSerializer(product, context={'request': request})
            product_data = product_serializer.data
            total = product_data['final_price'] * item["quantity"]
            grand_total += total

            detailed_order_items.append({
                "product_id": product_data['id'],
                "product_name": product_data['parts_name'],
                "product_category": product_data['parts_category'],
                "product_brand": product_data['parts_brand'],
                "product_price": product_data['final_price'],
                "product_image": product_data['main_image'],
                "quantity": item["quantity"],
                'code': item.get('code', []),
                "total": total,
            })

        response = Response(status=status.HTTP_200_OK)
        for item in detailed_order_items:
            self.set_cart_item_cookie(request, response, item["product_id"], item["quantity"])

        response.data = {
            "preferred_billing_address": Billaddressserializer(
                preferred_billing_address).data if preferred_billing_address else None,
            "preferred_shipping_address": Shippingaddressserializer(
                preferred_shipping_address).data if preferred_shipping_address else None,
            "order_items": detailed_order_items,
            "grand_total": grand_total,
        }
        return response


class OrderAPIView(BaseCartView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user_profile = Profile.objects.filter(user=user).first()
        if not user_profile:
            return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

        order_items = []
        for key, value in request.COOKIES.items():
            if key.startswith('product_') or key.startswith('cart_product_'):
                split_index = 2 if key.startswith('cart_product_') else 1
                product_id = int(key.split('_')[split_index])
                quantity = int(value)
                order_items.append({"product_id": product_id, "quantity": quantity})

        if not order_items:
            return Response({"detail": "No order items."}, status=status.HTTP_400_BAD_REQUEST)

        orders = []
        for item in order_items:
            product_id = item['product_id']
            quantity = item['quantity']

            product = Product.objects.get(id=product_id)
            order = Order.objects.create(
                user=user,
                product=product,
                quantity=quantity,
                billing_address=user_profile.preferred_billing_address,
                shipping_address=user_profile.preferred_shipping_address,
            )

            product_order_count, created = ProductOrderCount.objects.get_or_create(product=product)
            product_order_count.order_count += quantity
            product_order_count.save()
            orders.append(order)

        if not orders:
            return Response({"detail": "No valid orders could be created."}, status=status.HTTP_400_BAD_REQUEST)

        response_data = {
            "message": "Thank you for your order!",
            "order_details": [OrderSerializer(order).data for order in orders],
        }
        order_details = [
            {
                'order_id': order.order_id,
                'product_name': order.product,
                'quantity': order.quantity,
                'order_date': order.order_date,
                'billing_address': order.billing_address,
                'shipping_address': order.shipping_address,
            } for order in orders
        ]
        data = {
            'order_details': order_details,
            'to_email': user.email,
        }
        send_confirmation_email(data)

        if request.user.is_authenticated:
            Cart.objects.filter(user=user).delete()

        response = Response(response_data, status=status.HTTP_201_CREATED)

        for item in order_items:
            self.delete_cart_item_cookie(response, item["product_id"])

        self.delete_all_cart_item_cookies(request, response)

        return response


class BestSellingView(generics.ListAPIView):
    serializer_class = Bestsellingserializer
    pagination_class = CustomPagination

    def get_queryset(self):
        threshold = 15
        return ProductOrderCount.objects.filter(order_count__gte=threshold).order_by('-order_count')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
        # page = self.paginate_queryset(self.get_queryset())
        # if page is not None:
        #     serializer = self.get_serializer(page, many=True, context={'request': request})
        #     return self.get_paginated_response(serializer.data)
        # serializer = self.get_serializer(queryset, many=True, context={'request': request})
        # return Response(serializer.data, status=status.HTTP_200_OK)


class MyOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id=None):
        user = request.user

        def get_order_details(order):
            product = order.product
            product_data = ProductSerializer(product, context={'request': request}).data
            order_details = {
                'order_id': order.order_id,
                'order_date': order.order_date,
                "product_name": product_data['parts_name'],
                "part_no": product_data['parts_no'],
                "product_price": product_data['final_price'],
                "product_image": product_data['main_image'],
                'quantity': order.quantity,
            }
            return order_details

        if order_id:
            order = get_object_or_404(Order, user=user, order_id=order_id)
            order_details = get_order_details(order)
            return Response(order_details, status=status.HTTP_404_NOT_FOUND)
        orders = Order.objects.filter(user=user)
        if not orders:
            return Response({"detail": "No orders found."}, status=status.HTTP_404_NOT_FOUND)
        all_order_details = [get_order_details(order) for order in orders]
        return Response(all_order_details, status=status.HTTP_200_OK)

    def delete(self, request, order_id=None):
        if not order_id:
            return Response({"detail": "Order ID required"}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        order = get_object_or_404(Order, user=user, order_id=order_id)
        product_order_count = get_object_or_404(ProductOrderCount, product=order.product)
        product_order_count.order_count -= order.quantity
        if product_order_count.order_count <= 0:
            product_order_count.order_count = 0
        product_order_count.save()

        order.delete()
        return Response({"detail": "Order deleted."}, status=status.HTTP_204_NO_CONTENT)
