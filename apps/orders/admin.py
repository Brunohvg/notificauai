from django.contrib import admin
from .models import Customer, Address, Order, OrderItem


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0
    fields = ('address_type', 'street', 'number', 'floor', 'locality', 'city', 'province', 'zipcode', 'country')
    readonly_fields = ()
    show_change_link = True


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'source', 'external_id', 'workspace', 'total_spent_formatted')
    search_fields = ('name', 'email', 'external_id')
    list_filter = ('source', 'workspace')
    inlines = [AddressInline]

    def total_spent_formatted(self, obj):
        return f"R$ {obj.total_spent:.2f}" if hasattr(obj, 'total_spent') else "-"
    total_spent_formatted.short_description = "Total Gasto"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('external_product_id', 'product_name', 'quantity', 'price')
    can_delete = False
    show_change_link = True


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('external_id', 'customer', 'status', 'total_amount_formatted', 'order_created_at', 'workspace')
    list_filter = ('status', 'source', 'workspace')
    search_fields = ('external_id', 'customer__name', 'tracking_code')
    date_hierarchy = 'order_created_at'
    inlines = [OrderItemInline]

    def total_amount_formatted(self, obj):
        return f"R$ {obj.total_amount:.2f}"
    total_amount_formatted.short_description = "Total"


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('customer', 'address_type', 'street', 'number', 'floor', 'locality', 'city', 'province', 'zipcode', 'country')
    search_fields = ('customer__name', 'street', 'city', 'province', 'zipcode')
    list_filter = ('address_type', 'province', 'country')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'order', 'quantity', 'price_formatted')
    search_fields = ('product_name', 'external_product_id')

    def price_formatted(self, obj):
        return f"R$ {obj.price:.2f}"
    price_formatted.short_description = "Preço"
