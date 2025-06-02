"""
Banking app URLs
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .sandbox_views import (
    sandbox_status, sandbox_authorization_endpoint, 
    sandbox_token_endpoint, sandbox_accounts_endpoint, 
    sandbox_transactions_endpoint
)

app_name = 'banking'

router = DefaultRouter()
router.register(r'accounts', views.BankAccountViewSet, basename='bank-account')
router.register(r'transactions', views.TransactionViewSet, basename='transaction')
router.register(r'categories', views.TransactionCategoryViewSet, basename='category')
router.register(r'providers', views.BankProviderViewSet, basename='bank-provider')
router.register(r'budgets', views.BudgetViewSet, basename='budget')
router.register(r'goals', views.FinancialGoalViewSet, basename='financial-goal')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/enhanced/', views.EnhancedDashboardView.as_view(), name='enhanced-dashboard'),
    path('analytics/time-series/', views.TimeSeriesAnalyticsView.as_view(), name='time-series'),
    path('analytics/expense-trends/', views.ExpenseTrendsView.as_view(), name='expense-trends'),
    path('sync/<int:account_id>/', views.SyncBankAccountView.as_view(), name='sync-account'),
    path('connect/', views.ConnectBankAccountView.as_view(), name='connect-account'),
    path('oauth/callback/', views.OpenBankingCallbackView.as_view(), name='oauth-callback'),
    path('refresh-token/<int:account_id>/', views.RefreshTokenView.as_view(), name='refresh-token'),
    
    # Sandbox endpoints for realistic testing
    path('sandbox/status/', sandbox_status, name='sandbox-status'),
    path('sandbox/<str:bank_code>/oauth/authorize/', sandbox_authorization_endpoint, name='sandbox-auth'),
    path('sandbox/<str:bank_code>/oauth/token/', sandbox_token_endpoint, name='sandbox-token'),
    path('sandbox/<str:bank_code>/accounts/', sandbox_accounts_endpoint, name='sandbox-accounts'),
    path('sandbox/<str:bank_code>/accounts/<str:account_id>/transactions/', sandbox_transactions_endpoint, name='sandbox-transactions'),
]