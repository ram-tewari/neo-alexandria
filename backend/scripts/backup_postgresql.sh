#!/bin/bash

################################################################################
# PostgreSQL Backup Script for Neo Alexandria
# 
# This script performs automated backups of the PostgreSQL database with:
# - Multiple backup formats (custom, compressed SQL)
# - Automatic rotation and cleanup
# - Verification and integrity checks
# - Detailed logging and error handling
# - Email notifications (optional)
#
# Usage:
#   ./backup_postgresql.sh [full|incremental|monthly]
#
# Environment Variables:
#   DB_HOST          - Database host (default: localhost)
#   DB_PORT          - Database port (default: 5432)
#   DB_NAME          - Database name (default: neo_alexandria)
#   DB_USER          - Database user (default: postgres)
#   PGPASSWORD       - Database password (use .pgpass for security)
#   BACKUP_DIR       - Backup directory (default: /var/backups/postgresql)
#   RETENTION_DAYS   - Days to keep backups (default: 30)
#   COMPRESSION      - Compression level 0-9 (default: 6)
#   ENABLE_EMAIL     - Send email notifications (default: false)
#   EMAIL_TO         - Email recipient for notifications
#
# Cron Example:
#   # Daily backup at 2 AM
#   0 2 * * * /path/to/backup_postgresql.sh full >> /var/log/postgresql_backup.log 2>&1
#
################################################################################

set -euo pipefail  # Exit on error, undefined variables, and pipe failures

################################################################################
# Configuration
################################################################################

# Database connection settings
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-neo_alexandria}"
DB_USER="${DB_USER:-postgres}"

# Backup settings
BACKUP_DIR="${BACKUP_DIR:-/var/backups/postgresql}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
RETENTION_WEEKS="${RETENTION_WEEKS:-12}"
RETENTION_MONTHS="${RETENTION_MONTHS:-12}"
COMPRESSION_LEVEL="${COMPRESSION_LEVEL:-6}"

# Notification settings
ENABLE_EMAIL="${ENABLE_EMAIL:-false}"
EMAIL_TO="${EMAIL_TO:-admin@example.com}"
EMAIL_FROM="${EMAIL_FROM:-postgresql-backup@example.com}"

# Backup type (full, incremental, monthly)
BACKUP_TYPE="${1:-full}"

# Timestamp for backup files
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATE_ONLY=$(date +%Y%m%d)

# Log file
LOG_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}.log"

# Backup file paths
BACKUP_CUSTOM="${BACKUP_DIR}/backup_${BACKUP_TYPE}_${TIMESTAMP}.dump"
BACKUP_SQL="${BACKUP_DIR}/backup_${BACKUP_TYPE}_${TIMESTAMP}.sql.gz"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

################################################################################
# Functions
################################################################################

# Log message with timestamp
log() {
    local level="$1"
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] [${level}] ${message}" | tee -a "${LOG_FILE}"
}

# Log info message
log_info() {
    log "INFO" "$@"
    echo -e "${GREEN}✓${NC} $@"
}

# Log warning message
log_warn() {
    log "WARN" "$@"
    echo -e "${YELLOW}⚠${NC} $@"
}

# Log error message
log_error() {
    log "ERROR" "$@"
    echo -e "${RED}✗${NC} $@"
}

# Send email notification
send_email() {
    local subject="$1"
    local body="$2"
    
    if [ "${ENABLE_EMAIL}" = "true" ]; then
        echo "${body}" | mail -s "${subject}" -r "${EMAIL_FROM}" "${EMAIL_TO}"
        log_info "Email notification sent to ${EMAIL_TO}"
    fi
}

# Check if required commands are available
check_dependencies() {
    local missing_deps=()
    
    for cmd in pg_dump pg_restore psql gzip; do
        if ! command -v ${cmd} &> /dev/null; then
            missing_deps+=("${cmd}")
        fi
    done
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        log_error "Missing required commands: ${missing_deps[*]}"
        log_error "Please install PostgreSQL client tools"
        exit 1
    fi
    
    log_info "All required dependencies are available"
}

# Create backup directory if it doesn't exist
setup_backup_directory() {
    if [ ! -d "${BACKUP_DIR}" ]; then
        log_info "Creating backup directory: ${BACKUP_DIR}"
        mkdir -p "${BACKUP_DIR}"
        chmod 700 "${BACKUP_DIR}"
    fi
    
    # Check if directory is writable
    if [ ! -w "${BACKUP_DIR}" ]; then
        log_error "Backup directory is not writable: ${BACKUP_DIR}"
        exit 1
    fi
    
    log_info "Backup directory ready: ${BACKUP_DIR}"
}

# Check database connectivity
check_database_connection() {
    log_info "Testing database connection..."
    
    if psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" -c "SELECT 1;" > /dev/null 2>&1; then
        log_info "Database connection successful"
        return 0
    else
        log_error "Failed to connect to database"
        log_error "Host: ${DB_HOST}:${DB_PORT}, Database: ${DB_NAME}, User: ${DB_USER}"
        return 1
    fi
}

# Get database size
get_database_size() {
    local size=$(psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" -t -c "SELECT pg_size_pretty(pg_database_size('${DB_NAME}'));")
    echo "${size}" | xargs  # Trim whitespace
}

# Perform custom format backup
backup_custom_format() {
    log_info "Starting custom format backup..."
    log_info "Database: ${DB_NAME}, Size: $(get_database_size)"
    
    local start_time=$(date +%s)
    
    # Perform backup with progress
    if pg_dump -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" \
        -Fc -Z"${COMPRESSION_LEVEL}" -v -f "${BACKUP_CUSTOM}" 2>&1 | tee -a "${LOG_FILE}"; then
        
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        local backup_size=$(du -h "${BACKUP_CUSTOM}" | cut -f1)
        
        log_info "Custom format backup completed in ${duration} seconds"
        log_info "Backup file: ${BACKUP_CUSTOM}"
        log_info "Backup size: ${backup_size}"
        
        return 0
    else
        log_error "Custom format backup failed"
        return 1
    fi
}

# Perform compressed SQL backup
backup_sql_format() {
    log_info "Starting compressed SQL backup..."
    
    local start_time=$(date +%s)
    
    # Perform backup with compression
    if pg_dump -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" -v \
        2>&1 | tee -a "${LOG_FILE}" | gzip -"${COMPRESSION_LEVEL}" > "${BACKUP_SQL}"; then
        
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        local backup_size=$(du -h "${BACKUP_SQL}" | cut -f1)
        
        log_info "Compressed SQL backup completed in ${duration} seconds"
        log_info "Backup file: ${BACKUP_SQL}"
        log_info "Backup size: ${backup_size}"
        
        return 0
    else
        log_error "Compressed SQL backup failed"
        return 1
    fi
}

# Verify backup integrity
verify_backup() {
    local backup_file="$1"
    
    log_info "Verifying backup integrity: ${backup_file}"
    
    if [[ "${backup_file}" == *.dump ]]; then
        # Verify custom format backup
        if pg_restore -l "${backup_file}" > /dev/null 2>&1; then
            log_info "Backup integrity check passed"
            return 0
        else
            log_error "Backup integrity check failed"
            return 1
        fi
    elif [[ "${backup_file}" == *.sql.gz ]]; then
        # Verify compressed SQL backup
        if gunzip -t "${backup_file}" 2>&1 | tee -a "${LOG_FILE}"; then
            log_info "Backup integrity check passed"
            return 0
        else
            log_error "Backup integrity check failed"
            return 1
        fi
    else
        log_warn "Unknown backup format, skipping verification"
        return 0
    fi
}

# Test restore to temporary database (optional, resource-intensive)
test_restore() {
    local backup_file="$1"
    local test_db="test_restore_${TIMESTAMP}"
    
    log_info "Testing restore to temporary database: ${test_db}"
    
    # Create temporary database
    if ! psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -c "CREATE DATABASE ${test_db};" > /dev/null 2>&1; then
        log_warn "Failed to create test database, skipping restore test"
        return 0
    fi
    
    # Attempt restore
    local restore_success=false
    if [[ "${backup_file}" == *.dump ]]; then
        if pg_restore -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${test_db}" "${backup_file}" > /dev/null 2>&1; then
            restore_success=true
        fi
    elif [[ "${backup_file}" == *.sql.gz ]]; then
        if gunzip -c "${backup_file}" | psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${test_db}" > /dev/null 2>&1; then
            restore_success=true
        fi
    fi
    
    # Cleanup test database
    psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -c "DROP DATABASE ${test_db};" > /dev/null 2>&1
    
    if [ "${restore_success}" = true ]; then
        log_info "Test restore successful"
        return 0
    else
        log_error "Test restore failed"
        return 1
    fi
}

# Cleanup old backups based on retention policy
cleanup_old_backups() {
    log_info "Cleaning up old backups..."
    
    local deleted_count=0
    
    # Daily backups: keep for RETENTION_DAYS
    log_info "Removing daily backups older than ${RETENTION_DAYS} days"
    while IFS= read -r file; do
        rm -f "${file}"
        log_info "Deleted: ${file}"
        ((deleted_count++))
    done < <(find "${BACKUP_DIR}" -name "backup_full_*.dump" -mtime +${RETENTION_DAYS} 2>/dev/null)
    
    while IFS= read -r file; do
        rm -f "${file}"
        log_info "Deleted: ${file}"
        ((deleted_count++))
    done < <(find "${BACKUP_DIR}" -name "backup_full_*.sql.gz" -mtime +${RETENTION_DAYS} 2>/dev/null)
    
    # Weekly backups: keep for RETENTION_WEEKS
    log_info "Removing weekly backups older than ${RETENTION_WEEKS} weeks"
    local weeks_in_days=$((RETENTION_WEEKS * 7))
    while IFS= read -r file; do
        rm -f "${file}"
        log_info "Deleted: ${file}"
        ((deleted_count++))
    done < <(find "${BACKUP_DIR}" -name "backup_incremental_*.dump" -mtime +${weeks_in_days} 2>/dev/null)
    
    # Monthly backups: keep for RETENTION_MONTHS
    log_info "Removing monthly backups older than ${RETENTION_MONTHS} months"
    local months_in_days=$((RETENTION_MONTHS * 30))
    while IFS= read -r file; do
        rm -f "${file}"
        log_info "Deleted: ${file}"
        ((deleted_count++))
    done < <(find "${BACKUP_DIR}" -name "backup_monthly_*.dump" -mtime +${months_in_days} 2>/dev/null)
    
    # Cleanup old log files (keep for 90 days)
    while IFS= read -r file; do
        rm -f "${file}"
        ((deleted_count++))
    done < <(find "${BACKUP_DIR}" -name "backup_*.log" -mtime +90 2>/dev/null)
    
    log_info "Cleanup complete: ${deleted_count} files deleted"
}

# Generate backup report
generate_report() {
    local status="$1"
    local backup_file="$2"
    
    log_info "Generating backup report..."
    
    local report="${BACKUP_DIR}/backup_report_${TIMESTAMP}.txt"
    
    cat > "${report}" << EOF
================================================================================
PostgreSQL Backup Report
================================================================================

Backup Information:
  Date/Time:        $(date '+%Y-%m-%d %H:%M:%S')
  Backup Type:      ${BACKUP_TYPE}
  Status:           ${status}
  
Database Information:
  Host:             ${DB_HOST}:${DB_PORT}
  Database:         ${DB_NAME}
  User:             ${DB_USER}
  Database Size:    $(get_database_size)

Backup Files:
  Custom Format:    ${BACKUP_CUSTOM}
  SQL Format:       ${BACKUP_SQL}

Storage Information:
  Backup Directory: ${BACKUP_DIR}
  Total Backups:    $(ls -1 ${BACKUP_DIR}/backup_*.dump 2>/dev/null | wc -l)
  Disk Usage:       $(du -sh ${BACKUP_DIR} | cut -f1)
  Available Space:  $(df -h ${BACKUP_DIR} | tail -1 | awk '{print $4}')

Retention Policy:
  Daily Backups:    ${RETENTION_DAYS} days
  Weekly Backups:   ${RETENTION_WEEKS} weeks
  Monthly Backups:  ${RETENTION_MONTHS} months

Log File:
  ${LOG_FILE}

================================================================================
EOF
    
    cat "${report}"
    log_info "Report saved to: ${report}"
}

# Main backup function
perform_backup() {
    log_info "=========================================="
    log_info "PostgreSQL Backup Started"
    log_info "Backup Type: ${BACKUP_TYPE}"
    log_info "=========================================="
    
    local backup_status="SUCCESS"
    local backup_file=""
    
    # Perform custom format backup
    if backup_custom_format; then
        backup_file="${BACKUP_CUSTOM}"
        
        # Verify backup
        if ! verify_backup "${backup_file}"; then
            backup_status="FAILED"
            log_error "Backup verification failed"
        fi
    else
        backup_status="FAILED"
        log_error "Backup creation failed"
    fi
    
    # Optionally create SQL backup as well
    if [ "${backup_status}" = "SUCCESS" ] && [ "${BACKUP_TYPE}" = "monthly" ]; then
        log_info "Creating additional SQL backup for monthly archive"
        backup_sql_format
    fi
    
    # Cleanup old backups
    if [ "${backup_status}" = "SUCCESS" ]; then
        cleanup_old_backups
    fi
    
    # Generate report
    generate_report "${backup_status}" "${backup_file}"
    
    log_info "=========================================="
    log_info "PostgreSQL Backup Completed: ${backup_status}"
    log_info "=========================================="
    
    # Send notification
    if [ "${backup_status}" = "SUCCESS" ]; then
        send_email "PostgreSQL Backup Success - ${DB_NAME}" \
            "Backup completed successfully.\n\nBackup Type: ${BACKUP_TYPE}\nDatabase: ${DB_NAME}\nBackup File: ${backup_file}\nSize: $(du -h ${backup_file} | cut -f1)"
        return 0
    else
        send_email "PostgreSQL Backup FAILED - ${DB_NAME}" \
            "Backup failed. Please check logs immediately.\n\nBackup Type: ${BACKUP_TYPE}\nDatabase: ${DB_NAME}\nLog File: ${LOG_FILE}"
        return 1
    fi
}

################################################################################
# Main Script
################################################################################

main() {
    # Check dependencies
    check_dependencies
    
    # Setup backup directory
    setup_backup_directory
    
    # Check database connection
    if ! check_database_connection; then
        log_error "Cannot proceed without database connection"
        exit 1
    fi
    
    # Perform backup
    if perform_backup; then
        log_info "Backup process completed successfully"
        exit 0
    else
        log_error "Backup process failed"
        exit 1
    fi
}

# Run main function
main "$@"
