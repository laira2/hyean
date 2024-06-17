from django.urls import path
from . import views

urlpatterns = [
    path('request/<int:order_id>/', views.payment_request, name='payment_request'),
    path('success/', views.payment_success, name='payment_success'),
    path('fail/', views.payment_fail, name='payment_fail'),
    path('checkout/', views.payment_checkout, name='checkout'),

]
