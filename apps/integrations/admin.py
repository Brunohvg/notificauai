from django.contrib import admin
from .models import Integration
from apps.integrations.ecommerce.nuvemshop.models import NuvemshopIntegration
from apps.integrations.messaging.whatsapp.models import WhatsappIntegration
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

@admin.register(WhatsappIntegration)
class WhatsappIntegrationAdmin(admin.ModelAdmin):
    list_display = ('id', 'workspace', 'name', 'phone_number','is_active', 'integration_type', 'created_at' )
    list_filter =  ('integration_type', 'is_active', )
    search_fields = ('workspace__name', 'name', 'phone_number')