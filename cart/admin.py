from django.contrib import admin

from .models import Cart, CartAddedItem

class CartAddedItemInline(admin.TabularInline):  # TabularInline을 사용하면 테이블 형식으로 표시됩니다.
    model = CartAddedItem
    extra = 0  # 기본적으로 추가할 수 있는 Inline 항목 수, 0으로 설정하면 기본적으로 아무것도 추가되지 않습니다.

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    inlines = [CartAddedItemInline]
# Register your models here.
admin.site.register(CartAddedItem)