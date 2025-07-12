# Em apps/orders/urls.py
from django.urls import path
from .views.ui_views import order_list, order_detail, sync_orders_view

app_name = 'orders'  # Namespace para evitar conflito de nomes de URL

urlpatterns = [
    # Rota para a lista de pedidos: ex: /pedidos/
    path('', order_list, name='order_list'),

    # Rota para os detalhes de um pedido: ex: /pedidos/123/
    path('<int:order_id>/', order_detail, name='order_detail'),

    # Rota para a ação de sincronizar: ex: /pedidos/sincronizar/
    path('sincronizar/', sync_orders_view, name='sync_orders'),
]