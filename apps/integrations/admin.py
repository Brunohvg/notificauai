from django.contrib import admin
from .models import Integration
from apps.integrations.ecommerce.nuvemshop.models import NuvemshopIntegration

@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    list_display = ('id', 'workspace', 'integration_type', 'is_active', 'created_at')
    list_filter = ('integration_type', 'is_active')
    search_fields = ('workspace__name',)




@admin.register(NuvemshopIntegration)
class NuvemshopIntegrationAdmin(admin.ModelAdmin):
    list_display = ('id', 'workspace', 'store_id', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('workspace__name', 'store_id')