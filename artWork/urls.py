from django.urls import path
from . import views
from . import detail_page
from .views import detail_view  # detail_view 함수를 임포트

urlpatterns = [
    # path('', views.index, name='index'),  # 예를 들어, index view로 연결
    path('', views.openapi_view, name='index'),
    # path('', views.infiniteView, name='index'), infiniteView로 메인페이지 전체 띄우기 작업을 하기 위함 준비
    # path('<str:artNm>/', views.search, name='search_query'),
    # path('search/', views.search, name='search_query'),
    path('detail/<str:artCd>/', detail_page.detail_view, name='detail'),
    path('detail/<str:art_name>/', detail_view, name='detail'),  # URL 패턴 설정
    path('search/', views.search, name='search'),
    # path('artwork-api/', views.artwork_api, name='artwork_api'),# 예를 들어, index view로 연결
    path('detail/<str:art_name>/', detail_view, name='detail'),
    path('infinite-view/', views.infiniteView, name='infinite-view'),

]
