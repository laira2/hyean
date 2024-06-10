from django.urls import path
from . import views  # artWork의 views를 import

urlpatterns = [
    path('', views.index, name='index'),  # 예를 들어, index view로 연결
]