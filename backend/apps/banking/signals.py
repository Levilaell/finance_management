"""
Banking app signals for automatic processing
"""
from apps.categories.services import AICategorizationService
from django.db.models import F
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import BankAccount, Transaction


@receiver(post_save, sender=Transaction)
def process_new_transaction(sender, instance, created, **kwargs):
    """
    Process new transactions: categorize with AI and update account balance
    """
    if created:
        # Auto-categorize with AI if enabled
        if (instance.bank_account.company.enable_ai_categorization and 
            not instance.category and 
            not instance.is_ai_categorized):
            
            ai_service = AICategorizationService()
            ai_service.categorize_transaction(instance)
        
        # Update account balance if needed
        if instance.balance_after is None:
            # This would typically be handled by the banking sync
            pass


@receiver(pre_save, sender=BankAccount)
def update_primary_account(sender, instance, **kwargs):
    """
    Ensure only one primary account per company
    """
    if instance.is_primary:
        # Set all other accounts as non-primary
        BankAccount.objects.filter(
            company=instance.company,
            is_primary=True
        ).exclude(pk=instance.pk).update(is_primary=False)