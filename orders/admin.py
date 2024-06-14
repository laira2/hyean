from django.contrib import admin
from .models import Order

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'artCd', 'art_name', 'file_name', 'price', 'name', 'phone', 'email', 'order_date']
    list_filter = ['order_date']
    search_fields = ['artCd', 'art_name', 'name', 'phone', 'email']
    readonly_fields = ['order_date']

    def has_add_permission(self, request):
        return True

admin.site.register(Order, OrderAdmin)
