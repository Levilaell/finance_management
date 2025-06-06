# Generated by Django 4.2.16 on 2025-05-29 18:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('companies', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='template name')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('report_type', models.CharField(default='custom', max_length=20, verbose_name='report type')),
                ('template_config', models.JSONField(default=dict, verbose_name='template configuration')),
                ('charts', models.JSONField(default=list, verbose_name='charts configuration')),
                ('default_parameters', models.JSONField(default=dict, verbose_name='default parameters')),
                ('default_filters', models.JSONField(default=dict, verbose_name='default filters')),
                ('is_public', models.BooleanField(default=False, verbose_name='is public')),
                ('is_active', models.BooleanField(default=True, verbose_name='is active')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='report_templates', to='companies.company')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_templates', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Report Template',
                'verbose_name_plural': 'Report Templates',
                'db_table': 'report_templates',
            },
        ),
        migrations.CreateModel(
            name='ReportSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report_type', models.CharField(choices=[('monthly_summary', 'Resumo Mensal'), ('quarterly_report', 'Relatório Trimestral'), ('annual_report', 'Relatório Anual'), ('cash_flow', 'Fluxo de Caixa'), ('profit_loss', 'DRE - Demonstração de Resultados'), ('category_analysis', 'Análise por Categoria'), ('tax_report', 'Relatório Fiscal'), ('custom', 'Personalizado')], max_length=20, verbose_name='report type')),
                ('frequency', models.CharField(choices=[('daily', 'Diário'), ('weekly', 'Semanal'), ('monthly', 'Mensal'), ('quarterly', 'Trimestral'), ('yearly', 'Anual')], max_length=20, verbose_name='frequency')),
                ('send_email', models.BooleanField(default=True, verbose_name='send by email')),
                ('email_recipients', models.JSONField(default=list, verbose_name='email recipients')),
                ('file_format', models.CharField(choices=[('pdf', 'PDF'), ('xlsx', 'Excel'), ('csv', 'CSV'), ('json', 'JSON')], default='pdf', max_length=10, verbose_name='file format')),
                ('is_active', models.BooleanField(default=True, verbose_name='is active')),
                ('next_run_at', models.DateTimeField(verbose_name='next run at')),
                ('last_run_at', models.DateTimeField(blank=True, null=True, verbose_name='last run at')),
                ('parameters', models.JSONField(default=dict, verbose_name='parameters')),
                ('filters', models.JSONField(default=dict, verbose_name='filters')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='report_schedules', to='companies.company')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_schedules', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Report Schedule',
                'verbose_name_plural': 'Report Schedules',
                'db_table': 'report_schedules',
            },
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report_type', models.CharField(choices=[('monthly_summary', 'Resumo Mensal'), ('quarterly_report', 'Relatório Trimestral'), ('annual_report', 'Relatório Anual'), ('cash_flow', 'Fluxo de Caixa'), ('profit_loss', 'DRE - Demonstração de Resultados'), ('category_analysis', 'Análise por Categoria'), ('tax_report', 'Relatório Fiscal'), ('custom', 'Personalizado')], max_length=20, verbose_name='report type')),
                ('title', models.CharField(max_length=200, verbose_name='title')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('period_start', models.DateField(verbose_name='period start')),
                ('period_end', models.DateField(verbose_name='period end')),
                ('parameters', models.JSONField(default=dict, verbose_name='parameters')),
                ('filters', models.JSONField(default=dict, verbose_name='filters')),
                ('file_format', models.CharField(choices=[('pdf', 'PDF'), ('xlsx', 'Excel'), ('csv', 'CSV'), ('json', 'JSON')], max_length=10, verbose_name='file format')),
                ('file', models.FileField(blank=True, null=True, upload_to='reports/%Y/%m/', verbose_name='report file')),
                ('file_size', models.IntegerField(default=0, verbose_name='file size')),
                ('is_generated', models.BooleanField(default=False, verbose_name='is generated')),
                ('generation_time', models.IntegerField(default=0, verbose_name='generation time (seconds)')),
                ('error_message', models.TextField(blank=True, verbose_name='error message')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='companies.company')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_reports', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Report',
                'verbose_name_plural': 'Reports',
                'db_table': 'reports',
                'ordering': ['-created_at'],
            },
        ),
    ]
