from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.db.models import F, Sum, Q
from django.utils import timezone
from .models import Produto, Movimentacao
from .forms import ProdutoForm, MovimentacaoForm

@login_required
def dashboard(request):
    
    #Captura o termo digitado na barra de pesquisa
    query = request.GET.get('q', '')
    
    #Busca todos os produtos para os cálculos gerais
    produtos_base = Produto.objects.select_related('fornecedor').all().order_by('-id')
    
    #Se houver um termo de pesquisa, filtra os produtos
    if query:
        produtos = produtos_base.filter(
            Q(nome__icontains=query) | Q(sku__icontains=query)
        )
    else:
        produtos = produtos_base
        
    #Configura a paginação para a tabela de produtos
    paginator = Paginator(produtos, 10)  
    page_number = request.GET.get('page')
    produtos_paginados = paginator.get_page(page_number)
    
    # Cálculos para os Cards (KPIs)
    total_itens = sum(p.estoque_atual for p in produtos_base)
    produtos_alerta = produtos_base.filter(estoque_atual__lt=F('estoque_minimo'))
    alertas_count = produtos_alerta.count()
    
    # Simula a contagem de movimentações do dia atual
    hoje = timezone.now().date()
    movimentacoes_hoje = Movimentacao.objects.filter(data__date=hoje).count()

    context = {
        'produtos': produtos_paginados, # Lista filtrada para a tabela 
        'total_itens': total_itens,
        'alertas_count': alertas_count,
        'produtos_alerta': produtos_alerta[:5], # Pega apenas os 5 primeiros para a lista lateral
        'movimentacoes_hoje': movimentacoes_hoje,
        'query': query,
    }
    return render(request, 'estoque/dashboard.html', context)

@login_required
def produto_criar(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            form.save()
            # Redireciona de volta para o dashboard após salvar
            return redirect('dashboard')
    else:
        form = ProdutoForm()
    
    return render(request, 'estoque/produto_form.html', {'form': form})

@login_required
def movimentacao_criar(request):
    if request.method == 'POST':
        form = MovimentacaoForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return redirect('dashboard')
            except ValidationError as e:
                # Captura o erro do banco de dados e exibe no formulário
                form.add_error(None, e.message)
    else:
        form = MovimentacaoForm()
    
    return render(request, 'estoque/movimentacao_form.html', {'form': form})