"""
Banking app views
Financial dashboard and transaction management
"""
from datetime import datetime, timedelta
from decimal import Decimal

from django.db.models import Count, Q, Sum
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import BankAccount, BankProvider, Transaction, TransactionCategory
from .serializers import (BankAccountSerializer, BankProviderSerializer,
                          DashboardSerializer, TransactionCategorySerializer,
                          TransactionSerializer)
from .services import BankingSyncService


class BankAccountViewSet(viewsets.ModelViewSet):
    """
    Bank account management
    """
    serializer_class = BankAccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return BankAccount.objects.filter(
            company=self.request.user.company
        ).select_related('bank_provider')
    
    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """Sync transactions for specific account"""
        account = self.get_object()
        sync_service = BankingSyncService()
        
        try:
            result = sync_service.sync_account(account)
            return Response({
                'status': 'success',
                'message': 'Sincronização iniciada',
                'sync_id': result.id
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class TransactionViewSet(viewsets.ModelViewSet):
    """
    Transaction management and filtering
    """
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['category', 'transaction_type', 'bank_account']
    search_fields = ['description', 'counterpart_name']
    ordering_fields = ['transaction_date', 'amount']
    ordering = ['-transaction_date']
    
    def get_queryset(self):
        return Transaction.objects.filter(
            bank_account__company=self.request.user.company
        ).select_related(
            'bank_account', 
            'category', 
            'subcategory'
        )
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get transaction summary for dashboard"""
        queryset = self.get_queryset()
        
        # Date filtering
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(transaction_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(transaction_date__lte=end_date)
        
        # Calculate summary
        income = queryset.filter(
            transaction_type__in=['credit', 'transfer_in', 'pix_in']
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        expenses = queryset.filter(
            transaction_type__in=['debit', 'transfer_out', 'pix_out', 'fee']
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        return Response({
            'income': income,
            'expenses': abs(expenses),
            'net': income - abs(expenses),
            'transaction_count': queryset.count()
        })


class TransactionCategoryViewSet(viewsets.ModelViewSet):
    """
    Transaction category management
    """
    serializer_class = TransactionCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return TransactionCategory.objects.filter(
            Q(is_system=True) | Q(company=self.request.user.company)
        )


class BankProviderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Available bank providers
    """
    serializer_class = BankProviderSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = BankProvider.objects.filter(is_active=True)


class DashboardView(APIView):
    """
    Main financial dashboard data
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        company = request.user.company
        
        # Get current month data
        now = timezone.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get all company accounts
        accounts = BankAccount.objects.filter(company=company, is_active=True)
        
        # Current balances
        total_balance = accounts.aggregate(
            total=Sum('current_balance')
        )['total'] or Decimal('0')
        
        # This month transactions
        transactions = Transaction.objects.filter(
            bank_account__in=accounts,
            transaction_date__gte=start_of_month
        )
        
        # Income and expenses this month
        income = transactions.filter(
            transaction_type__in=['credit', 'transfer_in', 'pix_in']
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        expenses = transactions.filter(
            transaction_type__in=['debit', 'transfer_out', 'pix_out', 'fee']
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Recent transactions
        recent_transactions = Transaction.objects.filter(
            bank_account__in=accounts
        ).select_related('category', 'bank_account')[:10]
        
        # Top categories this month
        top_categories = transactions.filter(
            category__isnull=False
        ).values(
            'category__name', 
            'category__icon'
        ).annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')[:5]
        
        data = {
            'current_balance': total_balance,
            'monthly_income': income,
            'monthly_expenses': abs(expenses),
            'monthly_net': income - abs(expenses),
            'recent_transactions': TransactionSerializer(recent_transactions, many=True).data,
            'top_categories': top_categories,
            'accounts_count': accounts.count(),
            'transactions_count': transactions.count(),
        }
        
        return Response(data)


class ConnectBankAccountView(APIView):
    """
    Initiate bank account connection via Open Banking
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        bank_code = request.data.get('bank_code')
        account_type = request.data.get('account_type')
        
        if not bank_code:
            return Response({
                'error': 'bank_code é obrigatório'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            bank_provider = BankProvider.objects.get(code=bank_code, is_active=True)
        except BankProvider.DoesNotExist:
            return Response({
                'error': 'Banco não encontrado ou não suportado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Here you would integrate with Open Banking API
        # For now, return a mock response
        return Response({
            'status': 'success',
            'message': 'Redirecionando para autenticação bancária',
            'auth_url': f'https://openbanking.{bank_provider.code}.com.br/auth',
            'bank_name': bank_provider.name
        })


class SyncBankAccountView(APIView):
    """
    Manually trigger bank account sync
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, account_id):
        try:
            account = BankAccount.objects.get(
                id=account_id,
                company=request.user.company
            )
        except BankAccount.DoesNotExist:
            return Response({
                'error': 'Conta não encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        
        sync_service = BankingSyncService()
        
        try:
            sync_log = sync_service.sync_account(account)
            return Response({
                'status': 'success',
                'message': 'Sincronização iniciada',
                'sync_id': sync_log.id
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)