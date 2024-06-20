from django.urls import path, include
from rest_framework import routers
from .views import *



urlpatterns = [
    path('allproducts/',partslistview.as_view(),name='allproducts'),
    path('getoneproduct/<int:pk>/',partsonedetail.as_view(),name='getoneproduct'),
    path('allcategory/',categorylistview.as_view(),name='allcatetgories'),
    path('onecategorydetails/<int:pk>/',categoryonedetail.as_view(),name='onecategorydetails'),
    path('allbrand/',brandlistview.as_view(),name='allbrands'),
    path('brandonedetails/<int:pk>/',brandonedetail.as_view(),name='brandonedetails'),
    path('allvehicles/',vehiclelistview.as_view(),name='allvehicles'),
    path('vehiclegetview/',vehicle_view,name='vechilegetview'),
    path('vehicleonedetail/<int:pk>/',vehicleoneview.as_view(),name='vehicleonedetail'),
    path('alloffer/',allofferview.as_view(),name='alloffer'),
    path('offerproduct/<int:pk>/',partsonedetail.as_view(),name='offerproduct'),
    path('wishlistcreate/<int:pk>/',WishlistCreateView.as_view(),name='wishlistcreate'),
    path('wishallview/',WishallView.as_view(),name='wishallview'),
    path('wishdeleteoneitem/<int:pk>/', DeleteWishlistItemView.as_view(), name='wishdeleteoneitem'),
    path('wishdeleteitem/', DeleteAllWishlistItemsView.as_view(), name='wishdeleteitem'),
    path('cartlistcreate/<int:pk>/',CartItemsCreateView.as_view(),name='Cartlistcreate'),
    path('viewcartlist/',ViewCartView.as_view(),name='viewcartlist'),
    path('removecartitem/<int:pk>/',RemoveFromCartView.as_view(),name='removecartitem'),
    path('clearallcartitem/',CartItemsCreateView.as_view(),name='clearallcartitem'),
]

