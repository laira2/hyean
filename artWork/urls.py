from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('artWork/', include('artWork.urls')),  # artWork 앱의 URL 추가
    # 다른 URL 패턴 추가
]
