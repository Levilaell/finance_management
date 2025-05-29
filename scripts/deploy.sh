#!/bin/bash
# Deploy script for Caixa Digital

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENV=${1:-production}
BRANCH=${2:-main}

echo -e "${GREEN}🚀 Starting deployment to ${ENV}...${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check requirements
echo -e "${YELLOW}📋 Checking requirements...${NC}"
for cmd in git python3 pip docker docker-compose aws; do
    if ! command_exists $cmd; then
        echo -e "${RED}❌ $cmd is not installed${NC}"
        exit 1
    fi
done

# Update code
echo -e "${YELLOW}📥 Pulling latest code from ${BRANCH}...${NC}"
git fetch origin
git checkout $BRANCH
git pull origin $BRANCH

# Build Docker image
echo -e "${YELLOW}🐳 Building Docker image...${NC}"
docker build -t caixadigital:latest -f backend/Dockerfile backend/

# Tag for ECR
if [ "$ENV" == "production" ]; then
    echo -e "${YELLOW}🏷️  Tagging for ECR...${NC}"
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    AWS_REGION=${AWS_REGION:-us-east-1}
    ECR_REPO="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/caixadigital"
    
    # Login to ECR
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPO
    
    # Tag and push
    docker tag caixadigital:latest $ECR_REPO:latest
    docker tag caixadigital:latest $ECR_REPO:$(git rev-parse --short HEAD)
    docker push $ECR_REPO:latest
    docker push $ECR_REPO:$(git rev-parse --short HEAD)
fi

# Run migrations
echo -e "${YELLOW}🗄️  Running database migrations...${NC}"
if [ "$ENV" == "production" ]; then
    # Run in ECS
    aws ecs run-task \
        --cluster caixadigital-cluster \
        --task-definition caixadigital-migration \
        --overrides '{"containerOverrides":[{"name":"backend","command":["python","manage.py","migrate"]}]}'
else
    # Run locally
    docker-compose run --rm backend python manage.py migrate
fi

# Collect static files
echo -e "${YELLOW}📁 Collecting static files...${NC}"
if [ "$ENV" == "production" ]; then
    aws ecs run-task \
        --cluster caixadigital-cluster \
        --task-definition caixadigital-migration \
        --overrides '{"containerOverrides":[{"name":"backend","command":["python","manage.py","collectstatic","--noinput"]}]}'
else
    docker-compose run --rm backend python manage.py collectstatic --noinput
fi

# Deploy application
echo -e "${YELLOW}🚀 Deploying application...${NC}"
if [ "$ENV" == "production" ]; then
    # Update ECS service
    aws ecs update-service \
        --cluster caixadigital-cluster \
        --service caixadigital-service \
        --force-new-deployment
    
    # Wait for deployment
    echo -e "${YELLOW}⏳ Waiting for deployment to complete...${NC}"
    aws ecs wait services-stable \
        --cluster caixadigital-cluster \
        --services caixadigital-service
else
    # Restart local containers
    docker-compose down
    docker-compose up -d
fi

# Health check
echo -e "${YELLOW}🏥 Running health check...${NC}"
if [ "$ENV" == "production" ]; then
    HEALTH_URL="https://api.caixadigital.com.br/api/auth/health/"
else
    HEALTH_URL="http://localhost:8000/api/auth/health/"
fi

sleep 10  # Wait for service to start
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $HTTP_CODE -eq 200 ]; then
    echo -e "${GREEN}✅ Deployment successful!${NC}"
else
    echo -e "${RED}❌ Health check failed with code $HTTP_CODE${NC}"
    exit 1
fi

# Create Sentry release
if [ "$ENV" == "production" ] && command_exists sentry-cli; then
    echo -e "${YELLOW}📊 Creating Sentry release...${NC}"
    VERSION=$(git rev-parse --short HEAD)
    sentry-cli releases new -p caixadigital $VERSION
    sentry-cli releases set-commits --auto $VERSION
    sentry-cli releases finalize $VERSION
    sentry-cli releases deploys $VERSION new -e production
fi

echo -e "${GREEN}🎉 Deployment to ${ENV} completed successfully!${NC}"