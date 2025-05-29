"""
Banking and financial transaction models
Core financial data handling with AI categorization support
"""
import uuid
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class BankProvider(models.Model):
    """
    Supported bank providers for Open Banking integration
    """
    name = models.CharField(_('bank name'), max_length=100)
    code = models.CharField(_('bank code'), max_length=10, unique=True)
    logo = models.ImageField(_('logo'), upload_to='bank_logos/', blank=True, null=True)
    color = models.CharField(_('brand color'), max_length=7, default='#000000')
    is_open_banking = models.BooleanField(_('supports Open Banking'), default=True)
    api_endpoint = models.URLField(_('API endpoint'), blank=True)
    is_active = models.BooleanField(_('is active'), default=True)
    
    # Integration settings
    requires_agency = models.BooleanField(_('requires agency'), default=True)
    requires_account = models.BooleanField(_('requires account'), default=True)
    supports_pix = models.BooleanField(_('supports PIX'), default=True)
    supports_ted = models.BooleanField(_('supports TED'), default=True)
    supports_doc = models.BooleanField(_('supports DOC'), default=True)
    
    class Meta:
        db_table = 'bank_providers'
        verbose_name = _('Bank Provider')
        verbose_name_plural = _('Bank Providers')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class BankAccount(models.Model):
    """
    Company bank accounts connected via Open Banking
    """
    ACCOUNT_TYPES = [
        ('checking', 'Conta Corrente'),
        ('savings', 'Conta Poupança'),
        ('business', 'Conta Empresarial'),
        ('digital', 'Conta Digital'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Ativa'),
        ('inactive', 'Inativa'),
        ('pending', 'Pendente'),
        ('error', 'Erro de Conexão'),
        ('expired', 'Token Expirado'),
    ]
    
    # Basic information
    company = models.ForeignKey(
        'companies.Company', 
        on_delete=models.CASCADE, 
        related_name='bank_accounts'
    )
    bank_provider = models.ForeignKey(BankProvider, on_delete=models.PROTECT)
    
    # Account details
    account_type = models.CharField(_('account type'), max_length=20, choices=ACCOUNT_TYPES)
    agency = models.CharField(_('agency'), max_length=10)
    account_number = models.CharField(_('account number'), max_length=20)
    account_digit = models.CharField(_('account digit'), max_length=2, blank=True)
    
    # Open Banking integration
    external_account_id = models.CharField(_('external account ID'), max_length=100, blank=True)
    access_token = models.TextField(_('access token'), blank=True)
    refresh_token = models.TextField(_('refresh token'), blank=True)
    token_expires_at = models.DateTimeField(_('token expires at'), blank=True, null=True)
    
    # Account status and balance
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    current_balance = models.DecimalField(
        _('current balance'), 
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00')
    )
    available_balance = models.DecimalField(
        _('available balance'), 
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00')
    )
    last_sync_at = models.DateTimeField(_('last sync at'), blank=True, null=True)
    sync_frequency = models.IntegerField(_('sync frequency (hours)'), default=4)
    
    # Account settings
    nickname = models.CharField(_('nickname'), max_length=100, blank=True)
    is_primary = models.BooleanField(_('is primary account'), default=False)
    is_active = models.BooleanField(_('is active'), default=True)
    
    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'bank_accounts'
        verbose_name = _('Bank Account')
        verbose_name_plural = _('Bank Accounts')
        unique_together = ('company', 'bank_provider', 'agency', 'account_number')
    
    def __str__(self):
        return f"{self.bank_provider.name} - {self.agency}/{self.account_number}"
    
    @property
    def masked_account(self):
        """Return masked account number for security"""
        if len(self.account_number) > 4:
            return f"****{self.account_number[-4:]}"
        return self.account_number
    
    @property
    def display_name(self):
        """Return display name for the account"""
        if self.nickname:
            return f"{self.nickname} ({self.bank_provider.name})"
        return f"{self.bank_provider.name} - {self.masked_account}"


class TransactionCategory(models.Model):
    """
    Categories for transaction classification
    """
    CATEGORY_TYPES = [
        ('income', 'Receita'),
        ('expense', 'Despesa'),
        ('transfer', 'Transferência'),
    ]
    
    name = models.CharField(_('category name'), max_length=100)
    slug = models.SlugField(_('slug'), unique=True)
    category_type = models.CharField(_('category type'), max_length=20, choices=CATEGORY_TYPES)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='subcategories')
    
    # Visual settings
    icon = models.CharField(_('icon'), max_length=50, default='💰')
    color = models.CharField(_('color'), max_length=7, default='#3B82F6')
    
    # AI training data
    keywords = models.JSONField(_('keywords for AI'), default=list, help_text="Keywords for AI categorization")
    confidence_threshold = models.FloatField(_('confidence threshold'), default=0.7)
    
    # Settings
    is_system = models.BooleanField(_('is system category'), default=False)
    is_active = models.BooleanField(_('is active'), default=True)
    order = models.IntegerField(_('order'), default=0)
    
    class Meta:
        db_table = 'transaction_categories'
        verbose_name = _('Transaction Category')
        verbose_name_plural = _('Transaction Categories')
        ordering = ['category_type', 'order', 'name']
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
    
    @property
    def full_name(self):
        """Return full category path"""
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name


class Transaction(models.Model):
    """
    Financial transactions from bank accounts
    """
    TRANSACTION_TYPES = [
        ('debit', 'Débito'),
        ('credit', 'Crédito'),
        ('transfer_in', 'Transferência Recebida'),
        ('transfer_out', 'Transferência Enviada'),
        ('pix_in', 'PIX Recebido'),
        ('pix_out', 'PIX Enviado'),
        ('fee', 'Taxa'),
        ('interest', 'Juros'),
        ('adjustment', 'Ajuste'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('completed', 'Concluída'),
        ('failed', 'Falhou'),
        ('cancelled', 'Cancelada'),
    ]
    
    # Basic transaction info
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='transactions')
    external_id = models.CharField(_('external transaction ID'), max_length=100, blank=True)
    
    # Transaction details
    transaction_type = models.CharField(_('transaction type'), max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(_('amount'), max_digits=15, decimal_places=2)
    description = models.CharField(_('description'), max_length=500)
    transaction_date = models.DateTimeField(_('transaction date'))
    
    # Counterpart information
    counterpart_name = models.CharField(_('counterpart name'), max_length=200, blank=True)
    counterpart_document = models.CharField(_('counterpart document'), max_length=20, blank=True)
    counterpart_bank = models.CharField(_('counterpart bank'), max_length=100, blank=True)
    counterpart_agency = models.CharField(_('counterpart agency'), max_length=10, blank=True)
    counterpart_account = models.CharField(_('counterpart account'), max_length=20, blank=True)
    
    # Categorization
    category = models.ForeignKey(
        TransactionCategory, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='transactions'
    )
    subcategory = models.ForeignKey(
        TransactionCategory, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='subcategory_transactions'
    )
    
    # AI categorization data
    ai_category_confidence = models.FloatField(
        _('AI confidence'), 
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    ai_suggested_category = models.ForeignKey(
        TransactionCategory,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='ai_suggested_transactions'
    )
    is_ai_categorized = models.BooleanField(_('categorized by AI'), default=False)
    is_manually_reviewed = models.BooleanField(_('manually reviewed'), default=False)
    
    # Additional metadata
    reference_number = models.CharField(_('reference number'), max_length=100, blank=True)
    pix_key = models.CharField(_('PIX key'), max_length=100, blank=True)
    notes = models.TextField(_('notes'), blank=True)
    tags = models.JSONField(_('tags'), default=list)
    
    # Status and processing
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='completed')
    balance_after = models.DecimalField(
        _('balance after transaction'), 
        max_digits=15, 
        decimal_places=2,
        blank=True,
        null=True
    )
    
    # Reconciliation
    is_reconciled = models.BooleanField(_('is reconciled'), default=False)
    reconciled_at = models.DateTimeField(_('reconciled at'), blank=True, null=True)
    reconciled_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='reconciled_transactions'
    )
    
    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'transactions'
        verbose_name = _('Transaction')
        verbose_name_plural = _('Transactions')
        ordering = ['-transaction_date', '-created_at']
        indexes = [
            models.Index(fields=['bank_account', 'transaction_date']),
            models.Index(fields=['category', 'transaction_date']),
            models.Index(fields=['transaction_type', 'transaction_date']),
            models.Index(fields=['external_id']),
        ]
    
    def __str__(self):
        return f"{self.description} - R$ {self.amount} ({self.transaction_date.strftime('%d/%m/%Y')})"
    
    @property
    def is_income(self):
        """Check if transaction is income"""
        return self.transaction_type in ['credit', 'transfer_in', 'pix_in'] and self.amount > 0
    
    @property
    def is_expense(self):
        """Check if transaction is expense"""
        return self.transaction_type in ['debit', 'transfer_out', 'pix_out', 'fee'] or self.amount < 0
    
    @property
    def formatted_amount(self):
        """Return formatted amount with currency"""
        return f"R$ {abs(self.amount):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    @property
    def amount_with_sign(self):
        """Return amount with proper sign for display"""
        if self.is_income:
            return abs(self.amount)
        else:
            return -abs(self.amount)


class RecurringTransaction(models.Model):
    """
    Recurring transaction patterns for prediction and alerts
    """
    FREQUENCY_CHOICES = [
        ('daily', 'Diário'),
        ('weekly', 'Semanal'),
        ('biweekly', 'Quinzenal'),
        ('monthly', 'Mensal'),
        ('bimonthly', 'Bimestral'),
        ('quarterly', 'Trimestral'),
        ('semiannual', 'Semestral'),
        ('annual', 'Anual'),
    ]
    
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='recurring_transactions')
    name = models.CharField(_('name'), max_length=200)
    description_pattern = models.CharField(_('description pattern'), max_length=500)
    
    # Amount settings
    expected_amount = models.DecimalField(_('expected amount'), max_digits=15, decimal_places=2)
    amount_tolerance = models.DecimalField(
        _('amount tolerance'), 
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('5.00'),
        help_text="Tolerance percentage for amount matching"
    )
    
    # Timing settings
    frequency = models.CharField(_('frequency'), max_length=20, choices=FREQUENCY_CHOICES)
    next_expected_date = models.DateField(_('next expected date'))
    day_tolerance = models.IntegerField(_('day tolerance'), default=3)
    
    # Categorization
    category = models.ForeignKey(TransactionCategory, on_delete=models.SET_NULL, blank=True, null=True)
    
    # Settings
    is_active = models.BooleanField(_('is active'), default=True)
    auto_categorize = models.BooleanField(_('auto categorize'), default=True)
    send_alerts = models.BooleanField(_('send alerts'), default=True)
    
    # Statistics
    total_occurrences = models.IntegerField(_('total occurrences'), default=0)
    last_occurrence_date = models.DateField(_('last occurrence date'), blank=True, null=True)
    accuracy_rate = models.FloatField(_('accuracy rate'), default=0.0)
    
    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'recurring_transactions'
        verbose_name = _('Recurring Transaction')
        verbose_name_plural = _('Recurring Transactions')
    
    def __str__(self):
        return f"{self.name} - {self.frequency}"


class BankSync(models.Model):
    """
    Bank synchronization logs and status
    """
    SYNC_STATUS = [
        ('pending', 'Pendente'),
        ('running', 'Executando'),
        ('completed', 'Concluído'),
        ('failed', 'Falhou'),
        ('partial', 'Parcial'),
    ]
    
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='sync_logs')
    started_at = models.DateTimeField(_('started at'), auto_now_add=True)
    completed_at = models.DateTimeField(_('completed at'), blank=True, null=True)
    status = models.CharField(_('status'), max_length=20, choices=SYNC_STATUS, default='pending')
    
    # Sync details
    transactions_found = models.IntegerField(_('transactions found'), default=0)
    transactions_new = models.IntegerField(_('new transactions'), default=0)
    transactions_updated = models.IntegerField(_('updated transactions'), default=0)
    
    # Error handling
    error_message = models.TextField(_('error message'), blank=True)
    error_code = models.CharField(_('error code'), max_length=50, blank=True)
    
    # Sync range
    sync_from_date = models.DateField(_('sync from date'))
    sync_to_date = models.DateField(_('sync to date'))
    
    class Meta:
        db_table = 'bank_syncs'
        verbose_name = _('Bank Sync')
        verbose_name_plural = _('Bank Syncs')
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Sync {self.bank_account} - {self.status} ({self.started_at.strftime('%d/%m/%Y %H:%M')})"
    
    @property
    def duration(self):
        """Calculate sync duration"""
        if self.completed_at and self.started_at:
            return self.completed_at - self.started_at
        return None