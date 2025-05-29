"""
Banking app Celery tasks
Asynchronous tasks for bank synchronization and processing
"""
import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from .models import BankAccount, Company
from .services import BankingSyncService, FinancialInsightsService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def sync_bank_account(self, account_id, days_back=7):
    """
    Async task to sync individual bank account
    
    Args:
        account_id: BankAccount ID to sync
        days_back: Number of days to sync backwards
    """
    try:
        account = BankAccount.objects.get(id=account_id)
        sync_service = BankingSyncService()
        
        sync_log = sync_service.sync_account(account, days_back)
        
        logger.info(f"Bank account sync completed: {account} - {sync_log.transactions_new} new transactions")
        
        return {
            'status': 'success',
            'account_id': account_id,
            'sync_id': sync_log.id,
            'new_transactions': sync_log.transactions_new
        }
        
    except BankAccount.DoesNotExist:
        logger.error(f"Bank account {account_id} not found")
        return {'status': 'error', 'message': 'Account not found'}
        
    except Exception as exc:
        logger.error(f"Error syncing account {account_id}: {exc}")
        
        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        
        return {'status': 'error', 'message': str(exc)}


@shared_task
def sync_all_company_accounts(company_id):
    """
    Sync all accounts for a company
    
    Args:
        company_id: Company ID
    """
    try:
        company = Company.objects.get(id=company_id)
        sync_service = BankingSyncService()
        
        results = sync_service.sync_all_accounts(company)
        
        logger.info(f"Company sync completed: {company} - {len(results)} accounts processed")
        
        return {
            'status': 'success',
            'company_id': company_id,
            'results': results
        }
        
    except Company.DoesNotExist:
        logger.error(f"Company {company_id} not found")
        return {'status': 'error', 'message': 'Company not found'}
        
    except Exception as exc:
        logger.error(f"Error syncing company accounts {company_id}: {exc}")
        return {'status': 'error', 'message': str(exc)}


@shared_task
def periodic_account_sync():
    """
    Periodic task to sync all active accounts
    Runs every 4 hours via Celery Beat
    """
    active_accounts = BankAccount.objects.filter(
        is_active=True,
        status='active',
        company__subscription_status='active'
    )
    
    synced_count = 0
    error_count = 0
    
    for account in active_accounts:
        try:
            # Check if account needs sync based on frequency
            if account.last_sync_at:
                hours_since_sync = (timezone.now() - account.last_sync_at).total_seconds() / 3600
                if hours_since_sync < account.sync_frequency:
                    continue
            
            # Queue sync task
            sync_bank_account.delay(account.id)
            synced_count += 1
            
        except Exception as e:
            logger.error(f"Error queuing sync for account {account}: {e}")
            error_count += 1
    
    logger.info(f"Periodic sync queued: {synced_count} accounts, {error_count} errors")
    
    return {
        'queued': synced_count,
        'errors': error_count,
        'timestamp': timezone.now().isoformat()
    }


@shared_task
def generate_financial_insights(company_id):
    """
    Generate financial insights for a company
    
    Args:
        company_id: Company ID
    """
    try:
        company = Company.objects.get(id=company_id)
        insights_service = FinancialInsightsService()
        
        insights = insights_service.generate_insights(company)
        
        # Store insights in cache or database for dashboard
        # Implementation depends on your caching strategy
        
        logger.info(f"Financial insights generated for company: {company}")
        
        return {
            'status': 'success',
            'company_id': company_id,
            'insights': insights
        }
        
    except Company.DoesNotExist:
        logger.error(f"Company {company_id} not found")
        return {'status': 'error', 'message': 'Company not found'}
    
    except Exception as exc:
        logger.error(f"Error generating insights for company {company_id}: {exc}")
        return {'status': 'error', 'message': str(exc)}


@shared_task
def process_ai_categorization(transaction_id):
   """
   Process AI categorization for a transaction
   
   Args:
       transaction_id: Transaction ID to categorize
   """
   try:
       from apps.categories.services import AICategorizationService

       from .models import Transaction
       
       transaction = Transaction.objects.get(id=transaction_id)
       ai_service = AICategorizationService()
       
       result = ai_service.categorize_transaction(transaction)
       
       logger.info(f"AI categorization completed for transaction {transaction_id}: {result}")
       
       return {
           'status': 'success',
           'transaction_id': transaction_id,
           'category': result.get('category'),
           'confidence': result.get('confidence')
       }
       
   except Transaction.DoesNotExist:
       logger.error(f"Transaction {transaction_id} not found")
       return {'status': 'error', 'message': 'Transaction not found'}
       
   except Exception as exc:
       logger.error(f"Error processing AI categorization for transaction {transaction_id}: {exc}")
       return {'status': 'error', 'message': str(exc)}


@shared_task
def cleanup_old_sync_logs():
   """
   Clean up old bank sync logs (keep last 30 days)
   """
   from .models import BankSync
   
   cutoff_date = timezone.now() - timedelta(days=30)
   
   deleted_count = BankSync.objects.filter(
       started_at__lt=cutoff_date
   ).delete()[0]
   
   logger.info(f"Cleaned up {deleted_count} old sync logs")
   
   return {
       'status': 'success',
       'deleted_count': deleted_count,
       'cutoff_date': cutoff_date.isoformat()
   }


@shared_task
def send_low_balance_alerts():
   """
   Send alerts for accounts with low balance
   """
   from django.conf import settings
   from django.core.mail import send_mail
   
   low_balance_accounts = BankAccount.objects.filter(
       is_active=True,
       current_balance__lt=1000,  # Less than R$ 1000
       company__enable_notifications=True
   ).select_related('company', 'company__owner')
   
   alerts_sent = 0
   
   for account in low_balance_accounts:
       try:
           send_mail(
               subject=f'⚠️ Saldo Baixo - {account.display_name}',
               message=f'''
               Olá {account.company.owner.first_name},
               
               Sua conta {account.display_name} está com saldo baixo:
               Saldo atual: R$ {account.current_balance:,.2f}
               
               Recomendamos que verifique sua situação financeira.
               
               Atenciosamente,
               Equipe Caixa Digital
               ''',
               from_email=settings.DEFAULT_FROM_EMAIL,
               recipient_list=[account.company.owner.email],
               fail_silently=False,
           )
           alerts_sent += 1
           
       except Exception as e:
           logger.error(f"Error sending low balance alert for {account}: {e}")
   
   logger.info(f"Low balance alerts sent: {alerts_sent}")
   
   return {
       'status': 'success',
       'alerts_sent': alerts_sent
   }