from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('confirm/', views.confirm_payment, name='confirm'),
    path('success/', views.success, name='success'),
    path('fail/', views.fail, name='fail'),
    path('my_view/<int:order_id>', views.my_view, name='my_view')
]
