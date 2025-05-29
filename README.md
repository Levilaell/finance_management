# Caixa Digital - Financial SaaS Platform

Sistema de gestão financeira inteligente para pequenas e médias empresas brasileiras.

## 🚀 Tecnologias

- **Backend**: Django 5.0, Django REST Framework
- **Database**: PostgreSQL
- **Cache/Queue**: Redis
- **Task Queue**: Celery
- **AI**: OpenAI API para categorização inteligente
- **Autenticação**: JWT (djangorestframework-simplejwt)

## 📋 Pré-requisitos

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Conta na OpenAI (opcional, para AI categorization)

## 🛠️ Instalação

### Opção 1: Setup Local

1. **Clone o repositório**
   ```bash
   git clone https://github.com/seu-usuario/caixa-digital.git
   cd caixa-digital
   ```

2. **Configure o ambiente**
   ```bash
   # Copie o arquivo de exemplo
   cp backend/.env.example backend/.env
   
   # Edite o arquivo .env com suas credenciais
   ```

3. **Crie e ative o ambiente virtual**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate  # Windows
   ```

4. **Instale as dependências**
   ```bash
   pip install -r backend/requirements.txt
   ```

5. **Configure o banco de dados**
   ```bash
   # Crie o banco de dados no PostgreSQL
   createdb caixa_digital
   
   # Execute as migrações
   cd backend
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Carregue os dados iniciais**
   ```bash
   python manage.py create_subscription_plans
   python manage.py create_bank_providers
   python manage.py create_default_categories
   ```

7. **Crie um superusuário**
   ```bash
   python manage.py createsuperuser
   ```

8. **Inicie o servidor**
   ```bash
   python manage.py runserver
   ```

### Opção 2: Setup com Docker

1. **Clone o repositório**
   ```bash
   git clone https://github.com/seu-usuario/caixa-digital.git
   cd caixa-digital
   ```

2. **Configure o ambiente**
   ```bash
   cp backend/.env.example backend/.env
   ```

3. **Inicie os containers**
   ```bash
   docker-compose up -d
   ```

4. **Execute as migrações**
   ```bash
   docker-compose exec backend python manage.py migrate
   ```

5. **Carregue os dados iniciais**
   ```bash
   docker-compose exec backend python manage.py create_subscription_plans
   docker-compose exec backend python manage.py create_bank_providers
   docker-compose exec backend python manage.py create_default_categories
   ```

6. **Crie um superusuário**
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

## 📊 Estrutura do Projeto

```
caixa-digital/
├── backend/
│   ├── apps/
│   │   ├── authentication/    # Autenticação e usuários
│   │   ├── banking/          # Contas bancárias e transações
│   │   ├── categories/       # Categorização com AI
│   │   ├── companies/        # Empresas e assinaturas
│   │   ├── notifications/    # Sistema de notificações
│   │   └── reports/          # Relatórios financeiros
│   ├── core/                 # Configurações do Django
│   └── manage.py
├── docker-compose.yml
└── README.md
```

## 🔑 Funcionalidades Principais

- **Open Banking**: Integração com bancos brasileiros
- **Categorização Inteligente**: AI para categorizar transações automaticamente
- **Dashboard Financeiro**: Visão geral das finanças em tempo real
- **Relatórios**: Análises e insights financeiros
- **Multi-usuário**: Suporte para equipes (plano Enterprise)
- **API REST**: Integração com outros sistemas

## 🧪 Testes

```bash
# Execute os testes
cd backend
python manage.py test

# Com coverage
coverage run --source='.' manage.py test
coverage report
```

## 📝 API Documentation

Após iniciar o servidor, acesse:
- Admin: http://localhost:8000/admin/
- API: http://localhost:8000/api/

### Endpoints principais:

- `POST /api/auth/login/` - Autenticação
- `GET /api/banking/accounts/` - Listar contas bancárias
- `GET /api/banking/transactions/` - Listar transações
- `POST /api/banking/sync/<account_id>/` - Sincronizar conta
- `GET /api/banking/dashboard/` - Dashboard financeiro

## 🚀 Deploy

Para deploy em produção, recomendamos:

1. **Servidor**: AWS EC2, DigitalOcean, ou Heroku
2. **Database**: AWS RDS PostgreSQL
3. **Cache/Queue**: AWS ElastiCache Redis
4. **Storage**: AWS S3 para arquivos estáticos
5. **CDN**: CloudFront

## 📄 Licença

Este projeto é proprietário e confidencial.

## 👥 Equipe

- Desenvolvido por [Sua Empresa]

## 📞 Suporte

Para suporte, envie um email para suporte@caixadigital.com.br