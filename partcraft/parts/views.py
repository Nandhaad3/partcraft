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
from rest_framework.parsers import MultiPartParser, FormParser
from account.emails import send_confirmation_email
from django.contrib.auth import login
from account.models import User
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
from django.utils import timezone
from django.core.mail import EmailMessage

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
        data['addtocart'] = i['addtocart']
        data['product_fit'] = i['product_fit']
        last_data.append(data)
    return last_data


class CustomPagination(PageNumberPagination):
    page_size = 3
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
        return Response({'data': category_serializer.data, 'parts': lastdata}, status=status.HTTP_200_OK)


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
            return Response({'data': 'Product Not Found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True)
        brand_serializer = BrandSerializer(brand, context={'request': request})
        lastdata = adddict(serializer)
        return Response({'data': brand_serializer.data, 'parts': lastdata}, status=status.HTTP_200_OK)


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
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        existing_wishlist = Wishlist.objects.filter(wishlist_name=self.request.user, wishlist_product=product).exists()
        if existing_wishlist:
            return Response({"message": "Product is already in the wishlist."}, status=status.HTTP_400_BAD_REQUEST)

        data = {
            'wishlist_name': self.request.user,
            'wishlist_product': product
        }
        s = self.get_serializer(data=data)
        self.perform_create(s)

        headers = self.get_success_headers(serializer)
        return Response({'message': 'Wishlist created successfully'}, status=status.HTTP_201_CREATED, headers=headers)

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
            return Response({'Message': 'No Wishlist '}, status=status.HTTP_400_BAD_REQUEST)


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
        return Response({'message': 'Item removed from wishlist successfully.'}, status=status.HTTP_204_NO_CONTENT)


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

    def delete(self, request):
        carousel_serializer = Carouselpostserializer(data=request.data)

        if carousel_serializer.is_valid():
            carousel = get_object_or_404(Carousel, carousel_code=carousel_serializer.validated_data['carousel_code'])
            brand = get_object_or_404(Brand, brand_name=carousel.carousel_brand)
            category = get_object_or_404(Category, category_name=carousel.carousel_category)
            products = Product.objects.filter(parts_brand=brand, parts_category=category)
            response_data, status_code = self._remove_carousel_from_products(carousel, products, request,user=request.user)
            if isinstance(response_data, dict):
                return Response(response_data, status=status_code)
            return response_data
        else:
            return Response(carousel_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartItemsCreateView(BaseCartView):

    def post(self, request, pk):
        # Retrieve the product by primary key
        product = get_object_or_404(Product, pk=pk)
        # Get the quantity from the request, default to 1 if not provided
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

        # user = request.user
        # user_preferences, created = preferences.objects.update_or_create(
        #     user=user, defaults={'selected_seller': seller}
        # )

        serializer = SellerSerializer(seller, context={'request': request})
        return Response({
            "message": "Seller selected successfully.",
            "selected_seller": serializer.data
        }, status=status.HTTP_200_OK)


class PreferencesView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        prefer = preferences.objects.all()
        print(prefer)
        serializer = PreferencesSerializer(prefer, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        u=User.objects.get(email=request.user)
        print(u.id)
        serializer = PreferencesSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'data': 'Preferences has successfully created'}, status=status.HTTP_201_CREATED)
        return Response({'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



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
        product_id = data.get('product_id')

        product = Product.objects.filter(id=product_id).first()
        if not product:
            return Response({"error": f"Product with id {product_id} not found."}, status=status.HTTP_404_NOT_FOUND)

        inventory, _ = ProductInventory.objects.get_or_create(product=product)

        if inventory.instock_count <= inventory.back_order_threshold:
            return Response({"error": "Product out of stock."}, status=status.HTTP_400_BAD_REQUEST)

        if inventory.user_alert_threshold > 0 and data.get('quantity', 1) > inventory.reversed_count:
            return Response({"error": f"Cannot add more than {inventory.maximum_add_by_user} items."},
                            status=status.HTTP_400_BAD_REQUEST)

        order_item, created = orderitems.objects.get_or_create(
            order=active_order,
            product=product,
            defaults={'quantity': 1}
        )

        if not created:
            if order_item.quantity >= inventory.reversed_count:
                return Response(
                    {"error": f"You cannot add more than {inventory.reversed_count} items for this product."},
                    status=status.HTTP_400_BAD_REQUEST)

            order_item.quantity += 1
            order_item.save()

        self.apply_order_item_costs(order_item)
        self.apply_order_costs(active_order)

        inventory.instock_count -= 1
        inventory.items_left = inventory.instock_count
        inventory.save()

        serializer = OrderItemSerializer(order_item, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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


class CartItemDetailView(APIView):
    def get(self, request, format=None):
        user = request.user
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

        order_items = orderitems.objects.filter(order=active_order)
        serializer = OrderItemSerializer(order_items, many=True, context={'request': request})
        product = []
        final={}

        for item in serializer.data:
            data = {}
            data['product_id'] = item['product']['id']
            data['parts_name'] = item['product']['parts_name']
            data['parts_price'] = item['product']['parts_price'] * item['quantity']
            data['main_image'] = item['product']['main_image']
            data['parts_no'] = item['product']['parts_no']
            data['parts_offer'] = item['product']['parts_offer']
            data['product_full_detail'] = item['product']['product_full_detail'],
            data['final_price'] = item['product']['final_price'] * item['quantity']
            data['quantity'] = item['quantity']
            data['detele'] = item['delete']
            product.append(data)
        final['products'] = product
        print(final)
        total_price = []
        actual_price=[]
        for i in product:
            t = i["final_price"] * i["quantity"]
            total_price.append(int(t))
            a = i['parts_price'] * i['quantity']
            actual_price.append(int(a))
        tot=sum(total_price)
        act=sum(actual_price)
        saving_price=act-tot
        final['total_price']=tot
        final['saving_price']=saving_price
        response = Response({'data':final}, status=status.HTTP_200_OK)
        return response

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

        billing_address = BillingAddress.objects.filter(user=user).order_by('-id').first()
        if not billing_address:
            return Response({"error": "No billing address found."}, status=status.HTTP_404_NOT_FOUND)

        seller_preferences = preferences.objects.filter(user=user).first()
        if not seller_preferences or not seller_preferences.selected_seller:
            return Response({"error": "No seller preferences found."}, status=status.HTTP_404_NOT_FOUND)

        order_items = orderitems.objects.filter(order=active_order)
        order_item_serializer = OrderItemSerializer(order_items, many=True, context={'request': request})

        product_data = []

        for item in order_item_serializer.data:
            product = item['product']

            product_data.append({
                'parts_name': product['parts_name'],
                'parts_price': product['parts_price'],
                'main_image': product['main_image'],
                'parts_no': product['parts_no'],
                'parts_offer': product['parts_offer'],
                'product_full_detail': product['product_full_detail'],
                'final_price': product['final_price'],
                'quantity': item['quantity'],
                'total_price': item['quantity'] * product['final_price']
            })
            orderitemcost.objects.all()

        billing_serializer = Billaddressserializer(billing_address)
        seller_serializer = SellerSerializer(seller_preferences.selected_seller)

        response_data = dict(billing_address=billing_serializer.data, seller=seller_serializer.data,
                             products=product_data)

        return Response({'data':response_data}, status=status.HTTP_200_OK)


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

        # You need to provide billing_address_id and shipping_address_id in the request data or handle defaults

        total_cost = self.calculate_final_order_cost(order)

        # pdf_buffer = self.generate_quotation_pdf(
        #     user=user,
        #     order=order,
        #     total_cost=total_cost,
        #     quotation_id=quotation_id
        # )
        #
        # self.send_quotation_email(user.email, pdf_buffer, quotation_id)

        return Response({
            "message": "Order placed successfully.",
            "quotation_id": quotation_id,
            "total_cost": total_cost
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
                # Apply percentage-based cost (like tax or discount on product price)
                percentage_amount = (cost_type.percentage / 100) * product_price

                # Determine if the percentage amount is a debit (D) or credit (C)
                if cost_type.transaction_type == 'D':  # Debit
                    total_item_cost += percentage_amount
                elif cost_type.transaction_type == 'C':  # Credit
                    total_item_cost -= percentage_amount
            else:
                # Apply fixed amount cost
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
            # Calculate percentage amount
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
    def get(self, request, user_id=None, format=None):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            order_status_inprogress = OrderStatus.objects.get(order_status='InProgress')
        except OrderStatus.DoesNotExist:
            return Response({"error": "Order status 'InProgress' not found."}, status=status.HTTP_404_NOT_FOUND)
        active_order = orders.objects.filter(orderedby=user, orderstatus=order_status_inprogress).first()

        if not active_order:
            return Response({"error": "No active 'InProgress' order found."}, status=status.HTTP_404_NOT_FOUND)

        order_items = orderitems.objects.filter(order=active_order)
        serializer = OrderItemSerializer(order_items, many=True, context={'request': request})

        product = []
        final = {}
        total_parts_price = 0

        order_data = {
            'order_id': active_order.id,
            'order_date': active_order.order_date,
            'order_status': active_order.orderstatus.order_status,
        }

        for item in serializer.data:
            data = {}
            data['product_id'] = item['product']['id']
            data['parts_name'] = item['product']['parts_name']
            data['parts_price'] = item['product']['parts_price'] * item[
                'quantity']
            data['quantity'] = item['quantity']

            data['order'] = order_data

            product.append(data)
            total_parts_price += data['parts_price']

        final['products'] = product
        final['total_parts_price'] = total_parts_price

        response = Response({'data': final}, status=status.HTTP_200_OK)
        return response


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