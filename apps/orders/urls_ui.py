# Em apps/orders/urls.py
from django.urls import path
from .views.ui_views import order_list, order_detail, sync_orders_view, customer_list, customer_order_list, customer_detail

app_name = 'orders'  # Namespace para evitar conflito de nomes de URL

urlpatterns = [
    # Rota para a lista de pedidos: ex: /pedidos/
    path('', order_list, name='order_list'),

    # Rota para os detalhes de um pedido: ex: /pedidos/123/
    path('<int:order_id>/', order_detail, name='order_detail'),

    # Rota para a ação de sincronizar: ex: /pedidos/sincronizar/
    path('sincronizar/', sync_orders_view, name='sync_orders'),
    # NOVA ROTA PARA CLIENTES
    path('clientes/', customer_list, name='customer_list'),
    path('clientes/<int:customer_id>/pedidos/', customer_order_list, name='customer_order_list'),
    path('clientes/<int:customer_id>/', customer_detail, name='customer_detail'),



]