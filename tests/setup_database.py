#!/usr/bin/env python3
"""
Database setup script for Caixa Digital
Sets up the database with initial data
"""
import os
import sys

import django
from django.core.management import execute_from_command_line

# Add backend to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def run_command(command):
    """Run a Django management command"""
    print(f"\n{'='*50}")
    print(f"Running: {' '.join(command)}")
    print('='*50)
    execute_from_command_line(['manage.py'] + command)

def main():
    """Main setup function"""
    print("🚀 Setting up Caixa Digital Database...")
    
    # Create and run migrations
    commands = [
        ['makemigrations'],
        ['makemigrations', 'authentication'],
        ['makemigrations', 'companies'],
        ['makemigrations', 'banking'],
        ['makemigrations', 'categories'],
        ['makemigrations', 'reports'],
        ['makemigrations', 'notifications'],
        ['migrate'],
        
        # Create initial data
        ['create_subscription_plans'],
        ['create_bank_providers'],
        ['create_default_categories'],
        
        # Create superuser (optional)
        ['collectstatic', '--noinput'],
    ]
    
    for command in commands:
        try:
            run_command(command)
        except Exception as e:
            print(f"❌ Error running {command}: {e}")
            continue
    
    print("\n✅ Database setup completed!")
    print("\n📝 Next steps:")
    print("1. Create a superuser: python manage.py createsuperuser")
    print("2. Start the development server: python manage.py runserver")
    print("3. Start Celery worker: celery -A core worker -l info")
    print("4. Start Celery beat: celery -A core beat -l info")

if __name__ == '__main__':
    main()