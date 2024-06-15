from django.contrib import admin
from .models import Order, OrderItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email_name', 'address', 'payment_status', 'created_at')
    list_filter = ('payment_status', 'created_at')
    search_fields = ('username', 'email_name', 'address')
    readonly_fields = ('created_at',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'art_code', 'art_name', 'price', 'image_url')
    list_filter = ('order',)
    search_fields = ('art_code', 'art_name')
