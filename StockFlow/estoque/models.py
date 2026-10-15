from django.db import models
from django.core.exceptions import ValidationError

class Fornecedor(models.Model):
    nome = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18, unique=True, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

class Produto(models.Model):
    nome = models.CharField(max_length=255)
    sku = models.CharField(max_length=50, unique=True, help_text="Código único do produto")
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.SET_NULL, null=True, blank=True, related_name='produtos')
    preco_custo = models.DecimalField(max_digits=10, decimal_places=2)
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2)
    estoque_minimo = models.PositiveIntegerField(default=5)
    estoque_atual = models.IntegerField(default=0, editable=False) # Não editável manualmente!
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sku} - {self.nome}"

class Movimentacao(models.Model):
    TIPO_CHOICES = (
        ('ENTRADA', 'Entrada (Compra/Devolução)'),
        ('SAIDA', 'Saída (Venda/Perda)'),
    )
    
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='movimentacoes')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    quantidade = models.PositiveIntegerField()
    data = models.DateTimeField(auto_now_add=True)
    observacao = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Verifica se é uma nova movimentação antes de salvar
        is_new = self.pk is None 
        
        if is_new:
            # Regra de negócio: impede saída se não houver estoque suficiente
            if self.tipo == 'SAIDA' and self.produto.estoque_atual < self.quantidade:
                raise ValidationError(f"Estoque insuficiente. O produto {self.produto.nome} tem apenas {self.produto.estoque_atual} unidades.")
            
            # Atualiza o estoque do produto
            if self.tipo == 'ENTRADA':
                self.produto.estoque_atual += self.quantidade
            elif self.tipo == 'SAIDA':
                self.produto.estoque_atual -= self.quantidade
                
            self.produto.save()
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.produto.nome} - {self.tipo} ({self.quantidade})"