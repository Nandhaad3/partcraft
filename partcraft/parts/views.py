import json
import random
from django.utils.timezone import now
from django.db.migrations import serializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import status, generics
from django.db.models import F, Q
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from .serializers import *
from collections import defaultdict
from pymongo import MongoClient
from rest_framework.parsers import MultiPartParser, FormParser
from account.emails import send_confirmation_email
from django.contrib.auth import login
from account.models import User
# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import A4
from io import BytesIO
from django.utils import timezone
from django.core.mail import EmailMessage, EmailMultiAlternatives
from .models import mongo_models as mongodb
from django.template.loader import render_to_string
from weasyprint import HTML
from io import BytesIO

def adddict(serializer):
    last_data = []
    for i in serializer.data:
        data = {}
        data['id'] = i['id']
        data['parts_type'] = i['parts_type']
        data['main_image'] = i['main_image']
        data['brand_image'] = i['parts_brand']['brand_image']
        data['brand'] = i['parts_brand']
        d = (f"{i['parts_brand']['brand_name']} "
             f"{i['parts_category']['category_name']} "
             f'{i["subcategory_name"]}'
             f"{i['parts_voltage']} "
             f"{i['parts_litre']}L ")
        data['parts_name'] = d.replace('NoneL', '').strip()
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
        data['addtocart'] = i['addtocart']
        data['product_fit'] = i['product_fit']
        last_data.append(data)
    return last_data


class CustomPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'size'
    max_page_size = 10


class partslistview(generics.ListAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ProductoneSerializer
    pagination_class = CustomPagination
    queryset = Product.objects.all()
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(self.get_queryset())
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response({'data':serializer.data}, status=status.HTTP_200_OK)


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
            return Response({'data': 'Product Not Found'}, status=status.HTTP_404_NOT_FOUND)

        product = queryset.first()
        serializer = self.get_serializer(product)
        data = serializer.data

        if data.get('is_in_wishlist'):
            data.pop('wishlist', None)

        return Response({'data':data}, status=status.HTTP_200_OK)


class categorylistview(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if not queryset.exists():
            raise NotFound(detail="No Category found matching the criteria.")
        serializer = self.get_serializer(queryset, many=True)
        return Response({'data':serializer.data}, status=status.HTTP_200_OK)


class categoryonedetail(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        category_id = self.kwargs.get('pk')
        category_str = self.kwargs.get('code')
        if category_id:
            cat = Category.objects.get(id=category_id)
            quaryset = Product.objects.all().filter(parts_category_id=cat.id)
            return quaryset
        if category_str:
            cat = Category.objects.get(code=category_str)
            quaryset = Product.objects.all().filter(parts_category_id=cat.id)
            return quaryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        category_id = self.kwargs.get('pk')
        category_str= self.kwargs.get('code')
        if category_id:
            cat = Category.objects.get(id=category_id)
            if not queryset.exists():
                return Response({'details': 'Product Not Found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = self.get_serializer(queryset, many=True)
            category_serializer = CategorySerializer(cat, context={'request': request})
            lastdata = adddict(serializer)
            return Response({'data': category_serializer.data, 'results': lastdata}, status=status.HTTP_200_OK)
        if category_str:
            print(category_str)
            cat = Category.objects.get(code=category_str)
            if not queryset.exists():
                return Response({'details': 'Product Not Found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = self.get_serializer(queryset, many=True)
            category_serializer = CategorySerializer(cat, context={'request': request})
            lastdata = adddict(serializer)
            return Response({'data': category_serializer.data, 'results': lastdata}, status=status.HTTP_200_OK)



class brandlistview(generics.ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if not queryset.exists():
            raise NotFound(detail="No Brand found matching the criteria.")
        serializer = self.get_serializer(queryset, many=True)
        return Response({'data':serializer.data}, status=status.HTTP_200_OK)


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
            return Response({'data': 'Product Not Found'}, status=status.HTTP_200_OK)
        serializer = self.get_serializer(queryset, many=True)
        brand_serializer = BrandSerializer(brand, context={'request': request})
        lastdata = adddict(serializer)
        return Response({'data': brand_serializer.data, 'data': lastdata}, status=status.HTTP_200_OK)


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
        applicationserializer = ApplicationSerializer(data=request.data)
        if applicationserializer.is_valid():
            try:
                vehicle = Vehicle.objects.filter(
                    vehicle_make=applicationserializer.validated_data['vehicle_make'],
                    vehicle_variant=applicationserializer.validated_data['vehicle_variant'],
                    vehicle_model=applicationserializer.validated_data['vehicle_model'],
                    vehicle_year=applicationserializer.validated_data['vehicle_year'],
                )
                v = []
                for i in vehicle:
                    this_part = Product.objects.filter(this_parts_fits=i)
                    productserializer = ProductSerializer(this_part, context={'request': request}, many=True)
                    v.append(productserializer.data)

                lastdata = adddict(productserializer)

                vehicle_data = VehicleoneSerializer(vehicle, many=True, context={'request': request}).data

                response = Response({'vehicle': applicationserializer.data, 'parts': lastdata}, status=status.HTTP_200_OK)

                response.set_cookie('vehicle', json.dumps(vehicle_data))
                print("cookies set response:")
                for key, value in response.cookies.items():
                    print(f"{key}, {value}")
                return response
            except Vehicle.DoesNotExist:
                return Response({'data': 'Vehicle not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(applicationserializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        queryset = Vehicle.objects.all()
        serializer = ApplicationSerializer(queryset, many=True, context={'request': request})
        return Response({'data':serializer.data}, status=status.HTTP_200_OK)

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
        return Response({'data': vehicle_serializer.data, 'parts': lastdata}, status=status.HTTP_200_OK)


class MatchVehicle(APIView):
    def post(self, request, *args, **kwargs):
        year = request.data.get('year')
        model = request.data.get('model')

        filters = {}
        if year:
            if isinstance(year,(int,str)):
                year = int(year)
                filters['vehicle_year'] = year
            else:
                return Response({'details': 'Invalid format of year'}, status=status.HTTP_400_BAD_REQUEST)

        if model:
            if isinstance(model, str):
                filters['vehicle_model'] = model
            else:
                return Response({'details': 'Invalid of model'}, status=status.HTTP_400_BAD_REQUEST)

        vehicles = Vehicle.objects.filter(**filters)

        if not vehicles.exists():
            return Response({'details': 'Vehicle Not Found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ApplicationSerializer(vehicles, many=True, context={'request': request})
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

class VehicleTypeView(generics.ListAPIView):
    serializer_class = ApplicationcategorySerializer
    queryset = Application_category.objects.all()
    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        if queryset:
            serializer = self.serializer_class(queryset, many=True)
            return Response({'data':serializer.data}, status=status.HTTP_200_OK)
        return Response({'message': 'Data Not Found'}, status=status.HTTP_404_NOT_FOUND)


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
            return Response({'data': 'Product Not Found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)
        categorized_data = category_offer(serializer.data)

        return Response({'data': categorized_data}, status=status.HTTP_200_OK)



class WishlistCreateView(generics.ListCreateAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
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
        if not product:
            return Response({"error": "Product not found."}, status=status.HTTP_200_OK)

        existing_wishlist = Wishlist.objects.filter(wishlist_name=self.request.user, wishlist_product=product).exists()
        if existing_wishlist:
            return Response({"message": "Product is already in the wishlist."}, status=status.HTTP_200_OK)

        data = {
            'wishlist_name': self.request.user,
            'wishlist_product': product
        }
        s = self.get_serializer(data=data)
        self.perform_create(s)

        headers = self.get_success_headers(serializer)
        return Response({'message': 'Wishlist created successfully'}, status=status.HTTP_200_OK, headers=headers)

    def perform_create(self, serializer):
        if serializer.is_valid(raise_exception=True):
            serializer.save(wishlist_name=self.request.user, wishlist_product=self.get_product())


class WishallView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        wishlists = Wishlist.objects.filter(wishlist_name=self.request.user)
        move_to_cart_url = request.build_absolute_uri(reverse('move-to-cart'))
        delete_all_wishlist_url = request.build_absolute_uri(reverse('delete-all-wishlistitems'))
        product_info={}
        wish=[]
        for wishlist in wishlists:
            wishlist_data = WishallSerializer(wishlist, context={'request': request}).data
            product_info = {
                'product_id': wishlist_data['wishlist_product']['id'],
                'wishlist_product': f"{wishlist_data['wishlist_product']['parts_brand']['brand_name']} {wishlist_data['wishlist_product']['parts_category']['category_name']} {wishlist_data['wishlist_product']['subcategory_name']}",
                'parts_no': wishlist_data['parts_no'],
                'brand_logo': wishlist_data['brand_logo'],
                'parts_category': wishlist_data['parts_category'],
                'parts_type': wishlist_data['parts_type'],
                'parts_price': wishlist_data['parts_price'],
                'parts_offer': wishlist_data['parts_offer'],
                'final_price': wishlist_data['final_price'],
                'main_image': wishlist_data['main_image'],
                'url': wishlist_data['wishlist_product']['url'],
                'addtocart': wishlist_data['addtocart'],
                'Wishlistdel': wishlist_data['wishlist_delete'],
            }
            categorized_data = dict(product_info)
            wish.append(categorized_data)

        response = Response({
            'product': wish,
            'move_to_cart': move_to_cart_url,
            'delete_all_wishlist': delete_all_wishlist_url,
             },
            status=status.HTTP_200_OK)
        if bool(wish) is not False:
            return response
        else:
            return Response({'data': []}, status=status.HTTP_200_OK)


class MoveToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user

        product_ids = request.data.get('product_ids', [])

        if not product_ids:
            return Response({"detail": "Product IDs are required in the request body."},status=status.HTTP_400_BAD_REQUEST)

        messages = []

        for product_id in product_ids:
            product_id = int(product_id)
            product = get_object_or_404(Product, pk=product_id)

            wishlist_item = Wishlist.objects.filter(wishlist_name=user, wishlist_product=product).first()
            if not wishlist_item:
                messages.append({"product_id": product_id, "message": "Product not found in wishlist."})
                continue

            cart_item, created = Cart.objects.get_or_create(user=user, product=wishlist_item.wishlist_product)
            cart_item.save()

            wishlist_item.delete()
            messages.append({"product_id": product_id, "message": "Item moved to cart successfully."})
        return Response({"messages": messages}, status=status.HTTP_200_OK)

class DeleteWishlistItemView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        wishid = kwargs.get('pk')
        wishlistitem = get_object_or_404(Wishlist, pk=wishid, wishlist_name=self.request.user)
        wishlistitem.delete()
        return Response({'message': 'Item removed from wishlist successfully.'}, status=status.HTTP_200_OK)


class DeleteAllWishlistItemsView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        Wishlist.objects.filter(wishlist_name=self.request.user).delete()
        return Response({'message': 'All items removed from wishlist successfully.'}, status=status.HTTP_200_OK)


class BaseCartView(APIView):
    COOKIE_NAME = 'cart_items'  # Single cookie for cart items

    def get_cart_items_from_cookie(self, request):
        cart_items_json = request.COOKIES.get(self.COOKIE_NAME, '[]')
        return json.loads(cart_items_json)

    def save_cart_items_to_cookie(self, response, cart_items):
        response.set_cookie(
            self.COOKIE_NAME,
            json.dumps(cart_items),
            httponly=True,
            secure=True,
            max_age=3600,
            samesite='None'
        )

    def delete_cart_item_cookie(self, response, product_id):
        cookie_name = f'cp_{product_id}'
        response.delete_cookie(cookie_name)

    def clear_cart(self, response):
        response.delete_cookie(self.COOKIE_NAME, path='/')

    def update_cart_cookie(self, request, response, product_id, quantity, code=None):
        cart_items = self.get_cart_items_from_cookie(request)
        item_exists = False

        for item in cart_items:
            if item['product_id'] == product_id:
                item['quantity'] += quantity
                if code:
                    item.setdefault('code', []).append(code)
                item_exists = True
                break

        if not item_exists:
            cart_items.append({'product_id': product_id, 'quantity': quantity, 'code': [code] if code else []})

        self.save_cart_items_to_cookie(response, cart_items)

    def remove_item_from_cart_cookie(self, request, response, product_id):
        cart_items = self.get_cart_items_from_cookie(request)
        updated_cart_items = [item for item in cart_items if item['product_id'] != product_id]

        if len(updated_cart_items) != len(cart_items):
            self.save_cart_items_to_cookie(response, updated_cart_items)

        return len(updated_cart_items) != len(cart_items)

    def process_cart_data(self, cart_items):
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
                'final_price': final_price,
                'main_image': product.main_image,
                'code': item.get('code', []),
            })

        return cart_data, total_price, savings


class ViewCartView(BaseCartView):

    def get(self, request):
        if request.user.is_authenticated:
            cart_items = Cart.objects.filter(user=request.user)
            serializer = CartSerializer(cart_items, many=True, context={'request': request})

            if not serializer.data:
                return Response({'message': 'No cart items found.'}, status=status.HTTP_404_NOT_FOUND)

            total_price, savings = self.calculate_totals(serializer.data)
            checkout_url = request.build_absolute_uri(reverse('billing_addres'))
            response = Response({'cart': serializer.data, 'check_out:': checkout_url,'total_price': total_price, 'save': savings},
                                status=status.HTTP_200_OK)

            self.save_cart_items_to_cookie(response, serializer.data)
            return response
        else:
            cart_items = self.get_cart_items_from_cookie(request)
            cart_data, total_price, savings = self.process_cart_data(cart_items)

            checkout_url = request.build_absolute_uri(reverse('billing_addres'))

            if not cart_data:
                return Response({'message': 'No cart items found.'}, status=status.HTTP_204_NO_CONTENT)

            return Response({'cart': cart_data, 'check_out':checkout_url,'total_price': total_price, 'save': savings}, status=status.HTTP_200_OK)

    def calculate_totals(self, cart_items):
        total_price = 0
        savings = 0

        for item in cart_items:
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

        return total_price, savings

    def post(self, request):
        if request.user.is_authenticated:
            carouselserializer = Carouselpostserializer(data=request.data)
            user = request.user
            if carouselserializer.is_valid():
                c = Carousel.objects.get(carousel_code=carouselserializer.validated_data['carousel_code'])
                b = Brand.objects.get(brand_name=c.carousel_brand)
                ct = Category.objects.get(category_name=c.carousel_category)
                p = Product.objects.filter(parts_brand=b, parts_category=ct)
                pro = None
                for i in p:
                    crt = Cart.objects.filter(user=user)
                    if crt:
                        for j in crt:
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
                b = Brand.objects.get(brand_name=c.carousel_brand)
                ct = Category.objects.get(category_name=c.carousel_category)
                p = Product.objects.filter(parts_brand=b, parts_category=ct)

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


class RemoveCarouselView(APIView):
    COOKIE_NAME = 'cart_items'
    def get_cart_items_from_cookie(self, request):
        cart_items_json = request.COOKIES.get(self.COOKIE_NAME, '[]')
        return json.loads(cart_items_json)
    def save_cart_items_to_cookie(self, response, cart_items):
        response.set_cookie(self.COOKIE_NAME,json.dumps(cart_items),
            httponly=True,secure=True,
            max_age=3600,samesite='None')

    def _remove_carousel_from_products(self, carousel, products, request, user=None):
        if user and user.is_authenticated:
            carts = Cart.objects.filter(user=user)
            if not carts:
                return {'message': 'Cart not found'}, status.HTTP_404_NOT_FOUND

            for product in products:
                for cart in carts:
                    if product == cart.product:
                        if carousel in cart.code.all():
                            cart.code.remove(carousel)
                            return {'message': 'Removed successfully'}, status.HTTP_200_OK
            return {'message': 'Code not found in cart'}, status.HTTP_404_NOT_FOUND
        else:
            cart_items = self.get_cart_items_from_cookie(request)
            code_removed = False
            for item in cart_items:
                if 'code' in item and carousel.carousel_code in item['code']:
                    item['code'].remove(carousel.carousel_code)
                    code_removed = True

            if not code_removed:
                return {'message': 'Code not found in cart'}, status.HTTP_404_NOT_FOUND

            response = Response({'message': 'Removed successfully'},
                                status=status.HTTP_200_OK)
            self.save_cart_items_to_cookie(response, cart_items)
            return response, status.HTTP_200_OK

    def post(self, request):
        if request.user.is_authenticated:
            carouselserializer = Carouselpostserializer(data=request.data)
            user = request.user

            if carouselserializer.is_valid():
                try:
                    c = Carousel.objects.get(carousel_code=carouselserializer.validated_data['carousel_code'])
                    b = Brand.objects.get(brand_manufacturer=c.carousel_brand.brand_manufacturer)
                    ct = Category.objects.get(category_name=c.carousel_category)
                    p = Product.objects.filter(parts_brand=b, parts_category=ct)

                    crt = orders.objects.get(orderedby=user)
                    order_items = orderitems.objects.filter(order_id=crt.ID)

                    for i in p:
                        if order_items:
                            for j in order_items:
                                if i == j.product:
                                    u = User.objects.get(id=user.id)
                                    user_coupon = Usercoupon.objects.filter(user=u, product=j.product.id)

                                    # Debugging output
                                    print(
                                        f"User ID: {u.id}, Product ID: {j.product.id}, User Coupon Exists: {user_coupon.exists()}")

                                    # If a user coupon exists for the product, delete it
                                    if user_coupon.exists():
                                        user_coupon.delete()
                                        return Response(data='Coupon deleted successfully',
                                                        status=status.HTTP_204_NO_CONTENT)
                                    else:
                                        return Response(data='No coupon to delete for this product',
                                                        status=status.HTTP_404_NOT_FOUND)

                        else:
                            return Response(data='Cart not found', status=status.HTTP_404_NOT_FOUND)

                    # If no matching product was found in the user's order
                    return Response(data='Product not found in cart', status=status.HTTP_404_NOT_FOUND)

                except Carousel.DoesNotExist:
                    return Response(data="Carousel code not found", status=status.HTTP_404_NOT_FOUND)
                except Brand.DoesNotExist:
                    return Response(data="Brand not found", status=status.HTTP_404_NOT_FOUND)
                except Category.DoesNotExist:
                    return Response(data="Category not found", status=status.HTTP_404_NOT_FOUND)
                except orders.DoesNotExist:
                    return Response(data="Order not found for user", status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(carouselserializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(data="User not authenticated", status=status.HTTP_401_UNAUTHORIZED)


class CartItemsCreateView(BaseCartView):

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        quantity = int(request.data.get('quantity', 1))

        if request.user.is_authenticated:
            # Get or create a cart item for the user and product
            cart_item, created = Cart.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={'quantity': quantity}
            )
            # If the cart item already exists, increment the quantity
            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            # Serialize the cart item
            serializer = CartSerializer(cart_item, context={'request': request})
            response = Response({
                'message': 'Product added/incremented in cart',
                'cart': serializer.data
            }, status=status.HTTP_200_OK)

            return response
        else:
            response = self.handle_unauthenticated_cart(request, pk, quantity)
            return response

    def handle_unauthenticated_cart(self, request, product_id, quantity):
        response = Response({'message': 'Product added/incremented in cart'}, status=status.HTTP_200_OK)
        self.update_cart_cookie(request, response, product_id, quantity)
        cart_items = self.get_cart_items_from_cookie(request)
        cart_data, _, _ = self.process_cart_data(cart_items)
        response.data.update({'cart': cart_data})
        return response

    def patch(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        decrement_quantity = int(request.data.get('quantity', 1))

        if request.user.is_authenticated:
            return self.handle_authenticated_cart_patch(request, pk, product, decrement_quantity)
        else:
            return self.handle_unauthenticated_cart_patch(request, pk, decrement_quantity)

    def handle_authenticated_cart_patch(self, request, pk, product, decrement_quantity):
        cart_item = Cart.objects.filter(user=request.user, product=product).first()
        if cart_item:
            if cart_item.quantity > decrement_quantity:
                cart_item.quantity -= decrement_quantity
                cart_item.save()
                serializer = CartSerializer(cart_item, context={'request': request})
                response = Response({'message': 'Product decremented in cart', 'cart': serializer.data},
                                    status=status.HTTP_200_OK)
                self.update_cart_cookie(request, response, pk, -decrement_quantity)
                return response
            else:
                cart_item.delete()
                response = Response({'message': 'Product removed from cart'}, status=status.HTTP_200_OK)
                self.remove_item_from_cart_cookie(request, response, pk)
                return response
        else:
            return Response({'message': 'Product not in cart'}, status=status.HTTP_400_BAD_REQUEST)

    def handle_unauthenticated_cart_patch(self, request, pk, decrement_quantity):
        cart_items = self.get_cart_items_from_cookie(request)
        response = Response({'message': 'Product decremented in cart'}, status=status.HTTP_200_OK)

        for item in cart_items:
            if item['product_id'] == pk:
                if item['quantity'] > decrement_quantity:
                    item['quantity'] -= decrement_quantity
                else:
                    cart_items.remove(item)
                break
        else:
            return Response({'message': 'Product not in cart'}, status=status.HTTP_400_BAD_REQUEST)

        self.save_cart_items_to_cookie(response, cart_items)
        cart_data, _, _ = self.process_cart_data(cart_items)
        response.data.update({'cart': cart_data})
        return response

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)

        if request.user.is_authenticated:
            cart_item = Cart.objects.filter(user=request.user, product=product).first()
            if cart_item:
                cart_item.delete()
                response = Response({'message': 'Product removed from cart'}, status=status.HTTP_200_OK)
                self.remove_item_from_cart_cookie(request, response, pk)
                return response
            else:
                return Response({'message': 'Product not in cart'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return self.handle_unauthenticated_cart_delete(request, pk)

    def handle_unauthenticated_cart_delete(self, request, product_id):
        response = Response({'message': 'Product removed from cart'}, status=status.HTTP_200_OK)
        item_removed = self.remove_item_from_cart_cookie(request, response, product_id)

        if not item_removed:
            return Response({'message': 'Product not in cart'}, status=status.HTTP_400_BAD_REQUEST)

        cart_items = self.get_cart_items_from_cookie(request)
        cart_data, _, _ = self.process_cart_data(cart_items)
        response.data.update({'cart': cart_data})
        return response

class RemoveFromCartView(BaseCartView):
    def delete(self, request):
        response = self.clear_cart(request)
        return response

class Carouselallview(generics.ListAPIView):
    serializer_class = Carouselserilizers
    queryset = Carousel.objects.all()
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if not queryset.exists():
            return Response({'data': 'Carousel Not Found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

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
            return Response({'data': 'Product Not Found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        carousel_serilizer = Carouselserilizers(c, context={'request': request})
        lastdata = adddict(serializer)
        return Response({'data': carousel_serilizer.data, 'parts': lastdata}, status=status.HTTP_200_OK)

class ShippingAdressAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        serializer = Shippingaddressserializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            result = serializer.save()
            response_data = {
                "message": "shipping address saved successfully.",
                "shipping_address": Shippingaddressserializer(result).data
            }
            return Response({'data': response_data}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            shipping_address = ShippingAddress.objects.filter(user=request.user).order_by('-id').first()
            if shipping_address:
                serializer = Shippingaddressserializer(shipping_address)
                return Response({'data': serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response()
class BillingAddressAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        serializer = Billaddressserializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            result = serializer.save()
            response_data = {
                "billing_address": Billaddressserializer(result).data
            }
            return Response({"message": "billing address saved successfully.", 'data': response_data}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class OrderSummaryAPIView(BaseCartView):
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request):
#         user = request.user
#         products_data = request.query_params.getlist('products')
#         order_items = []
#         grand_total = 0
#
#         def parse_url_parameter_data(products_data):
#             items = []
#             for product_data in products_data:
#                 try:
#                     product_id, quantity = map(int, product_data.split(','))
#                     items.append({"product_id": product_id, "quantity": quantity})
#                 except ValueError:
#                     continue
#             return items
#
#         if request.user.is_authenticated:
#             cart_items = Cart.objects.filter(user=user)
#             if cart_items.exists():
#                 for item in cart_items:
#                     order_items.append({
#                         "product": item.product.id,
#                         "quantity": item.quantity,
#                         "code": list(item.code.values_list('id', flat=True))  # Convert to a list for serialization
#                     })
#         else:
#             order_item = self.get_cart_items_from_cookie(request)
#             order_data, _, _ = self.process_cart_data(order_item)
#             order_items.extend(order_data)
#
#         if products_data:
#             order_items.extend(parse_url_parameter_data(products_data))
#
#         if not order_items:
#             return Response({"detail": "No products."}, status=status.HTTP_400_BAD_REQUEST)
#
#         detailed_order_items = []
#
#         for item in order_items:
#             try:
#                 product = Product.objects.get(id=item["product"])
#             except Product.DoesNotExist:
#                 continue
#
#             product_serializer = TestProductSerializer(product, context={'request': request})
#             product_data = product_serializer.data
#             total = product_data['final_price'] * item["quantity"]
#             grand_total += total
#
#             detailed_order_items.append({
#                 "product_id": product_data['id'],
#                 "product_name": product_data['parts_name'],
#                 "product_category": product_data['parts_category'],
#                 "product_brand": product_data['parts_brand'],
#                 "product_price": product_data['final_price'],
#                 "product_image": product_data['main_image'],
#                 "quantity": item["quantity"],
#                 'code': item.get('code', []),
#                 "total": total,
#             })
#
#         datas = {
#             "order_items": detailed_order_items,
#             "grand_total": grand_total
#         }
#
#         order_summary_data = {
#             "billing_address": datas["billing_address"],
#             "dealer_address": datas["dealer_address"],
#             "order_items": detailed_order_items,
#             "grand_total": grand_total
#         }
#
#         # Ensure everything is serializable
#         order_summary_json = json.dumps(order_summary_data)
#
#         # Create the response
#         response = Response({'data': datas}, status=status.HTTP_200_OK)
#
#         # Set the serialized order summary data in the cookies
#         response.set_cookie('order_summary', order_summary_json, max_age=3600, httponly=True)
#
#         return response

class OrderAPIView(BaseCartView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        order_items = request.COOKIES['order_summary']
        j=json.loads(order_items)
        order_item=j['order_items']

        if not order_items:
            return Response({"detail": "No order items."}, status=status.HTTP_400_BAD_REQUEST)

        orders = []
        for item in order_item:
            product_id = item['product_id']
            quantity = item['quantity']

            product = Product.objects.get(id=product_id)
            order = Order.objects.create(
                user=user,
                product=product,
                quantity=quantity,
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

        self.clear_cart(response)
        response.delete_cookie('order_summary')

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
        return Response({'data':serializer.data}, status=status.HTTP_200_OK)
        # page = self.paginate_queryset(self.get_queryset())
        # if page is not None:
        #     serializer = self.get_serializer(page, many=True, context={'request': request})
        #     return self.get_paginated_response(serializer.data)
        # serializer = self.get_serializer(queryset, many=True, context={'request': request})
        # return Response(serializer.data, status=status.HTTP_200_OK)


class ToptenView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = Toptenserializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if not queryset.exists():
            raise NotFound(detail="No Product")
        serializer = self.get_serializer(queryset, many=True)
        return Response({'data':serializer.data}, status=status.HTTP_200_OK)


class ToptenProductView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        category_id = self.kwargs.get('pk')
        cat = Category.objects.get(id=category_id)
        queryset = Product.objects.filter(parts_category_id=cat.id).annotate(
            order_count=F('productordercount__order_count')
        ).filter(
            Q(order_count__gt=0) | Q(order_count__isnull=False)
                 ).order_by('-order_count')[:2]
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        category_id = self.kwargs.get('pk')
        cat = Category.objects.get(id=category_id)

        if not queryset.exists():
            return Response({'data': 'No Products Found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)
        category_serializer = Toptenserializer(cat, context={'request': request})
        lastdata = adddict(serializer)
        return Response({
            'Category': category_serializer.data,
            'parts': lastdata
        }, status=status.HTTP_200_OK)

class FeedbackView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def get(self, request):
        feedbacks = Feedback.objects.all()
        serializer = FeedbackSerializer(feedbacks, many=True)
        return Response({'data':serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'data':'Feedback has successfully created'}, status=status.HTTP_201_CREATED)
        return Response({'data':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


def get_random_id(model):
    ids = model.objects.values_list('id', flat=True)
    if not ids:
        return None
    return random.choice(ids)

class RandomProductView(APIView):
    def get(self, request):
        random_id = get_random_id(Product)
        if random_id:
            instance = Product.objects.get(id=random_id)
            serializer = RandomSerializer(instance, context={'request': request})
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)
        return Response({'data': None}, status=status.HTTP_404_NOT_FOUND)


class ProductTagsApiView(APIView):
    def get(self, request):
        product_tags = ProductTags.objects.all()
        serializer = ProductTagSerializer(product_tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ApplicationTypeView(APIView):
    def get(self, request):
        application_types = Application_type.objects.all()
        serializer = ApplicationTypeSerializer(application_types, many=True, context={'request':request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class ApplicationCategoryView(APIView):
    def get(self, request, id=None):
        if id:
            application_type = Application_type.objects.get(id=id)
            application_categories = Application_category.objects.filter(type_name=application_type)
        else:
            application_categories = Application_category.objects.all()
        serializer = ApplicationCategorySerializer(application_categories, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class ApplicationView(APIView):
    def get(self, request, id=None):
        if id:
            applications_categories = Application_category.objects.get(id=id)
            application = Vehicle.objects.filter(Vehicle_category=applications_categories)
        else:
            application = Vehicle.objects.all()

        serializer = ApplicationSerializer(application, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class SellerView(APIView):
    def get(self, request, id=None):
        seller = Seller.objects.all()
        serializer = SellerSerializer(seller, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetSellersByGroupNameAPIView(APIView):
    def post(self, request):
        group_name = request.data.get('group')

        if not group_name:
            return Response({'message': 'Group name not provided'}, status=status.HTTP_400_BAD_REQUEST)

        seller_group = SellerGroup.objects.filter(group__iexact=group_name).first()

        if not seller_group:
            return Response({'message': 'Group does not exist'}, status=status.HTTP_404_NOT_FOUND)

        sellers = Seller.objects.filter(group=seller_group)

        if sellers.exists():
            serializer = SellerSerializer(sellers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({'message': 'No sellers found in this group'}, status=status.HTTP_404_NOT_FOUND)
    def get(self, request):
        seller_group = SellerGroup.objects.all()
        serializer = SellergroupSerializer(seller_group, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SelectSellerAddressAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        seller_id = request.data.get('seller_id')
        if not seller_id:
            return Response({'message': 'Seller ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            seller = Seller.objects.get(id=seller_id)
        except Seller.DoesNotExist:
            return Response({'message': 'Seller not found.'}, status=status.HTTP_404_NOT_FOUND)

        selected_seller, created = SelectedSeller.objects.update_or_create(
            user=request.user,
            defaults={'seller': seller}
        )

        serializer = SellerSerializer(seller, context={'request': request})
        response_message = "Seller selected successfully."
        if not created:
            response_message = "Seller updated successfully."

        response = Response({
            "message": response_message,
            "selected_seller": serializer.data
        }, status=status.HTTP_200_OK)
        return response


class PreferencesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        u=request.user
        prefer = SellerPreferces.objects.get(user=u)
        b=[]
        for i in prefer.seller.all():
            b.append(f'{i.name} {i.address}')
        data={'user':prefer.user.email,'seller':b}
        return Response({'data': data}, status=status.HTTP_200_OK)

    def post(self, request):
        seller_id = request.data.get('seller_id', [])
        print(seller_id)
        user = request.user
        if seller_id:
            u = User.objects.get(id=user.id)
            b = []
            for i in seller_id:
                try:
                    s = Seller.objects.get(id=i)
                    b.append(s)
                except:
                    print('not found')

            l = SellerPreferces.objects.filter(user=u)
            if bool(l) is False:
                SellerPreferces.objects.create(user=u)
            o = SellerPreferces.objects.get(user=u)
            for i in b:
                o.seller.add(i.id)
            return Response({'message': 'Seller selected successfully.'}, status=status.HTTP_200_OK)
        return Response({'message': 'Seller_id not found.'}, status=status.HTTP_404_NOT_FOUND)
    def delete(self, request):
        seller_id = request.data.get('seller_id', [])
        print(seller_id)
        user = request.user
        if seller_id:
            u = User.objects.get(id=user.id)
            b = []
            for i in seller_id:
                try:
                    s = Seller.objects.get(id=i)
                    b.append(s)
                except:
                    print('not found')
            o = SellerPreferces.objects.get(user=u.id)
            for i in b:
                o.seller.remove(i.id)
            # p=SellerPreferces(user_id=seller_id, data=data)
            return Response({'message': 'Seller Deleted successfully.'}, status=status.HTTP_200_OK)
        return Response({'message': 'Seller_id not found.'}, status=status.HTTP_404_NOT_FOUND)


class CreateCartItem(APIView):
    def post(self, request, format=None):
        user = request.user
        data = request.data

        order_status_new, created = OrderStatus.objects.get_or_create(order_status='New')

        if user.is_authenticated:
            active_order, created = orders.objects.get_or_create(
                orderedby=user,
                orderstatus=order_status_new
            )
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key

            active_order, created = orders.objects.get_or_create(
                session_key=session_key,
                orderstatus=order_status_new
            )

        products_data = request.data.get('product_id', [])
        products_data = {'product_id': products_data}
        print(products_data)

        response_data = []
        for product_datas in products_data['product_id']:
            # print(type(product_datas))
            # product_id = product_datas.get('product_id')

            product = Product.objects.filter(id=product_datas).first()
            if not product:
                return Response({"error": f"Product with id {product_datas} not found."}, status=status.HTTP_404_NOT_FOUND)

            inventory, _ = ProductInventory.objects.get_or_create(product=product)

            if inventory.instock_count <= inventory.back_order_threshold:
                return Response({"error": f"Product {product} is out of stock."}, status=status.HTTP_400_BAD_REQUEST)

            order_item, created = orderitems.objects.get_or_create(
                order=active_order,
                product=product,
                defaults={'quantity': 1}
            )

            if not created:
                if order_item.quantity + 1 > inventory.reversed_count:
                    return Response(
                        {"error": f"You cannot add more than {inventory.reversed_count} items for {product.name}."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                order_item.quantity += 1
                order_item.save()

            inventory.instock_count -= 1
            inventory.items_left = inventory.instock_count
            inventory.save()

            self.apply_order_item_costs(order_item)
            self.apply_order_costs(active_order)

            serializer = OrderItemSerializer(order_item, context={'request': request})
            response_data.append(serializer.data)

        return Response(response_data, status=status.HTTP_201_CREATED)

    def put(self, request, format=None):
        user = request.user
        data = request.data

        order_status_new, created = OrderStatus.objects.get_or_create(order_status='New')

        if user.is_authenticated:
            active_order = orders.objects.filter(
                orderedby=user,
                orderstatus=order_status_new
            ).first()
        else:
            session_key = request.session.session_key
            if not session_key:
                return Response({"error": "Session not found."}, status=status.HTTP_400_BAD_REQUEST)

            active_order = orders.objects.filter(
                session_key=session_key,
                orderstatus=order_status_new
            ).first()

        if not active_order:
            return Response({"error": "No active order found."}, status=status.HTTP_404_NOT_FOUND)

        product_id = data.get('product_id')

        product = Product.objects.filter(id=product_id).first()
        if not product:
            return Response({"error": f"Product with id {product_id} not found."}, status=status.HTTP_404_NOT_FOUND)

        inventory, _ = ProductInventory.objects.get_or_create(product=product)

        order_item = orderitems.objects.filter(order=active_order, product=product).first()
        if not order_item:
            return Response({"error": "Order item not found."}, status=status.HTTP_404_NOT_FOUND)

        if order_item.quantity > 1:
            order_item.quantity -= 1
            order_item.save()
            inventory.instock_count += 1
        else:
            order_item.delete()
            inventory.instock_count += 1

        self.apply_order_item_costs(order_item)
        self.apply_order_costs(active_order)

        inventory.items_left = inventory.instock_count
        inventory.save()

        serializer = OrderItemSerializer(order_item, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def apply_order_item_costs(self, order_item):
        item_level_costs = Costtypes.objects.filter(is_order_item_level_cost=True)

        product_cost = Product_cost.objects.filter(product_id=order_item.product).first()

        if not product_cost:
            raise ValueError("No product cost found for the given product.")

        currency_code = product_cost.product_currency

        for cost_type in item_level_costs:
            if cost_type.transaction_type == 'Credit':
                amount = -1 * (order_item.product.parts_price * cost_type.percentage / 100) * order_item.quantity
            else:
                amount = (order_item.product.parts_price * cost_type.percentage / 100) * order_item.quantity

            if not isinstance(currency_code, CurrencyCode):
                raise ValueError("currency_code must be an instance of CurrencyCode.")

            orderitemcost.objects.update_or_create(
                orderitem=order_item,
                cost_type=cost_type,
                defaults={
                    'amount': amount,
                    'currency_code': currency_code
                }
            )

    def apply_order_costs(self, order):
        item_level_costs = Costtypes.objects.filter(is_order_level_cost=True)

        order_items = orderitems.objects.filter(order=order)

        total_cost = sum(item.product.parts_price * item.quantity for item in order_items)

        for cost_type in item_level_costs:
            if cost_type.transaction_type == 'Credit':
                amount = -1 * (total_cost * cost_type.percentage / 100)
            else:
                amount = (total_cost * cost_type.percentage / 100)
            currency_code = None
            for order_item in order_items:
                product_cost = Product_cost.objects.filter(product_id=order_item.product).first()
                if product_cost:
                    currency_code = product_cost.product_currency
                    break

            if not currency_code:
                raise ValueError("No currency code found for the products in the order.")

            if not isinstance(currency_code, CurrencyCode):
                raise ValueError("currency_code must be an instance of CurrencyCode.")

            ordercosts.objects.update_or_create(
                order=order,
                cost_type=cost_type,
                defaults={
                    'amount': amount,
                    'currency_code': currency_code
                }
            )


class EmptyCartView(APIView):
    def delete(self, request, format=None):
        user = request.user
        data = request.data

        order_status_new, _ = OrderStatus.objects.get_or_create(order_status='New')

        if user.is_authenticated:
            active_order = orders.objects.filter(
                orderedby=user,
                orderstatus=order_status_new
            ).first()
        else:
            session_key = request.session.session_key
            if not session_key:
                return Response({"error": "Session not found."}, status=status.HTTP_400_BAD_REQUEST)

            active_order = orders.objects.filter(
                session_key=session_key,
                orderstatus=order_status_new
            ).first()

        if not active_order:
            return Response({"error": "No active order found."}, status=status.HTTP_404_NOT_FOUND)
        order_items = orderitems.objects.filter(order=active_order)
        if not order_items.exists():
            return Response({"error": "No items found in the cart."}, status=status.HTTP_404_NOT_FOUND)

        for order_item in order_items:
            product = order_item.product
            inventory = ProductInventory.objects.filter(product=product).first()

            if inventory:
                inventory.instock_count += order_item.quantity
                inventory.items_left = inventory.instock_count
                inventory.save()

            order_item.delete()

        ordercosts.objects.filter(order=active_order).delete()
        active_order.delete()
        return Response({"message": "All cart items deleted successfully."}, status=status.HTTP_200_OK)

#New Cart
class CartItemDetailView(APIView):
    def post(self, request):
        if request.user.is_authenticated:
            carouselserializer = Carouselpostserializer(data=request.data)
            user = request.user

            if carouselserializer.is_valid():
                try:
                    # Fetch the related carousel, brand, category, and products
                    c = Carousel.objects.get(carousel_code=carouselserializer.validated_data['carousel_code'])
                    b = Brand.objects.get(brand_manufacturer=c.carousel_brand.brand_manufacturer)
                    ct = Category.objects.get(category_name=c.carousel_category)
                    p = Product.objects.filter(parts_brand=b, parts_category=ct)

                    # Initialize the cart and order items
                    crt = orders.objects.get(orderedby=user)
                    order_items = orderitems.objects.filter(order_id=crt.ID)

                    # Loop through the products and find matching ones in the order
                    for i in p:
                        if order_items:
                            for j in order_items:
                                if i == j.product:
                                    u = User.objects.get(id=user.id)
                                    user_coupon = Usercoupon.objects.filter(user=u, product=j.product.id)

                                    # If no user coupon exists for the product, create it
                                    if not user_coupon.exists():
                                        Usercoupon.objects.create(user=u, product=j.product)

                                    # Add the coupon code to the user's product coupon
                                    o = Usercoupon.objects.get(user=u, product=j.product.id)
                                    o.code.add(c)
                                    return Response(data='Added successfully', status=status.HTTP_201_CREATED)

                        else:
                            return Response(data='Cart not found', status=status.HTTP_404_NOT_FOUND)

                    # If no matching product was found in the user's order
                    return Response(data='Product not found in cart', status=status.HTTP_404_NOT_FOUND)

                except Carousel.DoesNotExist:
                    return Response(data="Carousel code not found", status=status.HTTP_404_NOT_FOUND)
                except Brand.DoesNotExist:
                    return Response(data="Brand not found", status=status.HTTP_404_NOT_FOUND)
                except Category.DoesNotExist:
                    return Response(data="Category not found", status=status.HTTP_404_NOT_FOUND)
                except orders.DoesNotExist:
                    return Response(data="Order not found for user", status=status.HTTP_404_NOT_FOUND)

            else:
                return Response(carouselserializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(data="User not authenticated", status=status.HTTP_401_UNAUTHORIZED)

    def get(self, request, format=None):
        user = request.user
        try:
            # Get or create new order status
            order_status_new, created = OrderStatus.objects.get_or_create(order_status='New')

            if user.is_authenticated:
                active_order = orders.objects.filter(orderedby=user, orderstatus=order_status_new).first()
            else:
                session_key = request.session.session_key
                if not session_key:
                    return Response({"error": "Session not found."}, status=status.HTTP_400_BAD_REQUEST)
                active_order = orders.objects.filter(session_key=session_key, orderstatus=order_status_new).first()

            if not active_order:
                return Response({"error": "No active order found."}, status=status.HTTP_404_NOT_FOUND)

            # Retrieve order items
            order_items = orderitems.objects.filter(order=active_order)
            serializer = OrderItemSerializer(order_items, many=True, context={'request': request})

            # Get user coupons
            u = Usercoupon.objects.filter(user=request.user.id)

            product = []
            final = {}
            couponprice = []

            for item in serializer.data:
                data = {
                    'product_id': item['product']['id'],
                    'parts_name': item['product']['parts_name'],
                    'parts_price': item['product']['parts_price'] * item['quantity'],
                    'main_image': item['product']['main_image'],
                    'parts_no': item['product']['parts_no'],
                    'parts_offer': item['product']['parts_offer'],
                    'product_full_detail': item['product']['product_full_detail'],
                    'quantity': item['quantity'],
                    'delete': item['delete']
                }

                # Default final price without coupons
                data['final_price'] = round(item['product']['final_price'] * item['quantity'], 2)

                # Check if product has coupons
                for i in u:
                    productcoupon = i.product.id
                    if productcoupon == item['product']['id']:
                        couponcode = []
                        couponprice = []
                        for j in i.code.all():
                            couponcode.append(j.carousel_code)
                            couponprice.append(j.carousel_offer)

                        f = item['product']['final_price'] * item['quantity']
                        data['final_price'] = f - f * (sum(couponprice) / 100)
                        data['couponcode'] = couponcode
                        break  # No need to check other coupons for this product

                product.append(data)

            final['order_items'] = product

            total_price = []
            actual_price = []
            for i in product:
                total_price.append(i["final_price"])
                actual_price.append(i['parts_price'])

            tot = sum(total_price)
            act = sum(actual_price)
            saving_price = act - tot + sum(couponprice)

            final['total_price'] = round(tot, 2)
            final['saving_price'] = round(saving_price, 2)

            return Response({'data': final}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CartDeleteView(APIView):
    def delete(self, request, item_id, format=None):
        order_item = orderitems.objects.filter(ID=item_id).first()

        if order_item is None:
            return Response({"error": "Order item not found."}, status=status.HTTP_404_NOT_FOUND)

        product = order_item.product
        product_inventory = ProductInventory.objects.filter(product=product).first()

        if product_inventory is None:
            return Response({"error": "Product inventory not found."}, status=status.HTTP_404_NOT_FOUND)

        product_inventory.instock_count += order_item.quantity
        product_inventory.save()

        orderitemcost.objects.filter(orderitem=order_item).delete()

        order_item.delete()

        return Response({"message": "cart item deleted successfully"},status=status.HTTP_200_OK)

class OrderSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        order_status_new, _ = OrderStatus.objects.get_or_create(order_status='New')

        active_order = orders.objects.filter(orderedby=user, orderstatus=order_status_new).first()
        if not active_order:
            return Response({"error": "No active order found."}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve the latest billing address
        billing_address = BillingAddress.objects.filter(user=user).order_by('-id').first()
        if not billing_address:
            return Response({"error": "No billing address found."}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve the selected seller for the user
        try:
            selected_seller = SelectedSeller.objects.get(user=user)
            seller_preferences = selected_seller.seller
        except SelectedSeller.DoesNotExist:
            return Response({"error": "No seller selected."}, status=status.HTTP_404_NOT_FOUND)

        order_items = orderitems.objects.filter(order=active_order)
        order_item_serializer = OrderItemSerializer(order_items, many=True, context={'request': request})

        order_costs = ordercosts.objects.filter(order=active_order)
        shipping_cost, packaging_cost, tax = self.calculate_costs(order_costs)

        user_coupons = Usercoupon.objects.filter(user=user.id)
        product_data = self.process_order_items(order_item_serializer.data, user_coupons)

        total_price = sum(item['total_price'] for item in product_data)
        ordercost_price = total_price + shipping_cost + packaging_cost + tax

        # Serialize billing address and seller information
        billing_serializer = Billaddressserializer(billing_address)
        seller_serializer = SellerSerializer(seller_preferences)

        # Prepare the response data
        response_data = {
            'billing_address': billing_serializer.data,
            'seller': seller_serializer.data,
            'order_items': product_data,
            'total_price': total_price,
            'shipping_cost': shipping_cost,
            'packaging_cost': packaging_cost,
            'tax': tax,
            'final_price': ordercost_price
        }

        return Response({'data': response_data}, status=status.HTTP_200_OK)

    def calculate_costs(self, order_costs):
        # Calculate individual costs
        shipping_cost = sum(cost.amount for cost in order_costs if cost.cost_type.name == 'Shipping Cost')
        packaging_cost = sum(cost.amount for cost in order_costs if cost.cost_type.name == 'Packaging Cost')
        central_tax = sum(cost.amount for cost in order_costs if cost.cost_type.name == 'Central Tax')
        state_tax = sum(cost.amount for cost in order_costs if cost.cost_type.name == 'State Tax')

        return shipping_cost, packaging_cost, state_tax + central_tax  # Return numeric values

    def process_order_items(self, order_items, user_coupons):
        product_data = []
        for item in order_items:
            product = item.get('product', {})
            coupon_discount = self.calculate_coupon_discount(product, user_coupons)
            quantity = item.get('quantity', 1)
            total_price = quantity * product.get('final_price', 0)
            product_data.append({
                'parts_name': product.get('parts_name', 'N/A'),
                'parts_price': product.get('parts_price', 0),
                'main_image': product.get('main_image', ''),
                'parts_no': product.get('parts_no', 'N/A'),
                'parts_offer': product.get('parts_offer', 'N/A'),
                'product_full_detail': product.get('product_full_detail', 'N/A'),
                'final_price': product.get('final_price', 0),
                'quantity': quantity,
                'total_price': round(total_price - (total_price * (coupon_discount / 100)), 2)
            })
        return product_data

    def calculate_coupon_discount(self, product, user_coupons):
        coupon_price = 0
        for coupon in user_coupons:
            if product.get('id', 0) == coupon.product.id:
                for code in coupon.code.all():
                    coupon_price += code.carousel_offer
        return coupon_price

class PlaceOrder(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        user = request.user

        # Fetch the latest order for the user, or adjust as needed
        order = orders.objects.filter(orderedby=user).latest('orderedon')  # Or use your criteria for selecting an order

        if not order:
            return Response({"error": "No orders found for the user."}, status=status.HTTP_404_NOT_FOUND)

        # Set order status to "InProgress"
        order_status_placed, created = OrderStatus.objects.get_or_create(order_status="InProgress")
        order.orderstatus = order_status_placed
        order.save()

        quotation_id = uuid.uuid4().hex.upper()

        url = ("https://asset.cloudinary.com/dfwjcn8kh/91841c30f2fe77d943b7d6983f4210d5")
        # pdf_buffer = self.generate_quotation_pdf(
        #     user=user,
        #     order=order,
        #     total_cost=total_cost,
        #     quotation_id=quotation_id
        # )

        def send_email_seller(quotation_id, url):
            html_content = f"""
                        <html>
                        <body>
                            <h4>Dear Sir/Madam,</h4>
                            <p>You have received an order <strong>{quotation_id}</strong>.</p>
                            <p>Please find the quotation attachment.</p>
                            <a href="{url}">Click here</a>
                        </body>
                        </html>
                        """

            email = EmailMessage(
                subject=f'Order Received - {quotation_id}',
                body=html_content,
                from_email=settings.EMAIL_HOST_USER,
                to=['dhanushpathiprakash0511@gmail.com'],
            )
            email.content_subtype = "html"
            try:
                email.send()
                print("Email sent successfully")
            except Exception as e:
                print(f"Failed to send email: {str(e)}")

        send_email_seller(quotation_id, url)

        return Response({
            "message": "Order placed successfully.",
            "quotation_no": quotation_id,
            "quotation_url": url
        }, status=status.HTTP_200_OK)


    def calculate_order_item_cost(self, orderitem):
        # Retrieve all cost entries for the given order item
        item_costs = orderitemcost.objects.filter(orderitem=orderitem)

        total_item_cost = 0
        for cost in item_costs:
            if (order_item.product.parts_price * cost_type.percentage / 100) == 'D':
                total_item_cost += cost.amount
            elif cost.cost_type.transaction_type == 'C':  # Credit
                total_item_cost -= cost.amount

        return total_item_cost

    def calculate_order_item_cost(self, orderitem):
        # Retrieve all cost entries for the given order item
        item_costs = orderitemcost.objects.filter(orderitem=orderitem)

        total_item_cost = 0
        product_price = orderitem.product.parts_price  # Base price of the product

        for cost in item_costs:
            cost_type = cost.cost_type

            if cost_type.percentage > 0:
                percentage_amount = (cost_type.percentage / 100) * product_price

                # Determine if the percentage amount is a debit (D) or credit (C)
                if cost_type.transaction_type == 'D':  # Debit
                    total_item_cost += percentage_amount
                elif cost_type.transaction_type == 'C':  # Credit
                    total_item_cost -= percentage_amount
            else:
                if cost_type.transaction_type == 'D':  # Debit
                    total_item_cost += cost.amount
                elif cost_type.transaction_type == 'C':  # Credit
                    total_item_cost -= cost.amount

        return total_item_cost

    def calculate_order_level_cost(self, order):
        # Retrieve all cost entries for the given order
        order_costs = ordercosts.objects.filter(order=order)

        total_order_cost = 0
        for cost in order_costs:
            cost_type = cost.cost_type

            if cost_type.percentage > 0:
                percentage_amount = (cost_type.percentage / 100) * cost.amount
                if cost_type.transaction_type == 'D':
                    total_order_cost += percentage_amount
                elif cost_type.transaction_type == 'C':
                    total_order_cost -= percentage_amount
            else:
                # Apply fixed amount cost
                if cost_type.transaction_type == 'D':
                    total_order_cost += cost.amount
                elif cost_type.transaction_type == 'C':  # Credit
                    total_order_cost -= cost.amount

        return total_order_cost

    def apply_percentage_based_costs(self, order, base_amount):
        # Retrieve all percentage-based costs (e.g., tax, discounts)
        percentage_costs = ordercosts.objects.filter(order=order, cost_type__percentage__gt=0)

        total_percentage_cost = 0
        for cost in percentage_costs:
            percentage_amount = (cost.cost_type.percentage / 100) * base_amount
            if cost.cost_type.transaction_type == 'D':  # Debit
                total_percentage_cost += percentage_amount
            elif cost.cost_type.transaction_type == 'C':  # Credit
                total_percentage_cost -= percentage_amount

        return total_percentage_cost

    def calculate_final_order_cost(self, order):
        total_item_cost = sum(self.calculate_order_item_cost(item) for item in order.orderitems_set.all())

        total_order_cost = self.calculate_order_level_cost(order)

        base_cost = total_item_cost + total_order_cost

        percentage_cost = self.apply_percentage_based_costs(order, base_cost)

        final_cost = base_cost + percentage_cost

        return final_cost
    # def generate_quotation_pdf(self, user, order, total_cost, quotation_id):
    #     # Create a PDF buffer
    #     buffer = BytesIO()
    #
    #     # Create a PDF with ReportLab
    #     p = canvas.Canvas(buffer, pagesize=A4)
    #     p.drawString(100, 800, f"Quotation ID: {quotation_id}")
    #     p.drawString(100, 780, f"User: {user.email}")
    #     p.drawString(100, 760, f"Order ID: {order.id}")
    #     p.drawString(100, 740, f"Date: {timezone.now().strftime('%Y-%m-%d')}")
    #
    #     # Billing and shipping address
    #
    #     # Total cost
    #     p.drawString(100, 640, f"Total Order Cost: ${total_cost:.2f}")
    #
    #     # Additional cost details (if you want to show item breakdown)
    #
    #     p.showPage()
    #     p.save()
    #
    #     buffer.seek(0)
    #     return buffer
    #
    # def send_quotation_email(self, email, pdf_buffer, quotation_id):
    #     subject = f"Your Quotation (ID: {quotation_id})"
    #     body = "Please find attached the quotation for your recent order."
    #
    #     email_message = EmailMessage(
    #         subject=subject,
    #         body=body,
    #         to=[email]
    #     )
    #     email_message.attach(f"quotation_{quotation_id}.pdf", pdf_buffer.getvalue(), "application/pdf")
    #     email_message.send()


class MyOrdersView(APIView):
    def get(self, request, format=None):
        user = request.user
        # Fetch all orders for the user
        all_orders = orders.objects.filter(orderedby=user)

        if not all_orders.exists():
            return Response({"error": "No orders found for this user."}, status=status.HTTP_404_NOT_FOUND)

        order_data_list = []
        total_parts_price = 0

        # Iterate through all orders
        for order in all_orders:
            order_items = orderitems.objects.filter(order=order)
            serializer = OrderItemSerializer(order_items, many=True, context={'request': request})

            order_data = {
                'order_id': order.ID,
                'order_date': order.orderedon,
                'order_status': order.orderstatus.order_status,
                'products': []
            }

            order_total_price = 0

            for item in serializer.data:
                product_data = {
                    'product_id': item['product']['id'],
                    'parts_name': item['product']['parts_name'],
                    'parts_price': item['product']['parts_price'] * item['quantity'],
                    'quantity': item['quantity']
                }

                order_total_price += product_data['parts_price']
                order_data['products'].append(product_data)

            order_data['total_price'] = order_total_price
            order_data_list.append(order_data)
            total_parts_price += order_total_price

        response_data = {
            'orders': order_data_list,
        }

        return Response({'data': response_data}, status=status.HTTP_200_OK)


class BtwocView(APIView):
    def get(self, request):
        b_2_c = Product_btc_links.objects.all()
        serializer = ProductBTCSerializer(b_2_c, many=True, context={'request':request})
        return Response({'data':serializer.data}, status=status.HTTP_200_OK)

class MerchandisingContentView(APIView):
    def get(self, request):
        merchant = MerchandisingContent.objects.all()
        serializer = MerchantSerializer(merchant, many=True, context={'request':request})
        return Response({'data':serializer.data}, status=status.HTTP_200_OK)


#attribute API

# class ProductattributeView(APIView):
#
#     def get(self, request):
#         # Fetch data from ProductAttribute (Django ORM)
#         pro = ProductAttribute.objects.all()
#
#         for i in pro:
#             product_code = i.productcode.product_code
#             attribute_code = i.attributecode.attributecode
#             tab_code = i.tabcode.tabcode
#             section_code = i.sectioncode.sectioncode
#
#             # Fetch the product from MongoDB by product code
#             product = mongodb.Product.objects(Productcode=product_code).first()
#
#             if not product:
#                 # If product does not exist, create a new one
#                 attribute = mongodb.Attribute(Attributecode=attribute_code)
#                 section = mongodb.Section(Sectioncode=section_code, Attributes=[attribute])
#                 tab = mongodb.Tab(Tabcode=tab_code, Sections=[section])
#                 product = mongodb.Product(Productcode=product_code, Tabs=[tab])
#             else:
#                 # If product exists, check for tab
#                 tab = next((t for t in product.Tabs if t.Tabcode == tab_code), None)
#
#                 if not tab:
#                     # If tab does not exist, create and add a new tab
#                     attribute = mongodb.Attribute(Attributecode=attribute_code)
#                     section = mongodb.Section(Sectioncode=section_code, Attributes=[attribute])
#                     tab = mongodb.Tab(Tabcode=tab_code, Sections=[section])
#                     product.Tabs.append(tab)
#                 else:
#                     # If tab exists, check for section
#                     section = next((s for s in tab.Sections if s.Sectioncode == section_code), None)
#
#                     if not section:
#                         # If section does not exist, create and add a new section
#                         attribute = mongodb.Attribute(Attributecode=attribute_code)
#                         section = mongodb.Section(Sectioncode=section_code, Attributes=[attribute])
#                         tab.Sections.append(section)
#                     else:
#                         # If section exists, check for attribute
#                         attribute = next((a for a in section.Attributes if a.Attributecode == attribute_code), None)
#
#                         if not attribute:
#                             # If attribute does not exist, add it to the section
#                             attribute = mongodb.Attribute(Attributecode=attribute_code)
#                             section.Attributes.append(attribute)
#
#             # Save the updated product to MongoDB
#             product.save()
#         data=mongodb.Product.objects.all()
#         print(data)
#         return Response(data={"message": "Products and attributes successfully updated in MongoDB"}, status=200)
#



class ProductattributeView(APIView):
    def saveproductmongodb(self):
        pro = ProductAttribute.objects.all()
        for i in pro:
            product_code = i.productcode.product_code
            attribute_code = i.attributecode.attributecode
            tab_code = i.tabcode.tabcode
            section_code = i.sectioncode.sectioncode

            # Fetch the product from MongoDB by product code
            product = mongodb.Product.objects(Productcode=product_code).first()

            if not product:
                # If product does not exist, create a new one
                attribute = mongodb.Attribute(Attributecode=attribute_code)
                section = mongodb.Section(Sectioncode=section_code, Attributes=[attribute])
                tab = mongodb.Tab(Tabcode=tab_code, Sections=[section])
                product = mongodb.Product(Productcode=product_code, Tabs=[tab])
            else:
                # If product exists, check for tab
                tab = next((t for t in product.Tabs if t.Tabcode == tab_code), None)

                if not tab:
                    # If tab does not exist, create and add a new tab
                    attribute = mongodb.Attribute(Attributecode=attribute_code)
                    section = mongodb.Section(Sectioncode=section_code, Attributes=[attribute])
                    tab = mongodb.Tab(Tabcode=tab_code, Sections=[section])
                    product.Tabs.append(tab)
                else:
                    # If tab exists, check for section
                    section = next((s for s in tab.Sections if s.Sectioncode == section_code), None)

                    if not section:
                        # If section does not exist, create and add a new section
                        attribute = mongodb.Attribute(Attributecode=attribute_code)
                        section = mongodb.Section(Sectioncode=section_code, Attributes=[attribute])
                        tab.Sections.append(section)
                    else:
                        # If section exists, check for attribute
                        attribute = next((a for a in section.Attributes if a.Attributecode == attribute_code), None)

                        if not attribute:
                            # If attribute does not exist, add it to the section
                            attribute = mongodb.Attribute(Attributecode=attribute_code)
                            section.Attributes.append(attribute)

            # Save the updated product to MongoDB
            product.save()

    def get(self, request):
        self.saveproductmongodb()
        # Fetch data from MongoDB
        products = mongodb.Product.objects()

        # List to store the serialized products
        product_list = []

        # Loop through the MongoDB objects and serialize them
        for product in products:
            product_data = {
                "Productcode": product.Productcode,
                "Tabs": []
            }

            # Loop through tabs
            for tab in product.Tabs:
                tab_data = {
                    "Tabcode": tab.Tabcode,
                    "Sections": []
                }

                # Loop through sections
                for section in tab.Sections:
                    section_data = {
                        "Sectioncode": section.Sectioncode,
                        "Attributes": []
                    }

                    # Loop through attributes
                    for attribute in section.Attributes:
                        attribute_data = {
                            "Attributecode": attribute.Attributecode
                        }
                        section_data["Attributes"].append(attribute_data)

                    tab_data["Sections"].append(section_data)

                product_data["Tabs"].append(tab_data)

            product_list.append(product_data)

        # Return the serialized MongoDB data as an API response
        return Response(data={"products": product_list}, status=200)


    def post(self, request):
        productcode= request.data.get('productcode')
        p=Product.objects.get(product_code=productcode)
        a=ProductAttribute.objects.filter(productcode=p.id)
        p=[]
        for i in a:
            data = {}
            data['Attributename']= i.attributecode.name
            try:
                v = ProductAttributeValue.objects.get(product_attribute_id=i.product_attribute_id)
                print(v.value, v.choice_value)
                if v.value is not None:
                    data['attributevalue'] = v.value
                elif v.choice_value is not None:
                    data['attributevalue'] = v.choice_value
            except:
                data['attributevalue'] = None
            p.append(data)

        return Response(data=p, status=status.HTTP_200_OK)



class CategoryTreeView(APIView):

    def savecategorymongodb(self):
        # Step 1: Save root categories (categories with no parent)
        root_categories = Category.objects.filter(parent__isnull=True)
        for category in root_categories:
            self.save_category_and_children(category)

        # Step 2: Add child categories (categories with a parent)
        child_categories = Category.objects.filter(parent__isnull=False)
        for category in child_categories:
            self.add_category_to_parent(category)

    def save_category_and_children(self, category):
        """
        Recursively build and save a category tree, starting from a root category.
        """
        category_name = category.category_name
        category_code = category.code

        # Fetch or create the root category in MongoDB
        root_category = mongodb.Root.objects(name=category_name).first()
        if not root_category:
            root_category = mongodb.Root(name=category_name, children=[])

        # Build and append the category tree
        root_category_node = self.build_category_tree(category)
        if not any(child.code == category_code for child in root_category.children):
            root_category.children.append(root_category_node)

        root_category.save()

    def build_category_tree(self, category):
        """
        Recursively build a category tree by processing parent and children relationships.
        """
        # Create the current category node
        category_node = mongodb.Categorys(
            name=category.category_name,
            code=category.code if category.code else "Refer Code",
            children=[]
        )

        # Fetch the children of the current category from the PostgreSQL model
        child_categories = category.children.all()

        # Recursively build the tree for each child
        for child in child_categories:
            child_node = self.build_category_tree(child)
            if not any(sub_child.code == child.code for sub_child in category_node.children):
                category_node.children.append(child_node)

        return category_node

    def add_category_to_parent(self, category):
        """
        Find the parent of the current category and add it as a child.
        """
        parent = category.parent

        # Find the parent category in MongoDB (inside Root's children)
        parent_category = None
        root_category = mongodb.Root.objects(children__name=parent.category_name).first()

        if root_category:
            # Find the parent category inside the root's children
            for child in root_category.children:
                if child.name == parent.category_name:
                    parent_category = child
                    break

        if parent_category:
            # Create a new node for the current category
            category_node = mongodb.Categorys(
                name=category.category_name,
                code=category.code if category.code else "Refer Code",
                children=[]
            )

            # Add the current category as a child to the parent category if not already present
            if not any(sub_child.code == category.code for sub_child in parent_category.children):
                parent_category.children.append(category_node)
                root_category.save()

    def get(self, request):
        self.savecategorymongodb()

        # Fetch data from MongoDB
        categories = mongodb.Root.objects()
        # List to store the serialized categories
        category_list = []

        # Loop through the MongoDB objects and serialize them in the required format
        for root in categories:
            # root_data = {
            #     "name": root.name,
            #     "children": []
            # }

            # Loop through root children
            for child in root.children:
                child_data = self.serialize_category(child)
                # root_data["children"].append(child_data)
                category_list.append(child_data)

        # Return the serialized MongoDB data as an API response
        return Response(data={"name": "ROOT", "children": category_list}, status=200)

    def serialize_category(self, category):
        """
        Serialize a category object into the required JSON format.
        """
        category_data = {
            "name": category.name,
            "code": category.code if category.code else "Refer Code",
            "children": []
        }

        for sub_child in category.children:
            sub_child_data = self.serialize_category(sub_child)
            category_data["children"].append(sub_child_data)

        return category_data

client = MongoClient('mongodb+srv://admin:kWwviQLhdkbL5MQE@admindash.zvg2l7k.mongodb.net/?retryWrites=true&w=majority')
db = client['partscraft']

class ProductoneattributeView(APIView):
    def get(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')

        try:
            product_code = Product.objects.get(id=product_id)
            code = product_code.product_code

            product = db['product'].find_one({"Productcode": "PR003"})

            if product:
                if "_id" in product:
                    product["_id"] = str(product["_id"])

                # Return the full product details including Productcode
                return Response(product, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        except Product.DoesNotExist:
            return Response({"error": "Product code not found in Django"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)