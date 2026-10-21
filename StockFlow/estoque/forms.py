# estoque/forms.py
from django import forms
from .models import Produto, Fornecedor, Movimentacao

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'sku', 'fornecedor', 'preco_custo', 'preco_venda', 'estoque_minimo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Notebook Pro'}),
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código único'}),
            'fornecedor': forms.Select(attrs={'class': 'form-select'}),
            'preco_custo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'preco_venda': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estoque_minimo': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        
class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = ['nome', 'cnpj', 'telefone', 'email']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do fornecedor: Ex: ABC Distribuidora'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CNPJ do fornecedor'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefone do fornecedor'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email do fornecedor'}),
        }

class MovimentacaoForm(forms.ModelForm):
    class Meta:
        model = Movimentacao
        fields = ['produto', 'tipo', 'quantidade', 'observacao']
        widgets = {
            'produto': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Motivo da saída ou origem da entrada...'}),
        }