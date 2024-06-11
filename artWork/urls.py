from django.urls import path
from . import views  # artWork의 views를 import

urlpatterns = [
    path('', views.index, name='index'),
    path('artwork-api/', views.artwork_api, name='artwork_api'),# 예를 들어, index view로 연결
]