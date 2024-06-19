from django.contrib import admin
from .models import Order, OrderItem, Ordered


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'total_price', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('user__username', 'name', 'email')
    inlines = [OrderItemInline]


class OrderedAdmin(admin.ModelAdmin):
    list_display = ('order', 'payment_id', 'payment_status', 'paid_amount', 'paid_at')
    list_filter = ('paid_at', 'payment_status')
    search_fields = ('order__user__username', 'payment_id')


admin.site.register(Order, OrderAdmin)
admin.site.register(Ordered, OrderedAdmin)

