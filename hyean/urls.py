from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from openapi.views import openapi_view  # 수정된 부분
from user_account import views as account_views

schema_view = get_schema_view(
    openapi.Info(
        title="My API",
        default_version='v1',
        description="API 문서",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@myapi.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('artWork/', include('artWork.urls')),# artWork 앱의 URL 추가
    path('openapi/', openapi_view, name='openapi'),  # 수정된 부분
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('accounts/', include('allauth.urls')),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('login/', account_views.user_login, name='login'),
    path('signup/', account_views.signup, name="signup"),
    path('account/', account_views.account, name="account"),
    path('delete/', account_views.delete_account, name ="delete_account"),
    path('update/', account_views.update_profile,name="update_profile"),
    path('', include('payments.urls'), name='payments'),
    path('order/', include('orders.urls')),

]
