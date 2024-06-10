from django.db.migrations import serializer
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser,IsAuthenticatedOrReadOnly,IsAuthenticated
from rest_framework import status, generics
# from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import NotFound
from rest_framework.filters import  SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view
from rest_framework import viewsets
from .models import *
from .serializers import *
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
        last_data.append(data)
    return last_data

def offerdata(queryset):
    return queryset.values_list('parts_offer', flat=True).distinct()
class partslistview(generics.ListAPIView):
    queryset = Product.objects.all()
    print(queryset)
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = OfferfilterSet



    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        print(queryset)
        if not queryset.exists():
            raise NotFound(detail="No Product found matching the criteria.")
        serializer = self.get_serializer(queryset, many=True)
        lastdata=adddict(serializer)
        # offer=offerdata(queryset)
        return Response(lastdata, status=status.HTTP_200_OK)

class partsonedetail(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    def get_queryset(self):
        product_id=self.kwargs.get('pk')
        print(product_id)

        quaryset=Product.objects.filter(id=product_id)
        return quaryset
    def list(self,request,*args, **kwargs):
        queryset=self.get_queryset()
        if not queryset.exists():
            return Response({'details':'Product Not Found'},status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

class categorylistview(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if not queryset.exists():
            raise NotFound(detail="No Category found matching the criteria.")
        serializer = self.get_serializer(queryset, many=True)
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
