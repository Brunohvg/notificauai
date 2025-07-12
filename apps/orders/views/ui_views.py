from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from apps.orders.models import Order
from django.utils.timezone import make_aware # <<< IMPORTE a função make_aware

from django.shortcuts import render
from django.db.models import Q # Importe o Q object

from datetime import datetime, time

def order_list(request):
    """
    Exibe a lista de pedidos com filtros avançados, incluindo filtro por status.
    """
    if not hasattr(request, 'workspace') or not request.workspace:
        return render(request, 'orders/base_orders.html', context={'error': 'Workspace não encontrada.'})

    # NOVO: Pega os status do modelo para enviar ao template
    status_choices = dict(Order.Status.choices)

    queryset = Order.objects.filter(workspace=request.workspace).select_related('customer').order_by('-order_created_at')

    # Parâmetros da URL
    query_param = request.GET.get('q')
    status_param = request.GET.get('status') # NOVO: Pega o parâmetro do status
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')

    # Filtro geral
    if query_param:
        queryset = queryset.filter(
            Q(number__icontains=query_param) |
            Q(customer__name__icontains=query_param) |
            Q(customer__identification__icontains=query_param)
        )

    # NOVO: Filtro por status
    if status_param:
        queryset = queryset.filter(status=status_param)

    # Filtro por data
    if data_inicio:
        dt_inicio = make_aware(datetime.strptime(data_inicio, '%Y-%m-%d'))
        queryset = queryset.filter(order_created_at__gte=dt_inicio)
    if data_fim:
        dt_fim_completo = make_aware(datetime.combine(datetime.strptime(data_fim, '%Y-%m-%d'), time.max))
        queryset = queryset.filter(order_created_at__lte=dt_fim_completo)
        
    context = {
        'orders': queryset,
        'header_title': 'Meus Pedidos',
        'status_choices': status_choices, # NOVO: Passa a lista de status para o template
    }
    return render(request, 'orders/base_orders.html', context)

def order_detail(request, order_id):
    """
    Exibe os detalhes completos de um único pedido.
    """
    if not hasattr(request, 'workspace') or not request.workspace:
        return render(request, 'orders/order_detail.html', context={'error': 'Workspace não encontrada.'})

    # Otimização avançada para a página de detalhes:
    # - select_related: para o cliente e endereço (relações 1-para-1)
    # - prefetch_related: para os itens do pedido (relação 1-para-muitos)
    query = Order.objects.select_related('customer', 'shipping_address').prefetch_related('items')

    # get_object_or_404 é a forma padrão do Django para buscar um objeto ou retornar um erro 404
    order = get_object_or_404(query, pk=order_id, workspace=request.workspace)

    context = {
        'order': order,
        'header_title': f'Detalhes do Pedido #{order.number or order.external_id}',
    }
    return render(request, 'orders/order_detail.html', context)


def sync_orders_view(request):
    """
    View de exemplo para o botão de sincronização.
    Aqui você colocaria a lógica para chamar a API e atualizar os pedidos.
    """
    # Exemplo: messages.success(request, "Sincronização iniciada com sucesso!")
    print("Lógica de sincronização de pedidos seria executada aqui.")
    
    # Redireciona de volta para a lista de pedidos
    return HttpResponseRedirect(reverse('orders:order_list'))