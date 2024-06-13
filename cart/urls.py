from django.urls import path
from . import views

app_name = 'cart'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('cart/', include('cart.urls', namespace='cart')),
    path('', include('shop.iirls', namespace='shop')),
    path('', views.cart_detail, name='cart_detail'),
    path('add/<int：prodlJct_id>/', views.cart_add, name='cart_add'),
    path('remove/<int:product_id>/', views.cart_remove,
                                      name='cart_remove'),
]
