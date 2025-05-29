"""
Banking app URLs
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'banking'

router = DefaultRouter()
router.register(r'accounts', views.BankAccountViewSet, basename='bank-account')
router.register(r'transactions', views.TransactionViewSet, basename='transaction')
router.register(r'categories', views.TransactionCategoryViewSet, basename='category')
router.register(r'providers', views.BankProviderViewSet, basename='bank-provider')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('sync/<int:account_id>/', views.SyncBankAccountView.as_view(), name='sync-account'),
    path('connect/', views.ConnectBankAccountView.as_view(), name='connect-account'),
]