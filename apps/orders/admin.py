from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrdersAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'customer',
        'workspace',
        'source',
        'external_id',
        'status',
        'total_amount',
        'order_created_at',
    )
    list_filter = ('source', 'status')
    search_fields = (
        'external_id',
        'customer__name',
        'customer__email',
        'workspace__name',
    )
    readonly_fields = ('raw_payload',)
