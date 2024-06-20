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
        print(queryset)
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




class ViewCartView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            cart_items = Cart.objects.filter(user=request.user)
        else:
            session_key = request.session.session_key
            cart_items = Cart.objects.filter(session_key=session_key)

        serializer = CartSerializer(cart_items, many=True, context={'request': request})
        if bool(serializer.data) is False:
            return Response({'cart': 'No Product in the Cart'}, status=status.HTTP_200_OK)
        else:
            return Response({'cart': serializer.data}, status=status.HTTP_200_OK)


# class CartItemsCreateView(APIView):
#     def post(self, request, pk):
#         product = get_object_or_404(Product, pk=pk)
#         print(product)
#         quantity = request.data.get('quantity', 1)
#         print(type(quantity))
#         quantity = int(quantity)
#         cart = request.session.get('cart', {})
#
#         if str(product) in cart:
#             cart[str(product)]['quantity'] += quantity
#         else:
#             cart[str(product)] = {
#                 'quantity': quantity,
#                 'parts_price': product.parts_price,
#                 'main_image': product.main_image.url,
#             }
#
#         request.session['cart'] = cart
#         return Response({'message': 'Product added to cart', 'cart': cart}, status=status.HTTP_200_OK)
#
#     def patch(self, request, pk):
#         product = get_object_or_404(Product, pk=pk)
#         decrement_quantity = request.data.get('quantity', 1)
#
#         cart = request.session.get('cart', {})
#
#         if str(product) in cart:
#             if cart[str(product)]['quantity'] > decrement_quantity:
#                 cart[str(product)]['quantity'] -= decrement_quantity
#             else:
#                 del cart[str(product)]
#         else:
#             return Response({'message': 'Product not in cart'}, status=status.HTTP_400_BAD_REQUEST)
#
#         request.session['cart'] = cart
#         return Response({'message': 'Product decremented/removed from cart', 'cart': cart}, status=status.HTTP_200_OK)

    # def delete(self, request):
    #     if bool(request.session['cart']) is False:
    #         return Response({'message': 'Cart has already cleared'}, status=status.HTTP_200_OK)
    #     request.session['cart'] = {}
    #     return Response({'message': 'All item has cleared successfully'}, status=status.HTTP_200_OK)


class CartItemsCreateView(APIView):

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        print(product)
        quantity = request.data.get('quantity', 1)
        quantity=int(quantity)

        if request.user.is_authenticated:
            cart_item, created = Cart.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={'quantity': quantity}
            )
        else:
            if not request.session.session_key:
                request.session.create()
            cart_item, created = Cart.objects.get_or_create(
                session_key=request.session.session_key,
                product=product,
                defaults={'quantity': quantity}
            )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        print(type(cart_item))
        serializer = CartSerializer(cart_item, context={'request': request})
        return Response({'message': 'Product added/incremented in cart', 'cart': serializer.data}, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        decrement_quantity = request.data.get('quantity', 1)

        if request.user.is_authenticated:
            cart_item = Cart.objects.filter(user=request.user, product=product).first()
        else:
            cart_item = Cart.objects.filter(session_key=request.session.session_key, product=product).first()

        if cart_item:
            if cart_item.quantity > decrement_quantity:
                cart_item.quantity -= decrement_quantity
                cart_item.save()
                serializer = CartSerializer(cart_item, context={'request': request})
                return Response({'message': 'Product decremented in cart', 'cart': serializer.data}, status=status.HTTP_200_OK)
            else:
                cart_item.delete()
                return Response({'message': 'Product removed from cart'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Product not in cart'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        if request.user.is_authenticated:
            c=Cart.objects.filter(user=request.user)
            if bool(c) is False:
                return Response({'message': 'Cart has already cleared'}, status=status.HTTP_200_OK)
            c.delete()
            return Response({'message': 'All items cleared from cart'}, status=status.HTTP_200_OK)

        else:
            c=Cart.objects.filter(session_key=request.session.session_key)
            if bool(c) is False:
                return Response({'message': 'Cart has already cleared'}, status=status.HTTP_200_OK)
            c.delete()
            return Response({'message': 'All items cleared from cart'}, status=status.HTTP_200_OK)


class RemoveFromCartView(APIView):

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)

        if request.user.is_authenticated:
            cart_item = Cart.objects.filter(user=request.user, product=product).first()
            if cart_item:
                cart_item.delete()
                return Response({'message': 'Product removed from cart'}, status=status.HTTP_200_OK)
            return Response({'error': 'Product not in cart'}, status=status.HTTP_400_BAD_REQUEST)

        else:
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key

            cart_item = Cart.objects.filter(session_key=session_key, product=product).first()
            if cart_item:
                cart_item.delete()
                return Response({'message': 'Product removed from cart'}, status=status.HTTP_200_OK)
            return Response({'error': 'Product not in cart'}, status=status.HTTP_400_BAD_REQUEST)

