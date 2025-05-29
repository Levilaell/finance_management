#!/bin/bash

echo "🚀 Setting up Caixa Digital..."

# Create .env file if it doesn't exist
if [ ! -f backend/.env ]; then
    echo "📋 Creating .env file..."
    cp backend/.env.example backend/.env
    echo "✅ .env file created. Please update it with your credentials."
fi

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r backend/requirements.txt

# Create migrations
echo "🗄️ Creating database migrations..."
cd backend
python manage.py makemigrations
python manage.py migrate

# Create management command directories if needed
mkdir -p apps/companies/management/commands

# Load initial data
echo "📊 Loading initial data..."
python manage.py create_subscription_plans
python manage.py create_bank_providers
python manage.py create_default_categories

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Setup completed!"
echo ""
echo "📝 Next steps:"
echo "1. Create a superuser: python manage.py createsuperuser"
echo "2. Start the development server: python manage.py runserver"
echo "3. (Optional) Start Celery: celery -A core worker -l info"
echo "4. (Optional) Start Celery Beat: celery -A core beat -l info"