# Em apps/integrations/urls.py
from django.urls import path, include

app_name = 'integrations'

urlpatterns = [
    # Aponta DIRETAMENTE para o urls.py do módulo da Nuvemshop
    path('nuvemshop/', include('apps.integrations.ecommerce.nuvemshop.urls', namespace='nuvemshop')),
    # Futuramente:
    # path('mercadolivre/', include('apps.integrations.ecommerce.mercadolivre.urls', namespace='mercadolivre')),
]