"""
Management command to create default transaction categories
"""
from apps.banking.models import TransactionCategory
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create default transaction categories'
    
    def handle(self, *args, **options):
        categories = [
            # Income categories
            {
                'name': 'Vendas',
                'slug': 'vendas',
                'category_type': 'income',
                'icon': '💰',
                'color': '#10B981',
                'keywords': ['venda', 'pagamento', 'recebimento', 'pix recebido', 'transferencia recebida'],
                'is_system': True
            },
            {
                'name': 'Serviços',
                'slug': 'servicos-receita',
                'category_type': 'income',
                'icon': '🔧',
                'color': '#3B82F6',
                'keywords': ['servico', 'consultoria', 'manutencao', 'reparo'],
                'is_system': True
            },
            {
                'name': 'Juros e Rendimentos',
                'slug': 'juros-rendimentos',
                'category_type': 'income',
                'icon': '📈',
                'color': '#8B5CF6',
                'keywords': ['juros', 'rendimento', 'aplicacao', 'cdb', 'poupanca'],
                'is_system': True
            },
            {
                'name': 'Outras Receitas',
                'slug': 'outras-receitas',
                'category_type': 'income',
                'icon': '💵',
                'color': '#059669',
                'keywords': ['outros', 'diversos'],
                'is_system': True
            },
            
            # Expense categories
            {
                'name': 'Fornecedores',
                'slug': 'fornecedores',
                'category_type': 'expense',
                'icon': '🏪',
                'color': '#EF4444',
                'keywords': ['fornecedor', 'materia prima', 'estoque', 'mercadoria'],
                'is_system': True
            },
            {
                'name': 'Aluguel',
                'slug': 'aluguel',
                'category_type': 'expense',
                'icon': '🏢',
                'color': '#F59E0B',
                'keywords': ['aluguel', 'locacao', 'imovel'],
                'is_system': True
            },
            {
                'name': 'Energia Elétrica',
                'slug': 'energia-eletrica',
                'category_type': 'expense',
                'icon': '⚡',
                'color': '#FBBF24',
                'keywords': ['energia', 'luz', 'eletrica', 'cemig', 'copel', 'enel'],
                'is_system': True
            },
            {
                'name': 'Água',
                'slug': 'agua',
                'category_type': 'expense',
                'icon': '💧',
                'color': '#06B6D4',
                'keywords': ['agua', 'saneamento', 'sabesp', 'copasa'],
                'is_system': True
            },
            {
                'name': 'Internet e Telefone',
                'slug': 'internet-telefone',
                'category_type': 'expense',
                'icon': '📡',
                'color': '#8B5CF6',
               'keywords': ['internet', 'telefone', 'claro', 'vivo', 'tim', 'oi', 'telecom'],
               'is_system': True
           },
           {
               'name': 'Combustível',
               'slug': 'combustivel',
               'category_type': 'expense',
               'icon': '⛽',
               'color': '#DC2626',
               'keywords': ['combustivel', 'gasolina', 'etanol', 'diesel', 'posto'],
               'is_system': True
           },
           {
               'name': 'Alimentação',
               'slug': 'alimentacao',
               'category_type': 'expense',
               'icon': '🍽️',
               'color': '#F97316',
               'keywords': ['alimentacao', 'restaurante', 'lanche', 'ifood', 'delivery'],
               'is_system': True
           },
           {
               'name': 'Material de Escritório',
               'slug': 'material-escritorio',
               'category_type': 'expense',
               'icon': '📝',
               'color': '#6B7280',
               'keywords': ['material', 'escritorio', 'papelaria', 'caneta', 'papel'],
               'is_system': True
           },
           {
               'name': 'Marketing e Publicidade',
               'slug': 'marketing-publicidade',
               'category_type': 'expense',
               'icon': '📢',
               'color': '#EC4899',
               'keywords': ['marketing', 'publicidade', 'facebook ads', 'google ads', 'propaganda'],
               'is_system': True
           },
           {
               'name': 'Impostos e Taxas',
               'slug': 'impostos-taxas',
               'category_type': 'expense',
               'icon': '📋',
               'color': '#7C2D12',
               'keywords': ['imposto', 'taxa', 'darf', 'das', 'inss', 'irpj', 'csll'],
               'is_system': True
           },
           {
               'name': 'Salários e Encargos',
               'slug': 'salarios-encargos',
               'category_type': 'expense',
               'icon': '👥',
               'color': '#1F2937',
               'keywords': ['salario', 'funcionario', 'inss', 'fgts', 'encargo'],
               'is_system': True
           },
           {
               'name': 'Manutenção e Reparos',
               'slug': 'manutencao-reparos',
               'category_type': 'expense',
               'icon': '🔧',
               'color': '#374151',
               'keywords': ['manutencao', 'reparo', 'conserto', 'oficina'],
               'is_system': True
           },
           {
               'name': 'Seguros',
               'slug': 'seguros',
               'category_type': 'expense',
               'icon': '🛡️',
               'color': '#1E40AF',
               'keywords': ['seguro', 'seguradora', 'bradesco seguros', 'porto seguro'],
               'is_system': True
           },
           {
               'name': 'Contabilidade',
               'slug': 'contabilidade',
               'category_type': 'expense',
               'icon': '📊',
               'color': '#059669',
               'keywords': ['contador', 'contabilidade', 'escritorio contabil'],
               'is_system': True
           },
           {
               'name': 'Tecnologia',
               'slug': 'tecnologia',
               'category_type': 'expense',
               'icon': '💻',
               'color': '#7C3AED',
               'keywords': ['software', 'sistema', 'tecnologia', 'aplicativo', 'saas'],
               'is_system': True
           },
           {
               'name': 'Viagens e Hospedagem',
               'slug': 'viagens-hospedagem',
               'category_type': 'expense',
               'icon': '✈️',
               'color': '#0891B2',
               'keywords': ['viagem', 'hotel', 'hospedagem', 'passagem', 'uber', '99'],
               'is_system': True
           },
           {
               'name': 'Taxas Bancárias',
               'slug': 'taxas-bancarias',
               'category_type': 'expense',
               'icon': '🏦',
               'color': '#B91C1C',
               'keywords': ['taxa', 'bancaria', 'manutencao conta', 'ted', 'doc', 'tarifa'],
               'is_system': True
           },
           {
               'name': 'Outras Despesas',
               'slug': 'outras-despesas',
               'category_type': 'expense',
               'icon': '💸',
               'color': '#6B7280',
               'keywords': ['outros', 'diversos', 'despesas'],
               'is_system': True
           },
           
           # Transfer categories
           {
               'name': 'Transferência Entre Contas',
               'slug': 'transferencia-contas',
               'category_type': 'transfer',
               'icon': '🔄',
               'color': '#6366F1',
               'keywords': ['transferencia', 'conta', 'proprio'],
               'is_system': True
           },
           {
               'name': 'Aplicações Financeiras',
               'slug': 'aplicacoes-financeiras',
               'category_type': 'transfer',
               'icon': '💎',
               'color': '#8B5CF6',
               'keywords': ['aplicacao', 'investimento', 'cdb', 'fundo'],
               'is_system': True
           }
       ]
        
        created_count = 0
       
        for category_data in categories:
           category, created = TransactionCategory.objects.get_or_create(
               slug=category_data['slug'],
               defaults=category_data
           )
           
           if created:
               created_count += 1
               self.stdout.write(
                   self.style.SUCCESS(f'Created category: {category.name}')
               )
           else:
               self.stdout.write(
                   self.style.WARNING(f'Category already exists: {category.name}')
               )

        # Create subcategories for some main categories
        subcategories = [
           # Fornecedores subcategories
           {
               'name': 'Matéria Prima',
               'slug': 'materia-prima',
               'category_type': 'expense',
               'parent_slug': 'fornecedores',
               'icon': '📦',
               'color': '#EF4444',
               'keywords': ['materia', 'prima', 'insumo'],
               'is_system': True
           },
           {
               'name': 'Produtos para Revenda',
               'slug': 'produtos-revenda',
               'category_type': 'expense',
               'parent_slug': 'fornecedores',
               'icon': '📋',
               'color': '#EF4444',
               'keywords': ['produto', 'revenda', 'mercadoria'],
               'is_system': True
           },

           # Marketing subcategories
           {
               'name': 'Facebook Ads',
               'slug': 'facebook-ads',
               'category_type': 'expense',
               'parent_slug': 'marketing-publicidade',
               'icon': '📘',
               'color': '#1877F2',
               'keywords': ['facebook', 'instagram', 'meta'],
               'is_system': True
           },
           {
               'name': 'Google Ads',
               'slug': 'google-ads',
               'category_type': 'expense',
               'parent_slug': 'marketing-publicidade',
               'icon': '🔍',
               'color': '#34A853',
               'keywords': ['google', 'adwords', 'ads'],
               'is_system': True
           },

           # Alimentação subcategories
           {
               'name': 'Delivery',
               'slug': 'delivery',
               'category_type': 'expense',
               'parent_slug': 'alimentacao',
               'icon': '🛵',
               'color': '#F97316',
               'keywords': ['ifood', 'uber eats', 'delivery', 'entrega'],
               'is_system': True
           },
           {
               'name': 'Restaurante',
               'slug': 'restaurante',
               'category_type': 'expense',
               'parent_slug': 'alimentacao',
               'icon': '🍽️',
               'color': '#F97316',
               'keywords': ['restaurante', 'jantar', 'almoco'],
               'is_system': True
           }
        ]
        
        for subcat_data in subcategories:
            parent_slug = subcat_data.pop('parent_slug')
            try:
                parent = TransactionCategory.objects.get(slug=parent_slug)
                subcat_data['parent'] = parent
                
                subcategory, created = TransactionCategory.objects.get_or_create(
                    slug=subcat_data['slug'],
                    defaults=subcat_data
                )
               
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Created subcategory: {subcategory.name} → {parent.name}')
                    )
                   
            except TransactionCategory.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Parent category not found: {parent_slug}')
                )
       
        self.stdout.write(
            self.style.SUCCESS(f'\nCreated {created_count} new categories successfully!')
        )