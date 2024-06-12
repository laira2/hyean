from django.urls import path
from . import views
from .detail_page import detail_view


urlpatterns = [
    path('', views.openapi_view, name='index'), # path('', views.index, name='index'),  # 예를 들어, index view로 연결
    path('search/', views.search, name='search_query'), # path('<str:artNm>/', views.search, name='search_query')
    path('artwork-api/', views.artwork_api, name='artwork_api'), # path('search/<str:search_query>/', views.search, name='search_query'),
    path('detail/<str:art_name>/', detail_view, name='detail'),
]
