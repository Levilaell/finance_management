#!/bin/bash

echo "🔧 Fixing migrations..."

cd backend

# Remove the existing database if it exists
if [ -f "db.sqlite3" ]; then
    echo "Removing existing database..."
    rm db.sqlite3
fi

# Remove existing migration files (keeping __init__.py)
echo "Cleaning up old migrations..."
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Create fresh migrations for each app
echo "Creating migrations for authentication app..."
python manage.py makemigrations authentication

echo "Creating migrations for companies app..."
python manage.py makemigrations companies

echo "Creating migrations for banking app..."
python manage.py makemigrations banking

echo "Creating migrations for categories app..."
python manage.py makemigrations categories

echo "Creating migrations for reports app..."
python manage.py makemigrations reports

echo "Creating migrations for notifications app..."
python manage.py makemigrations notifications

# Run all migrations
echo "Running migrations..."
python manage.py migrate

# Load initial data
echo "📊 Loading initial data..."
python manage.py create_subscription_plans
python manage.py create_bank_providers
python manage.py create_default_categories

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Migrations fixed!"
echo ""
echo "📝 Next steps:"
echo "1. Create a superuser: cd backend && python manage.py createsuperuser"
echo "2. Start the development server: cd backend && python manage.py runserver"