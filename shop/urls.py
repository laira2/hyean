from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.index, name='index'),
    # 다른 URL 패턴들을 필요에 따라 추가합니다.
]
