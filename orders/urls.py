# orders/urls.py
from django.urls import path
from .views import order_page

urlpatterns = [
    path('', order_page, name='order'),
    path('order_page/', order_page, name='order_page'),
]