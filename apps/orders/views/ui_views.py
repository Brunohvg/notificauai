from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from apps.orders.models import Order, Customer
from django.utils.timezone import make_aware # <<< IMPORTE a função make_aware
from django.core.paginator import Paginator # <<< IMPORTE O PAGINATOR
from django.shortcuts import render
from django.db.models import Q # Importe o Q object
from django.db.models import Count
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

    # Adicione a paginação antes do context
    paginator = Paginator(queryset, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
        
    context = {
        'page_obj': page_obj,
        'orders': page_obj, # Mantém 'orders' para compatibilidade
        'paginator': paginator,
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


def customer_list(request):
    """
    Exibe a lista de clientes com filtros e ordenação avançada.
    """
    if not hasattr(request, 'workspace') or not request.workspace:
        return render(request, 'orders/customer_list.html', context={'error': 'Workspace não encontrada.'})

    # A queryset base continua a mesma, calculando o total de pedidos
    customers_queryset = Customer.objects.filter(
        workspace=request.workspace
    ).annotate(
        order_count=Count('orders')
    )

    # --- LÓGICA DE FILTROS ---
    query_param = request.GET.get('q')
    marketing_param = request.GET.get('accepts_marketing')

    if query_param:
        customers_queryset = customers_queryset.filter(
            Q(name__icontains=query_param) |
            Q(email__icontains=query_param) |
            Q(identification__icontains=query_param)
        )
    
    # NOVO: Filtro por 'Aceita Marketing'
    if marketing_param in ['true', 'false']:
        accepts = (marketing_param == 'true')
        customers_queryset = customers_queryset.filter(accepts_marketing=accepts)

    # --- LÓGICA DE ORDENAÇÃO ---
    sort_by = request.GET.get('sort_by', '-created_at') # Padrão: mais recentes

    if sort_by == 'total_spent':
        # Ordena pelo maior valor gasto
        customers_queryset = customers_queryset.order_by('-total_spent')
    elif sort_by == 'order_count':
        # Ordena pela maior quantidade de pedidos
        customers_queryset = customers_queryset.order_by('-order_count', '-total_spent')
    else:
        # Padrão: ordena pelos clientes criados mais recentemente
        customers_queryset = customers_queryset.order_by('-created_at')

    # --- LÓGICA DE PAGINAÇÃO ---
    paginator = Paginator(customers_queryset, 10) # Mostra 25 clientes por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj, # Passamos o objeto da página, não mais a queryset inteira
        'customers': page_obj, # Mantemos 'customers' para compatibilidade com a tabela
        'paginator': paginator, # Passamos o paginator para o template de paginação
        'header_title': 'Clientes',
    }
    return render(request, 'orders/customer_list.html', context)

def customer_order_list(request, customer_id):
    """
    Exibe a lista de pedidos para um cliente específico, com filtros.
    """
    if not hasattr(request, 'workspace') or not request.workspace:
        return render(request, 'orders/base_orders.html', context={'error': 'Workspace não encontrada.'})

    # 1. Pega o cliente específico pelo ID da URL ou retorna um erro 404
    customer = get_object_or_404(Customer, pk=customer_id, workspace=request.workspace)

    # 2. A busca de pedidos começa já filtrada por este cliente
    queryset = Order.objects.filter(workspace=request.workspace, customer=customer).select_related('customer').order_by('-order_created_at')

    # O resto da lógica de filtro é EXATAMENTE a mesma da view order_list
    # (copiamos e colamos, pois a funcionalidade é a mesma)
    status_choices = dict(Order.Status.choices)
    query_param = request.GET.get('q')
    status_param = request.GET.get('status')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')

    if query_param:
        queryset = queryset.filter(number__icontains=query_param) # Aqui buscamos só por número do pedido
    if status_param:
        queryset = queryset.filter(status=status_param)
    if data_inicio:
        dt_inicio = make_aware(datetime.strptime(data_inicio, '%Y-%m-%d'))
        queryset = queryset.filter(order_created_at__gte=dt_inicio)
    if data_fim:
        dt_fim_completo = make_aware(datetime.combine(datetime.strptime(data_fim, '%Y-%m-%d'), time.max))
        queryset = queryset.filter(order_created_at__lte=dt_fim_completo)

    # Adicione a paginação antes do context
    paginator = Paginator(queryset, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'orders': page_obj, # Mantém 'orders' para compatibilidade
        'paginator': paginator,
        'orders': queryset,
        'customer': customer, # Passa o cliente para o template
        'header_title': f'Pedidos de {customer.name}', # Título dinâmico
        'status_choices': status_choices,
    }
    # 3. REUTILIZAMOS o mesmo template da lista de pedidos!
    return render(request, 'orders/base_orders.html', context)


def customer_detail(request, customer_id):
    """
    Exibe a página de perfil de um cliente específico com suas métricas e pedidos recentes.
    """
    if not hasattr(request, 'workspace') or not request.workspace:
        return render(request, 'orders/customer_detail.html', context={'error': 'Workspace não encontrada.'})

    # Busca o cliente específico
    customer = get_object_or_404(Customer, pk=customer_id, workspace=request.workspace)

    # Busca os 5 pedidos mais recentes deste cliente
    recent_orders = customer.orders.all().order_by('-order_created_at')[:5]

    # Calcula as métricas
    order_count = customer.orders.count()
    total_spent = customer.total_spent  # Já temos este campo no modelo!

    ticket_medio = 0
    if order_count > 0:
        ticket_medio = total_spent / order_count

    context = {
        'customer': customer,
        'recent_orders': recent_orders,
        'order_count': order_count,
        'ticket_medio': ticket_medio,
        'header_title': f'Perfil de {customer.name}',
    }
    return render(request, 'orders/customer_detail.html', context)