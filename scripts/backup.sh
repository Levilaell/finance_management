#!/bin/bash
# Backup script for Caixa Digital database

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BACKUP_DIR="/var/backups/caixadigital"
S3_BUCKET="caixadigital-backups"
RETENTION_DAYS=30
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Database credentials (from environment)
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-caixa_digital}
DB_USER=${DB_USER:-postgres}

echo -e "${GREEN}🔒 Starting backup process...${NC}"

# Create backup directory
mkdir -p $BACKUP_DIR

# Function to perform backup
perform_backup() {
    local backup_file="$BACKUP_DIR/caixadigital_${TIMESTAMP}.sql.gz"
    
    echo -e "${YELLOW}📦 Creating database backup...${NC}"
    
    # Use pg_dump with compression
    PGPASSWORD=$DB_PASSWORD pg_dump \
        -h $DB_HOST \
        -p $DB_PORT \
        -U $DB_USER \
        -d $DB_NAME \
        --no-owner \
        --no-privileges \
        --verbose \
        | gzip > $backup_file
    
    echo -e "${GREEN}✅ Backup created: $backup_file${NC}"
    echo $backup_file
}

# Function to upload to S3
upload_to_s3() {
    local backup_file=$1
    local s3_path="s3://$S3_BUCKET/database/$(basename $backup_file)"
    
    echo -e "${YELLOW}☁️  Uploading to S3...${NC}"
    
    aws s3 cp $backup_file $s3_path \
        --storage-class STANDARD_IA \
        --server-side-encryption AES256
    
    echo -e "${GREEN}✅ Uploaded to: $s3_path${NC}"
}

# Function to clean old backups
cleanup_old_backups() {
    echo -e "${YELLOW}🧹 Cleaning old backups...${NC}"
    
    # Local cleanup
    find $BACKUP_DIR -name "caixadigital_*.sql.gz" -mtime +$RETENTION_DAYS -delete
    
    # S3 cleanup (using lifecycle policy is better, but this is for immediate cleanup)
    aws s3 ls s3://$S3_BUCKET/database/ | while read -r line; do
        createDate=$(echo $line | awk '{print $1" "$2}')
        createDate=$(date -d "$createDate" +%s)
        olderThan=$(date -d "$RETENTION_DAYS days ago" +%s)
        if [[ $createDate -lt $olderThan ]]; then
            fileName=$(echo $line | awk '{print $4}')
            echo "Deleting old backup: $fileName"
            aws s3 rm s3://$S3_BUCKET/database/$fileName
        fi
    done
}

# Function to verify backup
verify_backup() {
    local backup_file=$1
    
    echo -e "${YELLOW}🔍 Verifying backup...${NC}"
    
    # Check file size
    local size=$(stat -f%z "$backup_file" 2>/dev/null || stat -c%s "$backup_file")
    if [ $size -lt 1000 ]; then
        echo -e "${RED}❌ Backup file too small: $size bytes${NC}"
        return 1
    fi
    
    # Test decompression
    if ! gzip -t $backup_file; then
        echo -e "${RED}❌ Backup file is corrupted${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ Backup verified successfully${NC}"
    return 0
}

# Function to send notification
send_notification() {
    local status=$1
    local message=$2
    
    # Send to Slack if webhook is configured
    if [ ! -z "$SLACK_WEBHOOK" ]; then
        local color="good"
        if [ "$status" != "success" ]; then
            color="danger"
        fi
        
        curl -X POST $SLACK_WEBHOOK \
            -H 'Content-type: application/json' \
            -d "{
                \"attachments\": [{
                    \"color\": \"$color\",
                    \"title\": \"Database Backup $status\",
                    \"text\": \"$message\",
                    \"footer\": \"Caixa Digital Backup System\",
                    \"ts\": $(date +%s)
                }]
            }"
    fi
    
    # Log to syslog
    logger -t caixadigital-backup "$status: $message"
}

# Main backup process
main() {
    # Check if running as part of maintenance mode
    if [ "$1" == "--maintenance" ]; then
        echo -e "${YELLOW}🔧 Enabling maintenance mode...${NC}"
        # Signal application to enter maintenance mode
        aws ssm send-command \
            --document-name "AWS-RunShellScript" \
            --targets "Key=tag:Name,Values=caixadigital-web" \
            --parameters 'commands=["touch /var/www/maintenance.flag"]'
        sleep 30  # Wait for connections to drain
    fi
    
    # Perform backup
    BACKUP_FILE=$(perform_backup)
    
    # Verify backup
    if verify_backup $BACKUP_FILE; then
        # Upload to S3
        upload_to_s3 $BACKUP_FILE
        
        # Clean old backups
        cleanup_old_backups
        
        # Send success notification
        send_notification "success" "Database backup completed successfully"
        
        # Disable maintenance mode if enabled
        if [ "$1" == "--maintenance" ]; then
            echo -e "${YELLOW}🔧 Disabling maintenance mode...${NC}"
            aws ssm send-command \
                --document-name "AWS-RunShellScript" \
                --targets "Key=tag:Name,Values=caixadigital-web" \
                --parameters 'commands=["rm -f /var/www/maintenance.flag"]'
        fi
        
        echo -e "${GREEN}🎉 Backup process completed successfully!${NC}"
        exit 0
    else
        # Send failure notification
        send_notification "failure" "Database backup failed - please check logs"
        
        echo -e "${RED}❌ Backup process failed!${NC}"
        exit 1
    fi
}

# Run main function
main $@