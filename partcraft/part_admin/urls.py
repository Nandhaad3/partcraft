from django.urls import path, include
from rest_framework import routers
from .views import *



urlpatterns = [
    path('admin_index/',IndexView.as_view(),name='admin_index'),
]

