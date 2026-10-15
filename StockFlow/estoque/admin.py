from django.contrib import admin
from .models import Fornecedor, Produto, Movimentacao

@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj', 'telefone', 'criado_em')
    search_fields = ('nome', 'cnpj')

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    # Mostra essas colunas na lista principal
    list_display = ('sku', 'nome', 'fornecedor', 'estoque_atual', 'preco_venda')
    search_fields = ('nome', 'sku')
    list_filter = ('fornecedor',)
    
    # Como colocamos editable=False no model, o Django já esconde o campo
    # estoque_atual do formulário de criação/edição. Isso garante a segurança!

@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    list_display = ('produto', 'tipo', 'quantidade', 'data')
    list_filter = ('tipo', 'data')
    search_fields = ('produto__nome', 'produto__sku')
    
    # Impede que movimentações antigas sejam alteradas (para manter a integridade)
    def has_change_permission(self, request, obj=None):
        return False