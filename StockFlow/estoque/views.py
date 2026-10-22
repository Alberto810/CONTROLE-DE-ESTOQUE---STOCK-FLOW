import io
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.db.models import F, Sum, Q, Case, When, IntegerField
import json
from django.utils import timezone
from .models import Produto, Movimentacao, Fornecedor
from .forms import ProdutoForm, MovimentacaoForm, FornecedorForm

@login_required
def dashboard(request):
    # Captura a busca e o filtro da URL (forçando letras minúsculas no filtro)
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '').lower() 
    
    # 1. Busca base
    produtos_base = Produto.objects.select_related('fornecedor').all().order_by('-id')
    produtos_lista = produtos_base

    # 2. Aplica a pesquisa por texto
    if query:
        produtos_lista = produtos_lista.filter(
            Q(nome__icontains=query) | Q(sku__icontains=query)
        )

    # 3. Aplica o filtro de status na MESMA lista
    if status_filter == 'esgotado':
        produtos_lista = produtos_lista.filter(estoque_atual__lte=0)
    elif status_filter == 'baixo':
        produtos_lista = produtos_lista.filter(estoque_atual__gt=0, estoque_atual__lt=F('estoque_minimo'))
    elif status_filter == 'ok':
        produtos_lista = produtos_lista.filter(estoque_atual__gte=F('estoque_minimo'))

    # 4. Pagina a lista já filtrada
    paginator = Paginator(produtos_lista, 8) 
    page_number = request.GET.get('page')
    produtos_paginados = paginator.get_page(page_number)

    # 5. Calcula os KPIs do topo da tela (sempre usando produtos_base para os cards não zerarem)
    total_itens = sum(p.estoque_atual for p in produtos_base)
    produtos_alerta = produtos_base.filter(estoque_atual__lt=F('estoque_minimo'))
    alertas_count = produtos_alerta.count()

    hoje = timezone.now().date()
    movimentacoes_hoje = Movimentacao.objects.filter(data__date=hoje).count()

    # 6. Envia tudo para o HTML
    context = {
        'produtos': produtos_paginados, # Tabela recebe apenas os itens filtrados
        'total_itens': total_itens,
        'alertas_count': alertas_count,
        'produtos_alerta': produtos_alerta[:10],  # Mostra apenas os 10 primeiros produtos em alerta
        'movimentacoes_hoje': movimentacoes_hoje,
        'query': query,
        'status_filter': status_filter,
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

@login_required
def historico_movimentacoes(request):
    # Busca todas as movimentações, ordenadas da mais recente para a mais antiga
    movimentacoes = Movimentacao.objects.select_related('produto').all().order_by('-data')
    return render(request, 'estoque/historico.html', {'movimentacoes': movimentacoes})

@login_required
def gerar_comprovante_pdf(request, pk):
    # Busca a movimentação específica pelo ID
    movimentacao = get_object_or_404(Movimentacao, pk=pk)
    
    # Cria um buffer de memória para o PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    
    # Desenhando o conteúdo do PDF
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, "Comprovante de Movimentacao de Estoque")
    
    p.setFont("Helvetica", 12)
    p.drawString(100, 760, f"ID da Movimentacao: #{movimentacao.id}")
    p.drawString(100, 740, f"Produto: {movimentacao.produto.nome} (SKU: {movimentacao.produto.sku})")
    p.drawString(100, 720, f"Tipo: {movimentacao.tipo}")
    p.drawString(100, 700, f"Quantidade: {movimentacao.quantidade} unidades")
    p.drawString(100, 680, f"Data/Hora: {movimentacao.data.strftime('%d/%m/%Y %H:%M')}")
    
    if movimentacao.observacao:
        p.drawString(100, 660, f"Observacao: {movimentacao.observacao}")
        
    p.drawString(100, 600, "____________________________________________________")
    p.drawString(100, 580, "StockFlow - Sistema de Controle de Estoque")
    
    # Fecha e salva o PDF
    p.showPage()
    p.save()
    buffer.seek(0)
    
    # Retorna o arquivo para download
    return FileResponse(buffer, as_attachment=True, filename=f'comprovante_{movimentacao.id}.pdf')

@login_required
def produto_editar(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    
    if request.method == 'POST':
        # Carrega o formulário com a instância do produto existente
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ProdutoForm(instance=produto)
        
    return render(request, 'estoque/produto_form.html', {'form': form, 'editando': True})

@login_required
def produto_deletar(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    
    if request.method == 'POST':
        produto.delete()
        return redirect('dashboard')
        
    return render(request, 'estoque/produto_confirmar_exclusao.html', {'produto': produto})

@login_required
def fornecedor_lista(request):
    # Lista todos os fornecedores em ordem alfabética pelo nome
    fornecedores = Fornecedor.objects.all().order_by('nome')
    return render(request, 'estoque/fornecedor_lista.html', {'fornecedores': fornecedores})

@login_required
def fornecedor_criar(request):
    if request.method == 'POST':
        form = FornecedorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('fornecedor_lista')
    else:
        form = FornecedorForm()
    
    return render(request, 'estoque/fornecedor_form.html', {'form': form})

@login_required
def fornecedor_editar(request, pk):
    fornecedor = get_object_or_404(Fornecedor, pk=pk)
    
    if request.method == 'POST':
        form = FornecedorForm(request.POST, instance=fornecedor)
        if form.is_valid():
            form.save()
            return redirect('fornecedor_lista')
    else:
        form = FornecedorForm(instance=fornecedor)
        
    return render(request, 'estoque/fornecedor_form.html', {'form': form, 'editando': True})

@login_required
def fornecedor_deletar(request, pk):
    fornecedor = get_object_or_404(Fornecedor, pk=pk)
    
    if request.method == 'POST':
        fornecedor.delete()
        return redirect('fornecedor_lista')
        
    return render(request, 'estoque/fornecedor_confirmar_exclusao.html', {'fornecedor': fornecedor})

@login_required
def relatorio_estoque_pdf(request):
    # Cria o buffer de memória
    buffer = io.BytesIO()
    
    # Configura o documento PDF com margens
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elementos = []
    
    # Estilos de texto
    estilos = getSampleStyleSheet()
    titulo = Paragraph("Relatório Geral de Estoque - StockFlow", estilos['Title'])
    elementos.append(titulo)
    elementos.append(Spacer(1, 20))
    
    # Busca os produtos e monta o cabeçalho da tabela
    produtos = Produto.objects.all().order_by('nome')
    dados_tabela = [['Produto', 'SKU', 'Qtd', 'Status']]
    
    # Preenche as linhas da tabela
    for p in produtos:
        if p.estoque_atual <= 0:
            status = "Esgotado"
        elif p.estoque_atual < p.estoque_minimo:
            status = "Baixo Estoque"
        else:
            status = "Em Estoque"
            
        dados_tabela.append([p.nome, p.sku, str(p.estoque_atual), status])
    
    # Configura o design da tabela
    tabela = Table(dados_tabela, colWidths=[220, 100, 80, 100])
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')), # Cabeçalho azul
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'), # Mantém o nome do produto alinhado à esquerda
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')), # Fundo cinza claro
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')), # Bordas
    ]))
    
    elementos.append(tabela)
    
    # Gera o PDF
    doc.build(elementos)
    buffer.seek(0)
    
    return FileResponse(buffer, as_attachment=True, filename=f"Relatorio_Estoque_{timezone.now().strftime('%d%m%Y')}.pdf")

@login_required
def relatorios_hub(request):
    return render(request, 'estoque/relatorios.html')

@login_required
def giro_estoque(request):
    # Anota o total de entradas e saídas diretamente no modelo de Produto (Top 10)
    produtos_giro = Produto.objects.annotate(
        total_entrada=Sum(
            Case(When(movimentacoes__tipo__icontains='e', then='movimentacoes__quantidade'), default=0, output_field=IntegerField())
        ),
        total_saida=Sum(
            Case(When(movimentacoes__tipo__icontains='s', then='movimentacoes__quantidade'), default=0, output_field=IntegerField())
        )
    ).filter(Q(total_entrada__gt=0) | Q(total_saida__gt=0)).order_by('-total_saida')[:10]

    # Prepara as listas para o Chart.js
    labels = [p.nome for p in produtos_giro]
    entradas_data = [p.total_entrada or 0 for p in produtos_giro]
    saidas_data = [p.total_saida or 0 for p in produtos_giro]

    context = {
        'labels_json': json.dumps(labels),
        'entradas_json': json.dumps(entradas_data),
        'saidas_json': json.dumps(saidas_data),
        'produtos': produtos_giro,
    }
    return render(request, 'estoque/giro_estoque.html', context)
