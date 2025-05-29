"""
Banking app serializers
Data serialization for financial models
"""
from decimal import Decimal

from django.utils import timezone
from rest_framework import serializers

from .models import (BankAccount, BankProvider, BankSync, RecurringTransaction,
                     Transaction, TransactionCategory)


class BankProviderSerializer(serializers.ModelSerializer):
    """
    Bank provider serializer for connection options
    """
    class Meta:
        model = BankProvider
        fields = [
            'id', 'name', 'code', 'logo', 'color',
            'is_open_banking', 'supports_pix', 'supports_ted'
        ]


class BankAccountSerializer(serializers.ModelSerializer):
    """
    Bank account serializer with balance and status info
    """
    bank_provider = BankProviderSerializer(read_only=True)
    masked_account = serializers.ReadOnlyField()
    display_name = serializers.ReadOnlyField()
    last_sync_status = serializers.SerializerMethodField()
    transaction_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BankAccount
        fields = [
            'id', 'bank_provider', 'account_type', 'agency', 
            'account_number', 'masked_account', 'display_name',
            'current_balance', 'available_balance', 'nickname',
            'is_primary', 'is_active', 'status', 'last_sync_at',
            'last_sync_status', 'transaction_count', 'created_at'
        ]
        read_only_fields = [
            'current_balance', 'available_balance', 'last_sync_at',
            'status', 'masked_account', 'display_name'
        ]
    
    def get_last_sync_status(self, obj):
        """Get last sync status"""
        last_sync = obj.sync_logs.first()
        if last_sync:
            return {
                'status': last_sync.status,
                'started_at': last_sync.started_at,
                'transactions_new': last_sync.transactions_new
            }
        return None
    
    def get_transaction_count(self, obj):
        """Get total transaction count for this account"""
        return obj.transactions.count()


class TransactionCategorySerializer(serializers.ModelSerializer):
    """
    Transaction category serializer with hierarchy
    """
    full_name = serializers.ReadOnlyField()
    subcategories = serializers.SerializerMethodField()
    transaction_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TransactionCategory
        fields = [
            'id', 'name', 'slug', 'category_type', 'parent',
            'icon', 'color', 'full_name', 'subcategories',
            'transaction_count', 'is_system', 'is_active'
        ]
    
    def get_subcategories(self, obj):
        """Get subcategories if any"""
        if obj.subcategories.exists():
            return TransactionCategorySerializer(
                obj.subcategories.filter(is_active=True), 
                many=True
            ).data
        return []
    
    def get_transaction_count(self, obj):
        """Get transaction count for this category"""
        request = self.context.get('request')
        if request and hasattr(request.user, 'company'):
            return obj.transactions.filter(
                bank_account__company=request.user.company
            ).count()
        return 0


class TransactionSerializer(serializers.ModelSerializer):
    """
    Transaction serializer with categorization and formatting
    """
    bank_account_name = serializers.CharField(source='bank_account.display_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_icon = serializers.CharField(source='category.icon', read_only=True)
    subcategory_name = serializers.CharField(source='subcategory.name', read_only=True)
    formatted_amount = serializers.ReadOnlyField()
    amount_with_sign = serializers.ReadOnlyField()
    is_income = serializers.ReadOnlyField()
    is_expense = serializers.ReadOnlyField()
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'bank_account', 'bank_account_name', 'transaction_type',
            'amount', 'formatted_amount', 'amount_with_sign', 'description',
            'transaction_date', 'counterpart_name', 'counterpart_document',
            'category', 'category_name', 'category_icon', 'subcategory',
            'subcategory_name', 'ai_category_confidence', 'is_ai_categorized',
            'is_manually_reviewed', 'reference_number', 'pix_key', 'notes',
            'tags', 'status', 'is_income', 'is_expense', 'is_reconciled',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'ai_category_confidence', 'is_ai_categorized', 'formatted_amount',
            'amount_with_sign', 'is_income', 'is_expense', 'bank_account_name',
            'category_name', 'category_icon', 'subcategory_name'
        ]
    
    def update(self, instance, validated_data):
        """Update transaction and mark as manually reviewed"""
        if 'category' in validated_data or 'subcategory' in validated_data:
            validated_data['is_manually_reviewed'] = True
        return super().update(instance, validated_data)


class RecurringTransactionSerializer(serializers.ModelSerializer):
    """
    Recurring transaction pattern serializer
    """
    bank_account_name = serializers.CharField(source='bank_account.display_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = RecurringTransaction
        fields = [
            'id', 'bank_account', 'bank_account_name', 'name',
            'description_pattern', 'expected_amount', 'amount_tolerance',
            'frequency', 'next_expected_date', 'day_tolerance',
            'category', 'category_name', 'is_active', 'auto_categorize',
            'send_alerts', 'total_occurrences', 'last_occurrence_date',
            'accuracy_rate', 'created_at'
        ]


class BankSyncSerializer(serializers.ModelSerializer):
    """
    Bank synchronization log serializer
    """
    bank_account_name = serializers.CharField(source='bank_account.display_name', read_only=True)
    duration = serializers.ReadOnlyField()
    
    class Meta:
        model = BankSync
        fields = [
            'id', 'bank_account', 'bank_account_name', 'started_at',
            'completed_at', 'duration', 'status', 'transactions_found',
            'transactions_new', 'transactions_updated', 'error_message',
            'sync_from_date', 'sync_to_date'
        ]


class DashboardSerializer(serializers.Serializer):
    """
    Dashboard data serializer
    """
    current_balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    monthly_income = serializers.DecimalField(max_digits=15, decimal_places=2)
    monthly_expenses = serializers.DecimalField(max_digits=15, decimal_places=2)
    monthly_net = serializers.DecimalField(max_digits=15, decimal_places=2)
    accounts_count = serializers.IntegerField()
    transactions_count = serializers.IntegerField()
    recent_transactions = TransactionSerializer(many=True, read_only=True)
    top_categories = serializers.ListField(child=serializers.DictField())


class TransactionSummarySerializer(serializers.Serializer):
    """
    Transaction summary for reports
    """
    period = serializers.CharField()
    income = serializers.DecimalField(max_digits=15, decimal_places=2)
    expenses = serializers.DecimalField(max_digits=15, decimal_places=2)
    net = serializers.DecimalField(max_digits=15, decimal_places=2)
    transaction_count = serializers.IntegerField()
    top_income_categories = serializers.ListField(child=serializers.DictField())
    top_expense_categories = serializers.ListField(child=serializers.DictField())


class CashFlowSerializer(serializers.Serializer):
    """
    Cash flow projection serializer
    """
    date = serializers.DateField()
    projected_balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    expected_income = serializers.DecimalField(max_digits=15, decimal_places=2)
    expected_expenses = serializers.DecimalField(max_digits=15, decimal_places=2)
    confidence_level = serializers.FloatField()
    alerts = serializers.ListField(child=serializers.CharField(), required=False)


class CategoryAnalysisSerializer(serializers.Serializer):
    """
    Category analysis for insights
    """
    category_name = serializers.CharField()
    category_icon = serializers.CharField()
    current_period = serializers.DecimalField(max_digits=15, decimal_places=2)
    previous_period = serializers.DecimalField(max_digits=15, decimal_places=2)
    change_percentage = serializers.FloatField()
    transaction_count = serializers.IntegerField()
    average_amount = serializers.DecimalField(max_digits=15, decimal_places=2)