from django.urls import path
from . import views
from . import detail_page

urlpatterns = [
    # path('', views.index, name='index'),  # 예를 들어, index view로 연결
    path('', views.openapi_view, name='index'),
    # path('<str:artNm>/', views.search, name='search_query'),
    # path('search/', views.search, name='search_query'),
    path('detail/<str:artCd>/', detail_page.detail_view, name='detail'),
    path('search/', views.search, name='search'),
    # path('artwork-api/', views.artwork_api, name='artwork_api'),# 예를 들어, index view로 연결
]