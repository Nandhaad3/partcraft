import json

from django.db.migrations import serializer
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser,IsAuthenticatedOrReadOnly,IsAuthenticated
from rest_framework import status, generics
from rest_framework.exceptions import NotFound
from rest_framework.filters import  SearchFilter,OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view
from django.db.models import F, CharField, Value
from django.db.models.functions import Concat
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *
from collections import defaultdict
from .filter import *
from account.emails import send_confirmation_email
import base64


def adddict(serializer):

    last_data = []
    for i in serializer.data:
        data = {}
        data['id'] = i['id']
        data['parts_type'] = i['parts_type']
        data['main_image']=i['main_image']
        data['brand_image']=i['parts_brand']['brand_image']
        d = (f"{i['parts_brand']['brand_name']} "
                                   f"{i['parts_category']['category_name']} "
                                   f'{i["subcategory_name"]}' 
                                   f"{i['parts_voltage']} "
                                   f"{i['parts_litre']}L ")
        data['parts__Name']=d.replace('NoneL','').strip()
        data['parts_no']=i['parts_no']
        data['parts_offer']=i['parts_offer']
        data['parts_price']=i['parts_price']
        dis=i['parts_price']*(i['parts_offer']/100)
        data['final_price']=i['parts_price']-dis
        data['product_full_detail']=i['url']
        data['is_in_wishlist'] = i['is_in_wishlist']
        if i['is_in_wishlist'] is False:
            data['wishlist']=i['wishlist']
            data['is_in_wishlist'] = i['is_in_wishlist']
        elif i['is_in_wishlist'] is True:
            data['is_in_wishlist']=i['is_in_wishlist']

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
        lastdata=adddict(serializer)
        # offer=offerdata(queryset)
        return Response(lastdata, status=status.HTTP_200_OK)

class partsonedetail(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get_queryset(self):
        product_id=self.kwargs.get('pk')
        queryset=Product.objects.filter(id=product_id)
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
        category_id=self.kwargs.get('pk')
        cat=Category.objects.get(id=category_id)
        quaryset=Product.objects.all().filter(parts_category_id=cat.id)
        return quaryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        category_id = self.kwargs.get('pk')
        cat = Category.objects.get(id=category_id)
        if not queryset.exists():
            return Response({'details':'Product Not Found'},status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True)
        category_serializer = CategorySerializer(cat, context={'request': request})
        lastdata = adddict(serializer)
        return Response({'brand':category_serializer.data,'parts':lastdata}, status=status.HTTP_200_OK)


class brandlistview(generics.ListAPIView):
    queryset=Brand.objects.all()
    serializer_class = BrandSerializer

    def list(self,request,*args, **kwargs):
        queryset=self.filter_queryset(self.get_queryset())
        if not queryset.exists():
            raise NotFound(detail="No Brand found matching the criteria.")
        serializer =self.get_serializer(queryset, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)


class brandonedetail(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        brand_id = self.kwargs.get('pk')
        brand = Brand.objects.get(id=brand_id)
        queryset = Product.objects.all().filter(parts_brand_id=brand)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        brand_id=self.kwargs.get('pk')
        brand = Brand.objects.get(id=brand_id)
        if not queryset.exists():
            return Response({'details': 'Product Not Found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True)
        brand_serializer = BrandSerializer(brand,context={'request':request})
        lastdata = adddict(serializer)
        return Response({'brand':brand_serializer.data,'parts':lastdata}, status=status.HTTP_200_OK)


class vehiclelistview(generics.ListAPIView):
    queryset = Vehicle.objects.all()
    serializer_class =  VehicleSerializer

    def list(self, request, *args, **kwargs):
        queryset=self.filter_queryset(self.get_queryset())
        if not queryset.exists():
            raise NotFound(detail="No Vehicle found matching the criteria.")
        serializer=self.get_serializer(queryset,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)


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
                productserializer = ProductSerializer(this_part,context={'request':request}, many=True)
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
        serializer = VehicleSerializer(queryset, many=True,context={'request':request})
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
        serializer = self.get_serializer(queryset, many=True,context={'request': request})
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

        return Response({'Offer':categorized_data}, status=status.HTTP_200_OK)

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
        queryset=Wishlist.objects.all().filter(wishlist_name=self.request.user)
        return queryset

    def get_product(self):
        product_id = self.kwargs.get('pk')
        try:
            return Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return None

    def create(self, request, *args, **kwargs):
        product = self.get_product()
        print('p',product)
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
        return Response({ 'message': 'Wishlist created successfully'}, status=status.HTTP_201_CREATED, headers=headers)

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
            brand =wishlist_data['wishlist_name']
            # wishlist_delete_all=wishlist_data['wishlistdelall']
            product_info = {
                'wishlist_product': f"{wishlist_data['wishlist_product']['parts_brand']['brand_name']} {wishlist_data['wishlist_product']['parts_category']['category_name']} {wishlist_data['wishlist_product']['subcategory_name']}",
                'url' : wishlist_data['wishlist_product']['url'],
                'Wishlistdel':wishlist_data['wishlist_delete']
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
        response.set_cookie(self.COOKIE_NAME, json.dumps(cart_items), httponly=True, secure=True, max_age=3600, samesite='Lax')

    def set_cart_item_cookie(self, request, response, product_id, quantity):
        cookie_name = f'cart_product_{product_id}'
        existing_quantity = int(request.COOKIES.get(cookie_name, 0))
        new_quantity = existing_quantity + quantity
        response.set_cookie(cookie_name, new_quantity, httponly=True, max_age=3600, secure=True, samesite='Lax')

    def delete_cart_item_cookie(self, response, product_id):
        cookie_name = f'cart_product_{product_id}'
        response.delete_cookie(cookie_name)
        print(f'Deleting cookie: {cookie_name}')

    def delete_all_cart_item_cookies(self, request, response):
        cart_items = self.get_cart_items_from_cookie(request)
        for item in cart_items:
            product_id = item['product_id']
            self.delete_cart_item_cookie(response, product_id)
        response.delete_cookie(self.COOKIE_NAME)
        print(f'Deleting cookie: {self.COOKIE_NAME}')

    def clear_cart(self, request):
        response = Response({'message': 'Cart cleared'})
        self.delete_all_cart_item_cookies(request, response)
        return response

class ViewCartView(BaseCartView):

    def get(self, request):
        if request.user.is_authenticated:
            cart_items = Cart.objects.filter(user=request.user)
            serializer = CartSerializer(cart_items, many=True, context={'request': request})
            if not serializer.data:
                return Response({'message': 'No cart items found.'}, status=status.HTTP_404_NOT_FOUND)
            else:
                response = Response({'cart': serializer.data}, status=status.HTTP_200_OK)
                for item in serializer.data:
                    self.set_cart_item_cookie(request, response, item["product"], item["quantity"])
                return response
        else:
            cart_items = self.get_cart_items_from_cookie(request)
            cart_data = []
            for item in cart_items:
                product = Product.objects.get(id=item['product_id'])
                cart_data.append({
                    'user': None,
                    'product': product.id,
                    'quantity': item['quantity'],
                    'parts_name': CartSerializer().arrangename(product),
                    'parts_price': product.parts_price,
                    'parts_offer': product.parts_offer,
                    'discount_amount': (product.parts_price * product.parts_offer) / 100,
                    'final_price': product.parts_price - (product.parts_price * product.parts_offer) / 100,
                    'main_image': product.main_image,
                })

            if not cart_data:
                return Response({'message': 'No cart items found.'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'cart': cart_data}, status=status.HTTP_200_OK)

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
                            item.setdefault('code', []).append(c.carousel_code)
                            cart_data=[]
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
                                    'code': item['code'],
                                })
                            response = Response({'message': 'Added successfully', 'cart': cart_data}, status=status.HTTP_200_OK)
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
            response = Response({'message': 'Product added/incremented in cart', 'cart': serializer.data}, status=status.HTTP_200_OK)
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
            response = Response({'message': 'Product added/incremented in cart', 'cart': cart_data}, status=status.HTTP_200_OK)
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
                    response = Response({'message': 'Product decremented in cart', 'cart': serializer.data}, status=status.HTTP_200_OK)
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

            response = Response({'message': 'Product decremented in cart', 'cart': cart_data}, status=status.HTTP_200_OK)
            self.save_cart_items_to_cookie(response, cart_items)
            self.set_cart_item_cookie(request, response, pk, -decrement_quantity)
            return response

    def delete(self, request, pk):
        if request.user.is_authenticated:
            Cart.objects.filter(user=request.user, product=pk).delete()
            response = Response({'message': 'Item deleted from cart'}, status=status.HTTP_200_OK)
            self.delete_cart_item_cookie(response, pk)
            return response
        else:
            cart_items = self.get_cart_items_from_cookie(request)
            for item in cart_items:
                if item['product_id'] == pk:
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
            response = Response({'message': 'Item deleted from cart', 'cart': cart_data}, status=status.HTTP_200_OK)
            self.save_cart_items_to_cookie(response, cart_items)
            self.delete_cart_item_cookie(response, pk)
            return response

class RemoveFromCartView(BaseCartView):

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
            cart_items = [item for item in cart_items if item['product_id'] != pk]
            response = Response({'message': 'Product removed from cart'}, status=status.HTTP_200_OK)
            self.save_cart_items_to_cookie(response, cart_items)
            self.delete_cart_item_cookie(response, pk)
            return response

class Carouselallview(generics.ListAPIView):
    serializer_class = Carouselserilizers
    queryset = Carousel.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if not queryset.exists():
            return Response({'details': 'Carousel Not Found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'Carousel':serializer.data}, status=status.HTTP_200_OK)

class Carouseloneview(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        carousel_id = self.kwargs.get('pk')
        c = Carousel.objects.get(id=carousel_id)
        cat=c.carousel_category
        ban=c.carousel_brand
        queryset = Product.objects.all().filter(parts_category=cat,parts_brand=ban)
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
                "shipping_address": Shippingaddressserializer(result["shipping_address"]).data if result["shipping_address"] else None
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
                "total": total,
            })

        response = Response(status=status.HTTP_200_OK)
        for item in detailed_order_items:
            self.set_cart_item_cookie(request, response, item["product_id"], item["quantity"])

        response.data = {
            "preferred_billing_address": Billaddressserializer(preferred_billing_address).data if preferred_billing_address else None,
            "preferred_shipping_address": Shippingaddressserializer(preferred_shipping_address).data if preferred_shipping_address else None,
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
        else:
            Cart.objects.filter(session_key=request.session.session_key).delete()

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
