from django.urls import path
from . import views

app_name = 'whatsapp'

urlpatterns = [
    # URL para o usuário clicar e iniciar a conexão
    path('auth/start/', views.start_nuvemshop_auth, name='start_auth'),
    
    # URL de callback que a     
    path('auth/callback/', views.nuvemshop_callback, name='callback'),
    
    # URL do webhook que a Nuvemshop usará para nos enviar eventos
    path('webhook/<str:received_token>/', views.nuvemshop_webhook_receiver, name='webhook_receiver'),
]