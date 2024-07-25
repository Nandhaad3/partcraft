from django.urls import path, include
from rest_framework import routers
from .views import *

urlpatterns = [
    path('allproducts/', partslistsDocumentView.as_view({'get': 'list'}), name='allproducts'),
]

