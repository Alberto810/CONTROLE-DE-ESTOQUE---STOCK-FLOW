# 📦 StockFlow - Sistema de Controle de Estoque

O StockFlow é um sistema web robusto e responsivo desenvolvido em Django para o gerenciamento eficiente de estoque. Ele permite acompanhar produtos, fornecedores, entradas e saídas, gerando relatórios em PDF e gráficos interativos para auxiliar na tomada de decisão.

## ✨ Funcionalidades Principais

Dashboard Interativo: Visão geral com KPIs importantes (total de itens, produtos em alerta, movimentações do dia).

Gestão de Produtos: CRUD completo, controle de SKU, estoque mínimo e status em tempo real (Em Estoque, Baixo Estoque, Esgotado).

Gestão de Fornecedores: Cadastro e gerenciamento de empresas parceiras.

Controle de Movimentações: Registro de entradas e saídas de mercadorias.

Filtros e Paginação: Busca dinâmica por texto (Nome/SKU) e filtros de acesso rápido por status.

Central de Relatórios: Geração automática de relatórios de estoque geral em formato PDF.

Giro de Estoque: Análise visual (via gráficos de barras comparativas) das mercadorias com maior fluxo de entrada e saída.

Alertas Críticos: Painel inteligente que destaca imediatamente os produtos que precisam de reposição.

Design Responsivo: Interface mobile-first, garantindo usabilidade perfeita em celulares, tablets e desktops.

## 🛠️ Tecnologias Utilizadas

Back-end: Python, Django (v6.x)

Front-end: HTML5, CSS3, Bootstrap 5, JavaScript

Gráficos: Chart.js

Geração de PDF: ReportLab

Hospedagem / Deploy: Vercel (com WhiteNoise para arquivos estáticos)

Banco de Dados: SQLite (Desenvolvimento) / PostgreSQL (Produção - opcional)

## 🚀 Como Executar o Projeto Localmente

Siga os passos abaixo para rodar o projeto na sua máquina:

### 1. Clone o repositório

git clone https://github.com/SEU_USUARIO/stock-flow.git
cd stock-flow


### 2. Crie e ative o Ambiente Virtual

### Windows
python -m venv .venv
.venv\Scripts\activate

### Linux/Mac
python3 -m venv .venv
source .venv/bin/activate


### 3. Instale as dependências

pip install -r requirements.txt


(Caso não tenha um requirements.txt, certifique-se de instalar: django, reportlab, whitenoise)

### 4. Execute as migrações do Banco de Dados

python manage.py makemigrations
python manage.py migrate


### 5. Crie um superusuário (Administrador)

python manage.py createsuperuser


### 6. Inicie o Servidor Local

python manage.py runserver


O sistema estará disponível em: http://127.0.0.1:8000/

## 🌐 Deploy na Vercel

O projeto está configurado para deploy fácil na Vercel. Certifique-se de que o seu arquivo settings.py possui as seguintes configurações de segurança e estáticos:

ALLOWED_HOSTS = ['.vercel.app', 'localhost', '127.0.0.1']

Configuração do WhiteNoise no MIDDLEWARE.

## 📄 Licença

Este projeto é de código aberto e está disponível sob a licença MIT.