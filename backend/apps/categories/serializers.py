"""
Categories app serializers
"""
from rest_framework import serializers

from .models import (AITrainingData, CategorizationLog, CategoryRule,
                     CategorySuggestion)


class CategoryRuleSerializer(serializers.ModelSerializer):
    """
    Category rule serializer
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_icon = serializers.CharField(source='category.icon', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = CategoryRule
        fields = [
            'id', 'name', 'rule_type', 'conditions', 'category',
            'category_name', 'category_icon', 'priority', 'is_active',
            'confidence_threshold', 'match_count', 'accuracy_rate',
            'created_at', 'updated_at', 'created_by_name'
        ]
        read_only_fields = ['match_count', 'accuracy_rate', 'created_by_name']


class AITrainingDataSerializer(serializers.ModelSerializer):
    """
    AI training data serializer
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    verified_by_name = serializers.CharField(source='verified_by.full_name', read_only=True)
    
    class Meta:
        model = AITrainingData
        fields = [
            'id', 'description', 'amount', 'transaction_type',
            'counterpart_name', 'category', 'category_name',
            'subcategory', 'is_verified', 'verification_source',
            'created_at', 'verified_by_name'
        ]


class CategorySuggestionSerializer(serializers.ModelSerializer):
    """
    Category suggestion serializer
    """
    transaction_description = serializers.CharField(source='transaction.description', read_only=True)
    transaction_amount = serializers.DecimalField(source='transaction.amount', max_digits=15, decimal_places=2, read_only=True)
    suggested_category_name = serializers.CharField(source='suggested_category.name', read_only=True)
    suggested_category_icon = serializers.CharField(source='suggested_category.icon', read_only=True)
    
    class Meta:
        model = CategorySuggestion
        fields = [
            'id', 'transaction', 'transaction_description', 'transaction_amount',
            'suggested_category', 'suggested_category_name', 'suggested_category_icon',
            'confidence_score', 'alternative_suggestions', 'model_version',
            'is_accepted', 'is_rejected', 'user_feedback', 'created_at'
        ]


class CategorizationLogSerializer(serializers.ModelSerializer):
    """
    Categorization log serializer
    """
    transaction_description = serializers.CharField(source='transaction.description', read_only=True)
    suggested_category_name = serializers.CharField(source='suggested_category.name', read_only=True)
    final_category_name = serializers.CharField(source='final_category.name', read_only=True)
    rule_name = serializers.CharField(source='rule_used.name', read_only=True)
    
    class Meta:
        model = CategorizationLog
        fields = [
            'id', 'transaction', 'transaction_description', 'method',
            'suggested_category_name', 'confidence_score', 'processing_time_ms',
            'rule_name', 'ai_model_version', 'was_accepted',
            'final_category_name', 'created_at'
        ]