from django.contrib import admin
from .models import Address, Order, OrderItem


class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ('pk', 'creation_date')


admin.site.register(Address)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
