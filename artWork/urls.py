from django.urls import path
from . import views
from . import detail_page
from .detail_page import detail_view
from cart.views import add_cart , cart_detail, cart_remove

urlpatterns = [
    # path('', views.index, name='index'),  # 예를 들어, index view로 연결
    path('', views.openapi_view, name='index'),
    # path('', views.infiniteView, name='index'), infiniteView로 메인페이지 전체 띄우기 작업을 하기 위함 준비
    # path('<str:artNm>/', views.search, name='search_query'),
    # path('search/', views.search, name='search_query'),
    path('detail/<str:artCd>/', detail_page.detail_view, name='detail'),
    path('search/', views.search, name='search'),
    # path('artwork-api/', views.artwork_api, name='artwork_api'),# 예를 들어, index view로 연결
    path('detail/<str:art_name>/', detail_view, name='detail'),
    path('infinite-view/', views.infiniteView, name='infinite-view'),
    path('add/',add_cart,name ="add_cart"),
    path('cart/detail/',cart_detail, name="cart_detail" ),
    path('cart/remove/', cart_remove, name="cart_remove")

]
