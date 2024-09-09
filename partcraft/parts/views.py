import json
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
from account.emails import send_confirmation_email

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
        vehicleserializer = VehicleoneSerializer(data=request.data)
        if vehicleserializer.is_valid():
            try:
                vehicle = Vehicle.objects.filter(
                    vehicle_name=vehicleserializer.validated_data['vehicle_name'],
                    vehicle_variant=vehicleserializer.validated_data['vehicle_variant'],
                    vehicle_model=vehicleserializer.validated_data['vehicle_model'],
                    vehicle_year=vehicleserializer.validated_data['vehicle_year'],
                )
                v = []
                for i in vehicle:
                    this_part = Product.objects.filter(this_parts_fits=i)
                    productserializer = ProductSerializer(this_part, context={'request': request}, many=True)
                    v.append(productserializer.data)

                lastdata = adddict(productserializer)

                vehicle_data = VehicleoneSerializer(vehicle, many=True, context={'request': request}).data

                response = Response({'vehicle': vehicleserializer.data, 'parts': lastdata}, status=status.HTTP_200_OK)
                response.set_cookie('vehicle', json.dumps(vehicle_data))
                print("cookies set response:")
                for key, value in response.cookies.items():
                    print(f"{key}, {value}")
                return response
            except Vehicle.DoesNotExist:
                return Response({'data': 'Vehicle not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(vehicleserializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        queryset = Vehicle.objects.all()
        serializer = VehicleSerializer(queryset, many=True, context={'request': request})
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
        serializer = VehicleSerializer(vehicles, many=True, context={'request': request})
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)


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

        if Wishlist.objects.filter(wishlist_name=request.user, wishlist_product=product).exists():
            return Response({"error": "Product already exists in the wishlist."}, status=status.HTTP_400_BAD_REQUEST)

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

        categorized_data = defaultdict(list)
        move_to_cart_url = request.build_absolute_uri(reverse('move-to-cart'))
        delete_all_wishlist_url = request.build_absolute_uri(reverse('delete-all-wishlistitems'))

        for wishlist in wishlists:
            wishlist_data = WishallSerializer(wishlist, context={'request': request}).data
            brand = wishlist_data['wishlist_name']
            product_info = {
                'product_id': wishlist_data['wishlist_product']['id'],
                'wishlist_product': f"{wishlist_data['wishlist_product']['parts_brand']['brand_name']} {wishlist_data['wishlist_product']['parts_category']['category_name']} {wishlist_data['wishlist_product']['subcategory_name']}",
                'parts_no': wishlist_data['parts_no'],
                'brand_logo': wishlist_data['brand_logo'],
                'parts_type': wishlist_data['parts_type'],
                'parts_price': wishlist_data['parts_price'],
                'parts_offer': wishlist_data['parts_offer'],
                'final_price': wishlist_data['final_price'],
                'main_image': wishlist_data['main_image'],
                'url': wishlist_data['wishlist_product']['url'],
                'addtocart': wishlist_data['addtocart'],
                'Wishlistdel': wishlist_data['wishlist_delete'],
            }

            categorized_data[brand].append(product_info)
        categorized_data = dict(categorized_data)
        response = Response({
            'Product': categorized_data,
            'move_to_cart': move_to_cart_url,
            'delete_all_wishlist': delete_all_wishlist_url,
             },
            status=status.HTTP_200_OK)
        if bool(categorized_data) is not False:
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
            print(cart_items)
            print("cart data:", cart_data)
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

            self.update_cart_cookie(request, response, pk, quantity)
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


class BuyNowAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        product = get_object_or_404(Product, pk=pk)
        serializer = Buynowserilizers(data=request.data, context={'request': request})
        if serializer.is_valid():
            result = serializer.save()
            response_data = {
                "message": "Shipping Addresses saved successfully.",
                "shipping_address": Shippingaddressserializer(result["shipping_address"]).data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BillingDealerView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        user = request.user
        shipping_address = ShippingAddress.objects.filter(user=user).first()
        if not shipping_address:
            return Response({"message": "No addresses found for the user."}, status=status.HTTP_404_NOT_FOUND)
        shipping_city = shipping_address.city
        dealer_address = DealerAddress.objects.filter(city=shipping_city).distinct()
        serializer = DealerAddressSerializer(dealer_address, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user = request.user
        shipping_address = ShippingAddress.objects.filter(user=user).first()

        if not user.is_authenticated:
            return Response({"message": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

        if not shipping_address:
            return Response({"message": "No shipping address found for the user."}, status=status.HTTP_404_NOT_FOUND)

        shipping_city = shipping_address.city

        dealer_address = DealerAddress.objects.filter(city=shipping_city).first()

        if not dealer_address:
            return Response({"message": "No dealers found in the shipping city."}, status=status.HTTP_404_NOT_FOUND)

        billing_address_data = {
            'user': user.id,
            'billing_name': dealer_address.name,
            'gst_number': dealer_address.gst_number,
            'email': dealer_address.email,
            'billing_address': dealer_address.address,
        }

        serializer = Billaddressserializer(data=billing_address_data)

        if serializer.is_valid():
            billing_address = serializer.save()
            return Response({
                "message": "Billing address saved successfully.",
                "billing_address": serializer.data
            }, status=status.HTTP_201_CREATED)

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

        # def parse_cookie_data():
        #     items = []
        #     for key, value in request.COOKIES.items():
        #         if key.startswith('cart_product_'):
        #             try:
        #                 product_id = int(key.split('_')[2])
        #                 quantity = int(value)
        #                 items.append({"product_id": product_id, "quantity": quantity})
        #             except (IndexError, ValueError):
        #                 continue
        #     return items

        def parse_url_parameter_data(products_data):
            items = []
            for product_data in products_data:
                try:
                    product_id, quantity = map(int, product_data.split(','))
                    items.append({"product_id": product_id, "quantity": quantity})
                except ValueError:
                    continue
            return items

        order_item = self.get_cart_items_from_cookie(request)
        order_data, _, _ = self.process_cart_data(order_item)
        order_items.extend(order_data)
        if products_data:
            order_items.extend(parse_url_parameter_data(products_data))


        if not order_items:
            return Response({"detail": "No products."}, status=status.HTTP_400_BAD_REQUEST)

        detailed_order_items = []

        for item in order_items:
            try:
                product = Product.objects.get(id=item["product"])
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

        for item in detailed_order_items:
            order_item = self.get_cart_items_from_cookie(request)
            order_data, _, _ = self.process_cart_data(order_item)
        datas = {"preferred_billing_address": Shippingaddressserializer(
                preferred_shipping_address).data if preferred_shipping_address else None,
            "order_items": detailed_order_items,
            "grand_total": grand_total}
        response = Response(
            datas, status=status.HTTP_200_OK
        )
        response.set_cookie('order_summary', json.dumps(datas))
        return response


class OrderAPIView(BaseCartView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user_profile = Profile.objects.filter(user=user).first()
        if not user_profile:
            return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

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
    def get(self, request):
        feedbacks = Feedback.objects.all()
        serializer = FeedbackSerializer(feedbacks, many=True)
        return Response({'data':serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            p = request.data
            f = Feedback.objects.all()
            l = []
            for i in f:
                l.append(i.email)
            if p['email'] in l:
                return Response({'data': 'Email already registered.'}, status=status.HTTP_208_ALREADY_REPORTED)
            serializer.save()
            return Response({'data':'Feedback has successfully created'}, status=status.HTTP_201_CREATED)
        return Response({'data':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class DealerAddressView(APIView):
    def get(self, request):
        dealer_addrress = DealerAddress.objects.all()
        serializer = DealerAddressSerializer(dealer_addrress, many=True)
        return Response({'data':serializer.data}, status=status.HTTP_200_OK)
