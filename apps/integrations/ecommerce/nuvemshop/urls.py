from django.urls import path
from . import views  # Importa as views do mesmo diretório

app_name = 'nuvemshop'

urlpatterns = [
    # A URL final é associada DIRETAMENTE a uma função em views.py
    path('webhook/', views.nuvemshop_webhook_receiver, name='webhook_receiver'),
]