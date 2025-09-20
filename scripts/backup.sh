#!/bin/bash

# Healthcare Voice AI - Backup and Recovery Script
# Comprehensive backup solution for production environments

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${BACKUP_DIR:-/backups/healthcare-voice-ai}"
DATE=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$BACKUP_DIR/backup_$DATE.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

# Create backup directory
create_backup_dir() {
    log_info "Creating backup directory: $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$BACKUP_DIR/database"
    mkdir -p "$BACKUP_DIR/application"
    mkdir -p "$BACKUP_DIR/logs"
    mkdir -p "$BACKUP_DIR/ssl"
    mkdir -p "$BACKUP_DIR/config"
}

# Database backup
backup_database() {
    log_info "Starting database backup..."
    
    local db_backup_file="$BACKUP_DIR/database/db_backup_$DATE.sql"
    
    # Check if we're using Supabase or local PostgreSQL
    if [[ -n "${SUPABASE_URL:-}" ]]; then
        log_info "Backing up Supabase database..."
        # For Supabase, we'll use pg_dump with the connection string
        if command -v pg_dump &> /dev/null; then
            pg_dump "$SUPABASE_URL" > "$db_backup_file"
            log_success "Database backup completed: $db_backup_file"
        else
            log_warning "pg_dump not found. Skipping database backup."
        fi
    else
        log_info "Backing up local PostgreSQL database..."
        if docker-compose ps postgres | grep -q "Up"; then
            docker-compose exec -T postgres pg_dump -U healthcare_user -d healthcare_voice_ai > "$db_backup_file"
            log_success "Database backup completed: $db_backup_file"
        else
            log_warning "PostgreSQL container not running. Skipping database backup."
        fi
    fi
    
    # Compress database backup
    if [[ -f "$db_backup_file" ]]; then
        gzip "$db_backup_file"
        log_success "Database backup compressed: $db_backup_file.gz"
    fi
}

# Application data backup
backup_application_data() {
    log_info "Starting application data backup..."
    
    local app_backup_file="$BACKUP_DIR/application/app_data_$DATE.tar.gz"
    
    # Backup uploads, logs, and quarantine directories
    tar -czf "$app_backup_file" \
        --exclude="*.log" \
        --exclude="*.tmp" \
        --exclude="node_modules" \
        --exclude=".git" \
        uploads/ \
        quarantine/ \
        temp/ \
        logs/ \
        2>/dev/null || true
    
    if [[ -f "$app_backup_file" ]]; then
        log_success "Application data backup completed: $app_backup_file"
    else
        log_warning "No application data to backup"
    fi
}

# Configuration backup
backup_configuration() {
    log_info "Starting configuration backup..."
    
    local config_backup_file="$BACKUP_DIR/config/config_$DATE.tar.gz"
    
    # Backup configuration files
    tar -czf "$config_backup_file" \
        .env* \
        docker-compose*.yml \
        nginx/ \
        monitoring/ \
        alembic.ini \
        pyproject.toml \
        2>/dev/null || true
    
    if [[ -f "$config_backup_file" ]]; then
        log_success "Configuration backup completed: $config_backup_file"
    else
        log_warning "No configuration files to backup"
    fi
}

# SSL certificates backup
backup_ssl_certificates() {
    log_info "Starting SSL certificates backup..."
    
    local ssl_backup_file="$BACKUP_DIR/ssl/ssl_certs_$DATE.tar.gz"
    
    # Backup SSL certificates if they exist
    if [[ -d "ssl" ]] || [[ -d "/etc/letsencrypt" ]]; then
        tar -czf "$ssl_backup_file" \
            ssl/ \
            /etc/letsencrypt/ \
            2>/dev/null || true
        
        if [[ -f "$ssl_backup_file" ]]; then
            log_success "SSL certificates backup completed: $ssl_backup_file"
        fi
    else
        log_info "No SSL certificates found to backup"
    fi
}

# Docker volumes backup
backup_docker_volumes() {
    log_info "Starting Docker volumes backup..."
    
    local volumes_backup_file="$BACKUP_DIR/application/docker_volumes_$DATE.tar.gz"
    
    # Get list of volumes
    local volumes=$(docker volume ls --format "{{.Name}}" | grep healthcare-voice-ai || true)
    
    if [[ -n "$volumes" ]]; then
        # Create temporary directory for volume backups
        local temp_dir=$(mktemp -d)
        
        for volume in $volumes; do
            log_info "Backing up volume: $volume"
            docker run --rm \
                -v "$volume":/source:ro \
                -v "$temp_dir":/backup \
                alpine:latest \
                tar -czf "/backup/$volume.tar.gz" -C /source .
        done
        
        # Compress all volume backups
        tar -czf "$volumes_backup_file" -C "$temp_dir" .
        rm -rf "$temp_dir"
        
        log_success "Docker volumes backup completed: $volumes_backup_file"
    else
        log_info "No Docker volumes found to backup"
    fi
}

# Create backup manifest
create_backup_manifest() {
    log_info "Creating backup manifest..."
    
    local manifest_file="$BACKUP_DIR/backup_manifest_$DATE.json"
    
    cat > "$manifest_file" << EOF
{
    "backup_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "backup_version": "1.0.0",
    "application_version": "${VERSION:-unknown}",
    "environment": "${ENVIRONMENT:-unknown}",
    "backup_files": [
EOF

    # Add backup files to manifest
    local first=true
    for file in "$BACKUP_DIR"/*/*_$DATE.*; do
        if [[ -f "$file" ]]; then
            if [[ "$first" == "true" ]]; then
                first=false
            else
                echo "," >> "$manifest_file"
            fi
            echo "        {" >> "$manifest_file"
            echo "            \"file\": \"$(basename "$file")\",\" >> "$manifest_file"
            echo "            \"path\": \"$file\",\" >> "$manifest_file"
            echo "            \"size\": $(stat -c%s "$file"),\" >> "$manifest_file"
            echo "            \"checksum\": \"$(sha256sum "$file" | cut -d' ' -f1)\"" >> "$manifest_file"
            echo -n "        }" >> "$manifest_file"
        fi
    done

    cat >> "$manifest_file" << EOF

    ],
    "system_info": {
        "hostname": "$(hostname)",
        "os": "$(uname -s)",
        "kernel": "$(uname -r)",
        "docker_version": "$(docker --version 2>/dev/null || echo 'not installed')",
        "docker_compose_version": "$(docker-compose --version 2>/dev/null || echo 'not installed')"
    }
}
EOF

    log_success "Backup manifest created: $manifest_file"
}

# Cleanup old backups
cleanup_old_backups() {
    log_info "Cleaning up old backups..."
    
    local retention_days="${BACKUP_RETENTION_DAYS:-30}"
    
    # Remove old backup files
    find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$retention_days -delete
    find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$retention_days -delete
    find "$BACKUP_DIR" -name "backup_manifest_*.json" -mtime +$retention_days -delete
    find "$BACKUP_DIR" -name "backup_*.log" -mtime +$retention_days -delete
    
    log_success "Old backups cleaned up (retention: $retention_days days)"
}

# Verify backup integrity
verify_backup() {
    log_info "Verifying backup integrity..."
    
    local manifest_file="$BACKUP_DIR/backup_manifest_$DATE.json"
    
    if [[ -f "$manifest_file" ]]; then
        # Verify each backup file
        while IFS= read -r line; do
            if [[ "$line" =~ \"file\":\ \"([^\"]+)\" ]]; then
                local file_name="${BASH_REMATCH[1]}"
                local file_path="$BACKUP_DIR"/*/"$file_name"
                
                if [[ -f $file_path ]]; then
                    local expected_checksum=$(grep -A 4 "\"file\": \"$file_name\"" "$manifest_file" | grep "\"checksum\":" | cut -d'"' -f4)
                    local actual_checksum=$(sha256sum "$file_path" | cut -d' ' -f1)
                    
                    if [[ "$expected_checksum" == "$actual_checksum" ]]; then
                        log_success "Backup file verified: $file_name"
                    else
                        log_error "Backup file verification failed: $file_name"
                        return 1
                    fi
                else
                    log_error "Backup file not found: $file_name"
                    return 1
                fi
            fi
        done < "$manifest_file"
        
        log_success "All backup files verified successfully"
    else
        log_error "Backup manifest not found"
        return 1
    fi
}

# Send backup notification
send_notification() {
    local status="$1"
    local message="$2"
    
    if [[ -n "${NOTIFICATION_EMAIL_TO:-}" ]] && command -v mail &> /dev/null; then
        echo "$message" | mail -s "Healthcare Voice AI Backup - $status" "$NOTIFICATION_EMAIL_TO"
        log_info "Notification sent to: $NOTIFICATION_EMAIL_TO"
    fi
}

# Main backup function
main() {
    log_info "Starting Healthcare Voice AI backup process..."
    log_info "Backup directory: $BACKUP_DIR"
    log_info "Backup date: $DATE"
    
    # Create backup directory
    create_backup_dir
    
    # Perform backups
    backup_database
    backup_application_data
    backup_configuration
    backup_ssl_certificates
    backup_docker_volumes
    
    # Create manifest
    create_backup_manifest
    
    # Verify backup
    if verify_backup; then
        log_success "Backup process completed successfully"
        send_notification "SUCCESS" "Backup completed successfully at $(date)"
    else
        log_error "Backup verification failed"
        send_notification "FAILED" "Backup verification failed at $(date)"
        exit 1
    fi
    
    # Cleanup old backups
    cleanup_old_backups
    
    log_success "Backup process completed successfully"
    log_info "Backup log: $LOG_FILE"
}

# Recovery function
recover() {
    local backup_date="$1"
    
    if [[ -z "$backup_date" ]]; then
        log_error "Backup date required for recovery"
        echo "Usage: $0 recover YYYYMMDD_HHMMSS"
        exit 1
    fi
    
    log_info "Starting recovery process for backup: $backup_date"
    
    local manifest_file="$BACKUP_DIR/backup_manifest_$backup_date.json"
    
    if [[ ! -f "$manifest_file" ]]; then
        log_error "Backup manifest not found: $manifest_file"
        exit 1
    fi
    
    # TODO: Implement recovery logic
    log_info "Recovery process not yet implemented"
}

# List available backups
list_backups() {
    log_info "Available backups:"
    
    if [[ -d "$BACKUP_DIR" ]]; then
        find "$BACKUP_DIR" -name "backup_manifest_*.json" | sort | while read -r manifest; do
            local backup_date=$(basename "$manifest" | sed 's/backup_manifest_\(.*\)\.json/\1/')
            local backup_size=$(du -sh "$BACKUP_DIR"/*/*_$backup_date.* 2>/dev/null | awk '{sum+=$1} END {print sum}' || echo "0")
            echo "  $backup_date - Size: $backup_size"
        done
    else
        log_warning "No backups found"
    fi
}

# Show usage
usage() {
    echo "Healthcare Voice AI Backup Script"
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  backup              Create a new backup"
    echo "  recover <date>      Recover from backup (YYYYMMDD_HHMMSS)"
    echo "  list                List available backups"
    echo "  cleanup             Clean up old backups"
    echo ""
    echo "Environment Variables:"
    echo "  BACKUP_DIR          Backup directory (default: /backups/healthcare-voice-ai)"
    echo "  BACKUP_RETENTION_DAYS Retention period in days (default: 30)"
    echo "  NOTIFICATION_EMAIL_TO Email address for notifications"
    echo ""
    echo "Examples:"
    echo "  $0 backup"
    echo "  $0 recover 20240115_143022"
    echo "  $0 list"
}

# Parse command line arguments
case "${1:-backup}" in
    backup)
        main
        ;;
    recover)
        recover "$2"
        ;;
    list)
        list_backups
        ;;
    cleanup)
        cleanup_old_backups
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        log_error "Unknown command: $1"
        usage
        exit 1
        ;;
esac
