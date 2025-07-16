# Em apps/integrations/urls.py
from django.urls import path, include

app_name = 'integrations_api'

urlpatterns = [
    # Aponta DIRETAMENTE para o urls.py do módulo da Nuvemshop
    path('nuvemshop/', include('apps.integrations.ecommerce.nuvemshop.urls', namespace='nuvemshop')),
    path('whatsapp/', include('apps.integrations.messaging.whatsapp.urls', namespace='whatsapp'))
    # Futuramente:
    # path('mercadolivre/', include('apps.integrations.ecommerce.mercadolivre.urls', namespace='mercadolivre')),
]