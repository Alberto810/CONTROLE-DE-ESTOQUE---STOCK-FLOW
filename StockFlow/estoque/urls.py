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
]