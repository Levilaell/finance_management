#!/bin/bash
# Restore script for Caixa Digital database

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BACKUP_DIR="/var/backups/caixadigital"
S3_BUCKET="caixadigital-backups"

# Database credentials (from environment)
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-caixa_digital}
DB_USER=${DB_USER:-postgres}

echo -e "${GREEN}🔄 Starting restore process...${NC}"

# Function to list available backups
list_backups() {
    echo -e "${YELLOW}📋 Available backups:${NC}"
    echo ""
    echo "Local backups:"
    ls -lh $BACKUP_DIR/*.sql.gz 2>/dev/null || echo "No local backups found"
    
    echo ""
    echo "S3 backups:"
    aws s3 ls s3://$S3_BUCKET/database/ --human-readable
}

# Function to download from S3
download_from_s3() {
    local s3_file=$1
    local local_file="$BACKUP_DIR/$(basename $s3_file)"
    
    echo -e "${YELLOW}⬇️  Downloading from S3...${NC}"
    aws s3 cp s3://$S3_BUCKET/database/$s3_file $local_file
    
    echo $local_file
}

# Function to restore backup
restore_backup() {
    local backup_file=$1
    
    echo -e "${YELLOW}⚠️  WARNING: This will overwrite the current database!${NC}"
    read -p "Are you sure you want to continue? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        echo -e "${RED}❌ Restore cancelled${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}🔧 Creating backup of current database...${NC}"
    PGPASSWORD=$DB_PASSWORD pg_dump \
        -h $DB_HOST \
        -p $DB_PORT \
        -U $DB_USER \
        -d $DB_NAME \
        --no-owner \
        --no-privileges \
        | gzip > "$BACKUP_DIR/pre_restore_$(date +%Y%m%d_%H%M%S).sql.gz"
    
    echo -e "${YELLOW}🗑️  Dropping existing database...${NC}"
    PGPASSWORD=$DB_PASSWORD psql \
        -h $DB_HOST \
        -p $DB_PORT \
        -U $DB_USER \
        -c "DROP DATABASE IF EXISTS $DB_NAME;"
    
    echo -e "${YELLOW}🆕 Creating new database...${NC}"
    PGPASSWORD=$DB_PASSWORD psql \
        -h $DB_HOST \
        -p $DB_PORT \
        -U $DB_USER \
        -c "CREATE DATABASE $DB_NAME;"
    
    echo -e "${YELLOW}📥 Restoring database...${NC}"
    gunzip -c $backup_file | PGPASSWORD=$DB_PASSWORD psql \
        -h $DB_HOST \
        -p $DB_PORT \
        -U $DB_USER \
        -d $DB_NAME
    
    echo -e "${GREEN}✅ Database restored successfully${NC}"
}

# Function to verify restore
verify_restore() {
    echo -e "${YELLOW}🔍 Verifying restore...${NC}"
    
    # Check table count
    local table_count=$(PGPASSWORD=$DB_PASSWORD psql \
        -h $DB_HOST \
        -p $DB_PORT \
        -U $DB_USER \
        -d $DB_NAME \
        -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
    
    if [ $table_count -gt 0 ]; then
        echo -e "${GREEN}✅ Found $table_count tables${NC}"
        
        # Run Django checks
        if command -v python3 >/dev/null 2>&1; then
            echo -e "${YELLOW}🐍 Running Django checks...${NC}"
            cd /app/backend && python3 manage.py check --database default
        fi
        
        return 0
    else
        echo -e "${RED}❌ No tables found in database${NC}"
        return 1
    fi
}

# Main restore process
main() {
    case "$1" in
        "list")
            list_backups
            ;;
        "restore")
            if [ -z "$2" ]; then
                echo -e "${RED}❌ Please specify a backup file${NC}"
                echo "Usage: $0 restore <backup_file>"
                exit 1
            fi
            
            BACKUP_FILE=$2
            
            # Check if file exists locally
            if [ ! -f "$BACKUP_FILE" ]; then
                # Check if it's an S3 file
                if [[ $BACKUP_FILE == s3://* ]]; then
                    BACKUP_FILE=$(download_from_s3 $(basename $BACKUP_FILE))
                else
                    # Try to download from S3
                    BACKUP_FILE=$(download_from_s3 $BACKUP_FILE)
                fi
            fi
            
            # Verify backup file exists
            if [ ! -f "$BACKUP_FILE" ]; then
                echo -e "${RED}❌ Backup file not found: $BACKUP_FILE${NC}"
                exit 1
            fi
            
            # Restore backup
            restore_backup $BACKUP_FILE
            
            # Verify restore
            if verify_restore; then
                echo -e "${GREEN}🎉 Restore completed successfully!${NC}"
                
                # Run post-restore tasks
                echo -e "${YELLOW}🔧 Running post-restore tasks...${NC}"
                cd /app/backend
                python3 manage.py migrate --run-syncdb
                python3 manage.py collectstatic --noinput
                
                # Clear cache
                python3 manage.py shell -c "from django.core.cache import cache; cache.clear()"
                
                echo -e "${GREEN}✅ Post-restore tasks completed${NC}"
            else
                echo -e "${RED}❌ Restore verification failed${NC}"
                exit 1
            fi
            ;;
        *)
            echo "Usage: $0 {list|restore <backup_file>}"
            exit 1
            ;;
    esac
}

# Run main function
main $@