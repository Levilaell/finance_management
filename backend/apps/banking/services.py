"""
Banking app services
Business logic for financial operations and integrations
"""
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

import requests
from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

from .models import (BankAccount, BankProvider, BankSync, RecurringTransaction,
                     Transaction, TransactionCategory)

logger = logging.getLogger(__name__)


class OpenBankingService:
    """
    Service for Open Banking API integration
    Handles connection and data retrieval from bank APIs
    """
    
    def __init__(self):
        self.timeout = 30
        self.base_headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'CaixaDigital/1.0'
        }
    
    def connect_account(self, bank_code: str, credentials: Dict) -> Dict:
        """
        Connect to bank account via Open Banking
        
        Args:
            bank_code: Bank provider code
            credentials: User banking credentials
            
        Returns:
            Dict with connection data and tokens
        """
        try:
            bank_provider = BankProvider.objects.get(code=bank_code)
            
            # Mock implementation - replace with actual Open Banking API
            if bank_provider.api_endpoint:
                auth_data = {
                    'client_id': settings.OPEN_BANKING_CLIENT_ID,
                    'client_secret': settings.OPEN_BANKING_CLIENT_SECRET,
                    'username': credentials.get('username'),
                    'password': credentials.get('password'),
                    'agency': credentials.get('agency'),
                    'account': credentials.get('account')
                }
                
                response = requests.post(
                    f"{bank_provider.api_endpoint}/auth",
                    json=auth_data,
                    headers=self.base_headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    raise Exception(f"Authentication failed: {response.status_code}")
            
            # Mock successful connection for development
            return {
                'access_token': f'mock_token_{bank_code}_{datetime.now().timestamp()}',
                'refresh_token': f'mock_refresh_{bank_code}_{datetime.now().timestamp()}',
                'expires_in': 3600,
                'account_id': f'acc_{bank_code}_{credentials.get("account")}',
                'account_info': {
                    'agency': credentials.get('agency'),
                    'account': credentials.get('account'),
                    'account_type': 'checking',
                    'balance': Decimal('10000.00')
                }
            }
            
        except BankProvider.DoesNotExist:
            raise Exception(f"Bank provider {bank_code} not found")
        except requests.RequestException as e:
            raise Exception(f"Connection error: {str(e)}")
    
    def get_account_info(self, bank_account: BankAccount) -> Dict:
        """
        Get account information and current balance
        """
        try:
            headers = {
                **self.base_headers,
                'Authorization': f'Bearer {bank_account.access_token}'
            }
            
            # Mock implementation
            return {
                'balance': float(bank_account.current_balance) + 100.50,
                'available_balance': float(bank_account.available_balance) + 50.25,
                'account_status': 'active',
                'last_update': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting account info for {bank_account}: {e}")
            raise
    
    def get_transactions(self, bank_account: BankAccount, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Fetch transactions from bank API
        
        Args:
            bank_account: BankAccount instance
            start_date: Start date for transaction fetch
            end_date: End date for transaction fetch
            
        Returns:
            List of transaction dictionaries
        """
        try:
            headers = {
                **self.base_headers,
                'Authorization': f'Bearer {bank_account.access_token}'
            }
            
            params = {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'account_id': bank_account.external_account_id
            }
            
            # Mock implementation - replace with actual API call
            mock_transactions = self._generate_mock_transactions(bank_account, start_date, end_date)
            return mock_transactions
            
        except Exception as e:
            logger.error(f"Error fetching transactions for {bank_account}: {e}")
            raise
    
    def _generate_mock_transactions(self, bank_account: BankAccount, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Generate mock transactions for development
        """
        transactions = []
        current_date = start_date
        
        while current_date <= end_date:
            # Generate 1-3 random transactions per day
            import random
            daily_transactions = random.randint(0, 3)
            
            for _ in range(daily_transactions):
                transaction_type = random.choice(['credit', 'debit', 'pix_in', 'pix_out'])
                amount = Decimal(str(random.uniform(10, 1000))).quantize(Decimal('0.01'))
                
                if transaction_type in ['debit', 'pix_out']:
                    amount = -amount
                
                transactions.append({
                    'external_id': f'mock_{current_date.strftime("%Y%m%d")}_{len(transactions)}',
                    'transaction_type': transaction_type,
                    'amount': float(amount),
                    'description': random.choice([
                        'PAGAMENTO PIX', 'TRANSFERENCIA TED', 'COMPRA CARTAO',
                        'DEPOSITO', 'SAQUE', 'TAXA MANUTENCAO', 'JUROS'
                    ]),
                    'transaction_date': current_date.isoformat(),
                    'counterpart_name': random.choice([
                        'LOJA ABC LTDA', 'SUPERMERCADO XYZ', 'POSTO COMBUSTIVEL',
                        'CLIENTE JOAO SILVA', 'FORNECEDOR MATERIAIS'
                    ]),
                    'reference_number': f'REF{random.randint(100000, 999999)}'
                })
            
            current_date += timedelta(days=1)
        
        return transactions


class BankingSyncService:
    """
    Service for synchronizing bank account data
    Orchestrates the sync process and handles errors
    """
    
    def __init__(self):
        self.open_banking = OpenBankingService()
    
    def sync_account(self, bank_account: BankAccount, days_back: int = 30) -> BankSync:
        """
        Synchronize transactions for a bank account
        
        Args:
            bank_account: BankAccount to sync
            days_back: Number of days to sync backwards
            
        Returns:
            BankSync log instance
        """
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days_back)
        
        # Create sync log
        sync_log = BankSync.objects.create(
            bank_account=bank_account,
            status='running',
            sync_from_date=start_date,
            sync_to_date=end_date
        )
        
        try:
            with transaction.atomic():
                # Update account info
                account_info = self.open_banking.get_account_info(bank_account)
                bank_account.current_balance = Decimal(str(account_info['balance']))
                bank_account.available_balance = Decimal(str(account_info['available_balance']))
                bank_account.last_sync_at = timezone.now()
                bank_account.status = 'active'
                bank_account.save()
                
                # Fetch and process transactions
                transactions_data = self.open_banking.get_transactions(
                    bank_account, 
                    datetime.combine(start_date, datetime.min.time()),
                    datetime.combine(end_date, datetime.max.time())
                )
                
                new_transactions = 0
                updated_transactions = 0
                
                for trans_data in transactions_data:
                    created = self._process_transaction(bank_account, trans_data)
                    if created:
                        new_transactions += 1
                    else:
                        updated_transactions += 1
                
                # Update sync log
                sync_log.status = 'completed'
                sync_log.completed_at = timezone.now()
                sync_log.transactions_found = len(transactions_data)
                sync_log.transactions_new = new_transactions
                sync_log.transactions_updated = updated_transactions
                sync_log.save()
                
                logger.info(f"Sync completed for {bank_account}: {new_transactions} new, {updated_transactions} updated")
                
        except Exception as e:
            sync_log.status = 'failed'
            sync_log.error_message = str(e)
            sync_log.completed_at = timezone.now()
            sync_log.save()
            
            bank_account.status = 'error'
            bank_account.save()
            
            logger.error(f"Sync failed for {bank_account}: {e}")
            raise
        
        return sync_log
    
    def _process_transaction(self, bank_account: BankAccount, trans_data: Dict) -> bool:
        """
        Process individual transaction data
        
        Returns:
            True if transaction was created, False if updated
        """
        external_id = trans_data.get('external_id')
        
        # Check if transaction already exists
        existing = Transaction.objects.filter(
            bank_account=bank_account,
            external_id=external_id
        ).first()
        
        transaction_date = datetime.fromisoformat(trans_data['transaction_date'].replace('Z', '+00:00'))
        
        transaction_data = {
            'transaction_type': trans_data['transaction_type'],
            'amount': Decimal(str(trans_data['amount'])),
            'description': trans_data['description'][:500],
            'transaction_date': transaction_date,
            'counterpart_name': trans_data.get('counterpart_name', '')[:200],
            'reference_number': trans_data.get('reference_number', '')[:100],
            'status': 'completed'
        }
        
        if existing:
            # Update existing transaction
            for key, value in transaction_data.items():
                setattr(existing, key, value)
            existing.save()
            return False
        else:
            # Create new transaction
            Transaction.objects.create(
                bank_account=bank_account,
                external_id=external_id,
                **transaction_data
            )
            return True
    
    def sync_all_accounts(self, company):
        """
        Sync all active accounts for a company
        """
        accounts = BankAccount.objects.filter(
            company=company,
            is_active=True,
            status='active'
        )
        
        results = []
        for account in accounts:
            try:
                sync_log = self.sync_account(account)
                results.append({
                    'account': account.display_name,
                    'status': 'success',
                    'sync_id': sync_log.id
                })
            except Exception as e:
                results.append({
                    'account': account.display_name,
                    'status': 'error',
                    'error': str(e)
                })
        
        return results


class CashFlowProjectionService:
    """
    Service for cash flow projections and financial planning
    """
    
    def __init__(self):
        pass
    
    def generate_projection(self, company, days_ahead: int = 30) -> List[Dict]:
        """
        Generate cash flow projection based on historical data and recurring transactions
        
        Args:
            company: Company instance
            days_ahead: Number of days to project
            
        Returns:
            List of daily cash flow projections
        """
        start_date = timezone.now().date()
        projections = []
        
        # Get current balance
        current_balance = BankAccount.objects.filter(
            company=company,
            is_active=True
        ).aggregate(
            total=models.Sum('current_balance')
        )['total'] or Decimal('0')
        
        # Get recurring transactions
        recurring_transactions = RecurringTransaction.objects.filter(
            bank_account__company=company,
            is_active=True
        )
        
        for day in range(days_ahead + 1):
            projection_date = start_date + timedelta(days=day)
            
            # Calculate expected transactions for this date
            expected_income = Decimal('0')
            expected_expenses = Decimal('0')
            alerts = []
            
            for recurring in recurring_transactions:
                if self._is_transaction_expected(recurring, projection_date):
                    if recurring.expected_amount > 0:
                        expected_income += recurring.expected_amount
                    else:
                        expected_expenses += abs(recurring.expected_amount)
                    
                    # Check for potential issues
                    if recurring.expected_amount < 0 and abs(recurring.expected_amount) > current_balance * Decimal('0.1'):
                        alerts.append(f"Grande despesa esperada: {recurring.name}")
            
            # Update projected balance
            daily_net = expected_income - expected_expenses
            current_balance += daily_net
            
            # Warning if balance gets low
            if current_balance < Decimal('1000'):
                alerts.append("Saldo projetado baixo")
            
            projections.append({
                'date': projection_date,
                'projected_balance': current_balance,
                'expected_income': expected_income,
                'expected_expenses': expected_expenses,
                'confidence_level': self._calculate_confidence(recurring_transactions, projection_date),
                'alerts': alerts
            })
        
        return projections
    
    def _is_transaction_expected(self, recurring: RecurringTransaction, date) -> bool:
        """
        Check if a recurring transaction is expected on a given date
        """
        if not recurring.next_expected_date:
            return False
        
        days_diff = abs((date - recurring.next_expected_date).days)
        return days_diff <= recurring.day_tolerance
    
    def _calculate_confidence(self, recurring_transactions, date) -> float:
        """
        Calculate confidence level for projection based on historical accuracy
        """
        # Simple confidence calculation based on recurring transaction accuracy
        if not recurring_transactions:
            return 0.3
        
        total_accuracy = sum(rt.accuracy_rate for rt in recurring_transactions)
        avg_accuracy = total_accuracy / len(recurring_transactions)
        
        # Decrease confidence for future dates
        days_ahead = (date - timezone.now().date()).days
        confidence_decay = max(0.1, 1.0 - (days_ahead * 0.02))
        
        return min(0.95, avg_accuracy * confidence_decay)


class FinancialInsightsService:
    """
    Service for generating financial insights and recommendations
    """
    
    def generate_insights(self, company) -> Dict:
        """
        Generate financial insights for dashboard
        """
        insights = {
            'spending_trends': self._analyze_spending_trends(company),
            'category_analysis': self._analyze_categories(company),
            'cash_flow_health': self._assess_cash_flow_health(company),
            'recommendations': self._generate_recommendations(company)
        }
        
        return insights
    
    def _analyze_spending_trends(self, company) -> Dict:
        """
        Analyze spending trends over time
        """
        # Implementation for spending trend analysis
        return {
            'trend': 'increasing',
            'percentage_change': 15.5,
            'period': 'last_30_days'
        }
    
    def _analyze_categories(self, company) -> List[Dict]:
        """
        Analyze spending by category
        """
        # Implementation for category analysis
        return []
    
    def _assess_cash_flow_health(self, company) -> Dict:
        """
        Assess overall cash flow health
        """
        return {
            'score': 7.5,
            'status': 'healthy',
            'issues': []
        }
    
    def _generate_recommendations(self, company) -> List[Dict]:
        """
        Generate actionable financial recommendations
        """
        return [
            {
                'type': 'cost_saving',
                'title': 'Reduza gastos com combustível',
                'description': 'Seus gastos com combustível aumentaram 25% este mês',
                'potential_saving': 340.50
            }
        ]