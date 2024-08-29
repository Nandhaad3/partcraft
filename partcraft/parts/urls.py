from rest_framework import routers
from .views import *
from django.urls import path

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
    path('cart/add/<int:pk>/', CartItemsCreateView.as_view(), name='cart-add'),  # Add or increment an item in the cart
    path('cart/view/', ViewCartView.as_view(), name='cart-view'),  # View the items in the cart
    path('cart/remove/<int:pk>/', CartItemsCreateView.as_view(), name='cart-remove'),# Decrement or remove an item from the cart
    path('cart/clear/', RemoveFromCartView.as_view(), name='cart-clear'),# Clear all items from the cart
    path('carouselallview/',Carouselallview.as_view(),name='carouselallview'),
    path('carouseloneview/<int:pk>',Carouseloneview.as_view(),name='carouseloneview'),
    path('buynow/<int:pk>/', BuyNowAPIView.as_view(), name='buy_now'),
    path('billing_address/', BillingDealerView.as_view(), name='billing_addres'),
    path('order_summary/', OrderSummaryAPIView.as_view(), name='order_summary'),
    path('place_order/', OrderAPIView.as_view(), name='place_order'),
    path('couponcodeapply/',ViewCartView.as_view(),name='couponcodeapply'),
    path('best_selling/', BestSellingView.as_view(), name='best_selling'),
    path('my_order/', MyOrderView.as_view(), name='my_order'),
    path('order_status/<str:order_id>/', MyOrderView.as_view(), name='order_status'),
    path('top-ten/', ToptenView.as_view(), name='top-ten'),
    path('top-ten-product/<int:pk>/', ToptenProductView.as_view(), name='top-ten-product'),
    path('feedback/',FeedbackView.as_view(), name='feedback'),
    path('dealers/', DealerAddressView.as_view(), name='dealers'),
]

