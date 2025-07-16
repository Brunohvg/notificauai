from django.urls import path
from . import views

app_name = 'whatsapp'

urlpatterns = [
    # URL para o usuário clicar e iniciar a conexão
    path('auth/start/', views.start_whatsapp_auth, name='start_auth'),

]