from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('success/', views.success, name='payment_success'),
    path('fail/', views.fail, name='payment_fail'),
    path('checkout/', views.checkout_view, name='checkout'),
]
