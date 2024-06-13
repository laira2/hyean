from django.urls import path
from . import views
from .detail_page import detail_view


urlpatterns = [
    # path('', views.index, name='index'),  # 예를 들어, index view로 연결
    path('', views.openapi_view, name='index'),
    # path('<str:artNm>/', views.search, name='search_query'),
    # path('search/', views.search, name='search_query'),
    path('search/', views.search, name='search'),
    # path('artwork-api/', views.artwork_api, name='artwork_api'),# 예를 들어, index view로 연결
    path('detail/<str:art_name>/', detail_view, name='detail'),
    path('infinite-view/', views.infiniteView, name='infinite-view'),
]
