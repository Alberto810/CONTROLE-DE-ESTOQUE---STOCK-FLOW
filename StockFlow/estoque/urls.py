from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
]

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('produto/novo/', views.produto_criar, name='produto_criar'),
    path('movimentacao/nova/', views.movimentacao_criar, name='movimentacao_criar'),
    path('historico/', views.historico_movimentacoes, name='historico_movimentacoes'),
    path('comprovante/<int:pk>/', views.gerar_comprovante_pdf, name='gerar_comprovante_pdf'),
    path('produto/<int:pk>/editar/', views.produto_editar, name='produto_editar'),
    path('produto/<int:pk>/deletar/', views.produto_deletar, name='produto_deletar'),
    path('fornecedores/', views.fornecedor_lista, name='fornecedor_lista'),
    path('fornecedores/novo/', views.fornecedor_criar, name='fornecedor_criar'),
    path('fornecedores/<int:pk>/editar/', views.fornecedor_editar, name='fornecedor_editar'),
    path('fornecedores/<int:pk>/deletar/', views.fornecedor_deletar, name='fornecedor_deletar')
]    