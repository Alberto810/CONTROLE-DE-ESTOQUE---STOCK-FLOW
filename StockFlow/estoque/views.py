from django.shortcuts import render
from django.db.models import F, Sum
from django.utils import timezone
from .models import Produto, Movimentacao

def dashboard(request):
    produtos = Produto.objects.select_related('fornecedor').all()
    
    # Cálculos para os Cards (KPIs)
    total_itens = sum(p.estoque_atual for p in produtos)
    produtos_alerta = produtos.filter(estoque_atual__lt=F('estoque_minimo'))
    alertas_count = produtos_alerta.count()
    
    # Simula a contagem de movimentações do dia atual
    hoje = timezone.now().date()
    movimentacoes_hoje = Movimentacao.objects.filter(data__date=hoje).count()

    context = {
        'produtos': produtos,
        'total_itens': total_itens,
        'alertas_count': alertas_count,
        'produtos_alerta': produtos_alerta[:5], # Pega apenas os 5 primeiros para a lista lateral
        'movimentacoes_hoje': movimentacoes_hoje,
    }
    return render(request, 'estoque/dashboard.html', context)