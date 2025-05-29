"""
Management command to create default subscription plans
"""
from decimal import Decimal

from apps.companies.models import SubscriptionPlan
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create default subscription plans'
    
    def handle(self, *args, **options):
        plans = [
            {
                'name': 'Starter',
                'slug': 'starter',
                'plan_type': 'starter',
                'price_monthly': Decimal('49.90'),
                'price_yearly': Decimal('478.80'),  # 20% discount
                'max_transactions': 500,
                'max_bank_accounts': 1,
                'max_users': 1,
                'has_ai_categorization': True,
                'has_advanced_reports': False,
                'has_api_access': False,
                'has_accountant_access': False,
                'is_active': True
            },
            {
                'name': 'Pro',
                'slug': 'pro',
                'plan_type': 'pro',
                'price_monthly': Decimal('99.90'),
                'price_yearly': Decimal('958.80'),  # 20% discount
                'max_transactions': 2000,
                'max_bank_accounts': 3,
                'max_users': 3,
                'has_ai_categorization': True,
                'has_advanced_reports': True,
                'has_api_access': False,
                'has_accountant_access': True,
                'is_active': True
            },
            {
                'name': 'Enterprise',
                'slug': 'enterprise',
                'plan_type': 'enterprise',
                'price_monthly': Decimal('199.90'),
                'price_yearly': Decimal('1918.80'),  # 20% discount
                'max_transactions': 10000,
                'max_bank_accounts': 10,
                'max_users': 10,
                'has_ai_categorization': True,
                'has_advanced_reports': True,
                'has_api_access': True,
                'has_accountant_access': True,
                'is_active': True
            }
        ]
        
        created_count = 0
        
        for plan_data in plans:
            plan, created = SubscriptionPlan.objects.get_or_create(
                slug=plan_data['slug'],
                defaults=plan_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created plan: {plan.name} - R$ {plan.price_monthly}/mês')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Plan already exists: {plan.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nCreated {created_count} new subscription plans successfully!')
        )