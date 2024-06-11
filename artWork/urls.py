from django.urls import path
from . import views

urlpatterns = [
    # path('', views.index, name='index'),  # 예를 들어, index view로 연결
    path('', views.openapi_view, name='index'),
    # path('<str:search>/', views.search_view, name='search_view'),
]