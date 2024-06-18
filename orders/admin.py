# orders/admin.py
from django.contrib import admin
from .models import Order,OrderItem

class OrderItemInline(admin.TabularInline):  # TabularInline을 사용하면 테이블 형식으로 표시됩니다.
    model = OrderItem
    extra = 0  # 기본적으로 추가할 수 있는 Inline 항목 수, 0으로 설정하면 기본적으로 아무것도 추가되지 않습니다.

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
# Register your models here.
admin.site.register(OrderItem)