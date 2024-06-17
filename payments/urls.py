from django.urls import path
from .views import create_order, payment_success, payment_fail, confirm_payment, payment_request

urlpatterns = [
    path('create-order/', create_order, name='create_order'),
    path('success/', payment_success, name='payment_success'),
    path('fail/', payment_fail, name='payment_fail'),
    path('confirm/', confirm_payment, name='confirm_payment'),
    path('checkout/', payment_request, name='payment_request'),  # checkout URL 추가
]
