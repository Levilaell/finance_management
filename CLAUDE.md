# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Backend (Django)
```bash
cd backend

# Database operations
python manage.py migrate
python manage.py makemigrations
python manage.py shell

# Load initial data
python manage.py create_default_categories
python manage.py create_bank_providers  
python manage.py create_subscription_plans

# Run development server
python manage.py runserver

# Testing
python manage.py test
coverage run --source='.' manage.py test
coverage report
```

### Frontend (Next.js)
```bash
cd frontend

# Development
npm run dev
npm run build
npm run start
npm run lint

# Bundle analysis
npm run analyze  # If configured

# Testing
npm test
```

### Docker Operations
```bash
# Full stack development
docker-compose up -d
docker-compose logs -f
docker-compose down

# Production deployment
docker-compose -f docker-compose.production.yml up -d

# Execute commands in containers
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py shell
```

## Architecture Overview

### Backend Architecture (Django)
The backend follows a modular Django app structure with clear separation of concerns:

- **`apps/authentication/`**: Custom user model with 2FA support, JWT authentication
- **`apps/banking/`**: Core financial functionality - bank accounts, transactions, Open Banking integration
- **`apps/categories/`**: AI-powered transaction categorization using OpenAI GPT-3.5
- **`apps/companies/`**: Multi-tenant company management and subscription plans
- **`apps/notifications/`**: Real-time notifications via Django Channels/WebSockets
- **`apps/reports/`**: Financial reporting and analytics with Celery background tasks

Key architectural patterns:
- **Services layer**: Business logic separated from views (e.g., `banking/services.py`)
- **Signal-based automation**: Post-save signals trigger AI categorization and notifications
- **Async task processing**: Celery for bank synchronization and report generation
- **Multi-tenant design**: All financial data scoped by company

### Frontend Architecture (Next.js)
React-based SPA with modern patterns:

- **App Router**: Next.js 13+ app directory structure with route groups
- **State Management**: Zustand stores (`auth-store.ts`, `banking-store.ts`, `ui-store.ts`)
- **API Layer**: Centralized API client with authentication and error handling
- **Component System**: Radix UI + Tailwind CSS with custom UI components
- **Form Handling**: React Hook Form + Zod validation

### Open Banking Integration
Brazilian Open Finance compliance with multi-bank support:

- **Certificate-based authentication**: mTLS for bank API communication
- **Token management**: OAuth 2.0 flow with encrypted token storage
- **Transaction synchronization**: Background Celery tasks with deduplication
- **Mock integration**: Development-friendly bank simulation

### AI Categorization System
Intelligent transaction categorization:

- **OpenAI Integration**: GPT-3.5 Turbo for transaction analysis
- **Feature Engineering**: Automated extraction of transaction patterns
- **Learning System**: User feedback improves categorization accuracy
- **Fallback Logic**: Rule-based categorization when AI is unavailable

## Critical Configuration

### Environment Variables (Backend)
```env
# Security (NEVER use defaults in production)
SECRET_KEY=your-secret-key-here
DEBUG=False

# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# Redis
REDIS_URL=redis://localhost:6379/0

# OpenAI
OPENAI_API_KEY=sk-...

# Open Banking certificates
OPEN_FINANCE_CLIENT_CERT_PATH=/path/to/client.crt
OPEN_FINANCE_CLIENT_KEY_PATH=/path/to/client.key
```

### Database Considerations
- **PostgreSQL required**: Financial precision requires proper DECIMAL handling
- **Indexes needed**: Transaction queries are heavy - ensure proper indexing
- **Migrations**: Financial data migrations must be reversible and safe

### Security Requirements
- **Token encryption**: All banking tokens must be encrypted at rest
- **Certificate management**: mTLS certificates for Open Banking compliance
- **Rate limiting**: All external API calls must be rate-limited
- **Audit logging**: Financial operations require comprehensive logging

## Key Business Logic

### Transaction Processing Flow
1. **Bank sync** triggers via Celery tasks (`banking/tasks.py`)
2. **Deduplication** by external_id and transaction fingerprint
3. **AI categorization** via OpenAI API with company-specific context
4. **Balance calculation** with proper decimal precision
5. **Real-time notifications** via WebSockets

### Financial Calculations
- **Use Decimal, never float** for monetary values
- **Brazilian currency format**: R$ with comma decimal separator
- **Tax considerations**: Categories support tax-deductible flagging
- **Multi-currency**: Designed for BRL but extensible

### Multi-tenancy
- **Company isolation**: All queries must filter by company
- **User-company relationship**: Users belong to companies, not global
- **Data separation**: Strict isolation between companies

## Performance Considerations

### Database Optimization
- **Query optimization**: Use select_related/prefetch_related for dashboard
- **Aggregation queries**: Monthly/yearly summaries need optimization
- **Transaction indexes**: Critical for filtering large datasets

### Caching Strategy
- **Redis caching**: Dashboard data and frequent aggregations
- **API response caching**: Bank provider lists and categories
- **Query result caching**: Expensive financial calculations

### Background Processing
- **Celery tasks**: Bank synchronization, report generation, email sending
- **Rate limiting**: External API calls (banks, OpenAI) must respect limits
- **Error handling**: Robust retry logic for financial operations

## Development Notes

### Testing Financial Logic
- **Decimal precision**: All monetary calculations must use Decimal
- **Transaction scenarios**: Test duplicate handling, rollbacks, failures
- **Multi-company**: Ensure data isolation in tests
- **Mock external APIs**: Bank APIs and OpenAI for reliable testing

### Code Quality Requirements
- **Type hints**: Required for all service layer functions
- **Error handling**: Financial operations need comprehensive error handling
- **Logging**: All financial operations must be logged for audit
- **Documentation**: Complex financial logic requires docstrings

### Security Best Practices
- **Input validation**: All financial inputs must be validated/sanitized
- **Permission checks**: Company-scoped permissions on all views
- **Token handling**: Never log or expose financial tokens
- **SSL/TLS**: All external communications must use TLS

## Production Deployment

### Database Requirements
- **PostgreSQL 13+** with proper connection pooling
- **Backup strategy**: Automated backups with point-in-time recovery
- **Read replicas**: For reporting queries at scale

### Infrastructure
- **Redis cluster**: For cache and Celery broker
- **Celery workers**: Separate workers for different task types
- **Load balancing**: Multiple Django instances behind nginx
- **File storage**: S3-compatible for document storage

### Monitoring Requirements
- **Financial metrics**: Transaction volume, categorization accuracy
- **Performance monitoring**: Database query performance, API response times
- **Error tracking**: Sentry integration for error monitoring
- **Business metrics**: Dashboard for financial insights

## Common Issues

### OpenAI API Updates
The current implementation uses deprecated OpenAI API patterns. When updating:
- Replace `openai.ChatCompletion.create()` with `openai.OpenAI().chat.completions.create()`
- Update authentication to use API client initialization
- Test categorization accuracy after API changes

### Banking Integration Failures
- **Certificate expiry**: Monitor Open Banking certificate validity
- **API rate limits**: Implement exponential backoff for bank API calls
- **Token refresh**: Handle OAuth token expiry gracefully

### Performance Issues
- **N+1 queries**: Common in dashboard and transaction lists
- **Large datasets**: Implement pagination for transaction queries
- **Memory usage**: Monitor AI categorization memory consumption