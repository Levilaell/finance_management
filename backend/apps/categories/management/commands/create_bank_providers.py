"""
Management command to create default bank providers
"""
from apps.banking.models import BankProvider
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create default bank providers'
    
    def handle(self, *args, **options):
        banks = [
            {
                'name': 'Itaú Unibanco',
                'code': '341',
                'color': '#FF6600',
                'is_open_banking': True,
                'supports_pix': True,
                'supports_ted': True,
                'supports_doc': True,
                'is_active': True
            },
            {
                'name': 'Banco do Brasil',
                'code': '001',
                'color': '#FFFF00',
                'is_open_banking': True,
                'supports_pix': True,
                'supports_ted': True,
                'supports_doc': True,
                'is_active': True
            },
            {
                'name': 'Bradesco',
                'code': '237',
                'color': '#CC092F',
                'is_open_banking': True,
                'supports_pix': True,
                'supports_ted': True,
                'supports_doc': True,
                'is_active': True
            },
            {
                'name': 'Santander',
                'code': '033',
                'color': '#EC0000',
                'is_open_banking': True,
                'supports_pix': True,
                'supports_ted': True,
                'supports_doc': True,
                'is_active': True
            },
            {
                'name': 'Caixa Econômica Federal',
                'code': '104',
                'color': '#0066CC',
                'is_open_banking': True,
                'supports_pix': True,
                'supports_ted': True,
                'supports_doc': True,
                'is_active': True
            },
            {
                'name': 'Nubank',
                'code': '260',
                'color': '#8A05BE',
                'is_open_banking': True,
                'supports_pix': True,
                'supports_ted': True,
                'supports_doc': False,
                'is_active': True
            },
            {
                'name': 'Inter',
                'code': '077',
                'color': '#FF6600',
                'is_open_banking': True,
                'supports_pix': True,
                'supports_ted': True,
                'supports_doc': True,
                'is_active': True
            },
            {
                'name': 'C6 Bank',
                'code': '336',
                'color': '#FFDD00',
                'is_open_banking': True,
                'supports_pix': True,
                'supports_ted': True,
                'supports_doc': False,
                'is_active': True
            },
            {
                'name': 'Next',
                'code': '237',  # Same as Bradesco
                'color': '#00AA55',
                'is_open_banking': True,
                'supports_pix': True,
                'supports_ted': True,
                'supports_doc': False,
                'is_active': True
            },
            {
                'name': 'PicPay',
                'code': '380',
                'color': '#11C76F',
                'is_open_banking': True,
                'supports_pix': True,
                'supports_ted': False,
                'supports_doc': False,
                'is_active': True
            }
        ]
        
        created_count = 0
        
        for bank_data in banks:
            bank, created = BankProvider.objects.get_or_create(
                code=bank_data['code'],
                name=bank_data['name'],
                defaults=bank_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created bank: {bank.name} ({bank.code})')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Bank already exists: {bank.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nCreated {created_count} new banks successfully!')
        )