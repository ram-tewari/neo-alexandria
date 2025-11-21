# PostgreSQL Backup and Recovery Guide

## Overview

This guide provides comprehensive procedures for backing up and restoring the Neo Alexandria PostgreSQL database. It covers multiple backup strategies, point-in-time recovery (PITR), and best practices for data protection.

## Table of Contents

1. [Backup Strategies](#backup-strategies)
2. [Backup Procedures](#backup-procedures)
3. [Point-in-Time Recovery (PITR)](#point-in-time-recovery-pitr)
4. [Restore Procedures](#restore-procedures)
5. [Automated Backup Script](#automated-backup-script)
6. [Backup Frequency and Retention](#backup-frequency-and-retention)
7. [Monitoring and Verification](#monitoring-and-verification)
8. [Troubleshooting](#troubleshooting)

---

## Backup Strategies

Neo Alexandria supports three primary backup strategies:

### 1. Logical Backups (pg_dump)

**Advantages:**
- Database-agnostic format (can restore to different PostgreSQL versions)
- Selective backup (specific tables or schemas)
- Human-readable SQL format option
- Cross-platform compatible

**Disadvantages:**
- Slower for large databases
- Requires more storage for plain SQL format
- Not suitable for point-in-time recovery

**Use Cases:**
- Development and staging environments
- Database migrations
- Selective table backups
- Cross-version upgrades

### 2. Physical Backups (pg_basebackup)

**Advantages:**
- Faster backup and restore for large databases
- Enables point-in-time recovery (PITR)
- Consistent snapshot of entire cluster
- Minimal performance impact

**Disadvantages:**
- Requires more storage (full cluster copy)
- Same PostgreSQL version required for restore
- Platform-specific (same architecture)

**Use Cases:**
- Production environments
- Disaster recovery planning
- High-availability setups
- Large databases (>100GB)

### 3. Continuous Archiving (WAL Archiving)

**Advantages:**
- Point-in-time recovery to any moment
- Minimal data loss (RPO < 1 minute)
- Incremental backup approach
- Supports streaming replication

**Disadvantages:**
- More complex setup
- Requires WAL archive storage
- Ongoing maintenance required

**Use Cases:**
- Mission-critical production systems
- Compliance requirements (audit trails)
- Zero-downtime recovery scenarios

---

## Backup Procedures

### Full Database Backup (Plain SQL Format)

The simplest backup format, creates a plain SQL script:

```bash
# Basic full backup
pg_dump -h localhost -U postgres -d neo_alexandria > backup.sql

# With timestamp
pg_dump -h localhost -U postgres -d neo_alexandria > backup_$(date +%Y%m%d_%H%M%S).sql

# Verbose output
pg_dump -h localhost -U postgres -d neo_alexandria -v > backup.sql
```

**Restore:**
```bash
psql -h localhost -U postgres -d neo_alexandria < backup.sql
```

### Compressed Backup (Gzip)

Reduces storage requirements by 70-90%:

```bash
# Create compressed backup
pg_dump -h localhost -U postgres -d neo_alexandria | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Restore from compressed backup
gunzip -c backup_20250120_120000.sql.gz | psql -h localhost -U postgres -d neo_alexandria
```

### Custom Format Backup (Recommended)

PostgreSQL's custom format provides the best balance of features:

```bash
# Create custom format backup
pg_dump -h localhost -U postgres -d neo_alexandria -Fc -f backup_$(date +%Y%m%d_%H%M%S).dump

# With compression level (0-9, default 6)
pg_dump -h localhost -U postgres -d neo_alexandria -Fc -Z9 -f backup.dump

# Parallel dump (faster for large databases)
pg_dump -h localhost -U postgres -d neo_alexandria -Fc -j 4 -f backup.dump
```

**Advantages of Custom Format:**
- Built-in compression
- Selective restore capability
- Parallel restore support
- Reordering of objects during restore
- More flexible than plain SQL

**Restore:**
```bash
# Full restore
pg_restore -h localhost -U postgres -d neo_alexandria -c backup.dump

# Parallel restore (4 jobs)
pg_restore -h localhost -U postgres -d neo_alexandria -j 4 backup.dump
```

### Directory Format Backup

Best for very large databases requiring parallel operations:

```bash
# Create directory format backup
pg_dump -h localhost -U postgres -d neo_alexandria -Fd -j 4 -f backup_dir/

# Restore from directory
pg_restore -h localhost -U postgres -d neo_alexandria -j 4 backup_dir/
```

### Selective Backups

Backup specific tables or schemas:

```bash
# Backup specific tables
pg_dump -h localhost -U postgres -d neo_alexandria -t resources -t citations -Fc -f resources_backup.dump

# Backup specific schema
pg_dump -h localhost -U postgres -d neo_alexandria -n public -Fc -f public_schema.dump

# Exclude specific tables
pg_dump -h localhost -U postgres -d neo_alexandria -T 'prediction_logs' -T 'user_interactions' -Fc -f backup.dump

# Schema only (no data)
pg_dump -h localhost -U postgres -d neo_alexandria -s -Fc -f schema_only.dump

# Data only (no schema)
pg_dump -h localhost -U postgres -d neo_alexandria -a -Fc -f data_only.dump
```

### Physical Backup (pg_basebackup)

For production environments requiring PITR:

```bash
# Create base backup
pg_basebackup -h localhost -U postgres -D /backup/base -Ft -z -P

# Options explained:
# -D: Output directory
# -Ft: Tar format
# -z: Compress with gzip
# -P: Show progress
# -X stream: Include WAL files in backup
```

---

## Point-in-Time Recovery (PITR)

PITR allows you to restore the database to any specific moment in time, essential for recovering from data corruption or accidental deletions.

### Prerequisites

1. **Enable WAL Archiving** in `postgresql.conf`:

```ini
# Enable archiving
wal_level = replica
archive_mode = on
archive_command = 'test ! -f /var/lib/postgresql/wal_archive/%f && cp %p /var/lib/postgresql/wal_archive/%f'

# Recommended settings
max_wal_senders = 3
wal_keep_size = 1GB
```

2. **Create WAL Archive Directory**:

```bash
mkdir -p /var/lib/postgresql/wal_archive
chown postgres:postgres /var/lib/postgresql/wal_archive
chmod 700 /var/lib/postgresql/wal_archive
```

3. **Restart PostgreSQL**:

```bash
sudo systemctl restart postgresql
```

### PITR Configuration Steps

#### Step 1: Create Base Backup

```bash
# Stop application to ensure consistency
docker-compose stop neo_alexandria

# Create base backup with WAL files
pg_basebackup -h localhost -U postgres \
  -D /backup/pitr/base_$(date +%Y%m%d_%H%M%S) \
  -Ft -z -P -X stream

# Restart application
docker-compose start neo_alexandria
```

#### Step 2: Continuous WAL Archiving

WAL files are automatically archived based on `archive_command`. Monitor the archive directory:

```bash
# Check WAL archive status
ls -lh /var/lib/postgresql/wal_archive/

# Monitor archive rate
watch -n 5 'ls /var/lib/postgresql/wal_archive/ | wc -l'
```

#### Step 3: Restore to Specific Point in Time

```bash
# Stop PostgreSQL
sudo systemctl stop postgresql

# Backup current data directory
mv /var/lib/postgresql/15/main /var/lib/postgresql/15/main.old

# Extract base backup
mkdir /var/lib/postgresql/15/main
tar -xzf /backup/pitr/base_20250120_120000/base.tar.gz -C /var/lib/postgresql/15/main

# Create recovery configuration
cat > /var/lib/postgresql/15/main/recovery.signal << EOF
# This file triggers recovery mode
EOF

# Configure recovery target in postgresql.conf or recovery.conf
cat >> /var/lib/postgresql/15/main/postgresql.auto.conf << EOF
restore_command = 'cp /var/lib/postgresql/wal_archive/%f %p'
recovery_target_time = '2025-01-20 14:30:00'
recovery_target_action = 'promote'
EOF

# Set permissions
chown -R postgres:postgres /var/lib/postgresql/15/main
chmod 700 /var/lib/postgresql/15/main

# Start PostgreSQL (will enter recovery mode)
sudo systemctl start postgresql

# Monitor recovery progress
tail -f /var/log/postgresql/postgresql-15-main.log
```

### Recovery Target Options

```ini
# Recover to specific timestamp
recovery_target_time = '2025-01-20 14:30:00'

# Recover to specific transaction ID
recovery_target_xid = '12345678'

# Recover to specific WAL location
recovery_target_lsn = '0/3000000'

# Recover to named restore point
recovery_target_name = 'before_migration'

# Recovery behavior after target
recovery_target_action = 'promote'  # or 'pause' or 'shutdown'
```

### Creating Named Restore Points

```sql
-- Create a restore point before risky operations
SELECT pg_create_restore_point('before_data_migration');

-- Later, recover to this point
-- recovery_target_name = 'before_data_migration'
```

---

## Restore Procedures

### Full Database Restore

#### From Plain SQL Backup

```bash
# Drop and recreate database
psql -h localhost -U postgres -c "DROP DATABASE IF EXISTS neo_alexandria;"
psql -h localhost -U postgres -c "CREATE DATABASE neo_alexandria;"

# Restore from backup
psql -h localhost -U postgres -d neo_alexandria < backup.sql

# Or with progress indicator
pv backup.sql | psql -h localhost -U postgres -d neo_alexandria
```

#### From Custom Format Backup

```bash
# Clean restore (drops existing objects)
pg_restore -h localhost -U postgres -d neo_alexandria -c -v backup.dump

# Create new database and restore
createdb -h localhost -U postgres neo_alexandria
pg_restore -h localhost -U postgres -d neo_alexandria backup.dump

# Parallel restore for faster performance
pg_restore -h localhost -U postgres -d neo_alexandria -j 4 backup.dump
```

### Partial Database Restore

#### Restore Specific Tables

```bash
# List available tables in backup
pg_restore -l backup.dump | grep TABLE

# Restore only specific tables
pg_restore -h localhost -U postgres -d neo_alexandria -t resources -t citations backup.dump

# Restore using table of contents file
pg_restore -l backup.dump > toc.list
# Edit toc.list to comment out unwanted items
pg_restore -h localhost -U postgres -d neo_alexandria -L toc.list backup.dump
```

#### Restore Schema Only

```bash
# Restore only schema (no data)
pg_restore -h localhost -U postgres -d neo_alexandria -s backup.dump
```

#### Restore Data Only

```bash
# Restore only data (assumes schema exists)
pg_restore -h localhost -U postgres -d neo_alexandria -a backup.dump
```

### Restore to Different Database

```bash
# Create new database
createdb -h localhost -U postgres neo_alexandria_restored

# Restore to new database
pg_restore -h localhost -U postgres -d neo_alexandria_restored backup.dump

# Or with SQL backup
psql -h localhost -U postgres -d neo_alexandria_restored < backup.sql
```

### Restore with Data Transformation

```bash
# Restore and modify data during restore
pg_restore -h localhost -U postgres -d neo_alexandria backup.dump | \
  sed 's/old_value/new_value/g' | \
  psql -h localhost -U postgres -d neo_alexandria
```

---

## Automated Backup Script

The automated backup script (`backend/scripts/backup_postgresql.sh`) provides:
- Scheduled backups with rotation
- Multiple backup formats
- Compression and encryption
- Verification and reporting
- Error handling and notifications

### Script Features

- **Multiple Backup Types**: Full, incremental, and WAL archiving
- **Compression**: Automatic gzip compression for space savings
- **Retention Policy**: Automatic cleanup of old backups
- **Verification**: Post-backup integrity checks
- **Notifications**: Email alerts on success/failure
- **Logging**: Detailed backup logs for auditing

### Usage

```bash
# Run manual backup
./backend/scripts/backup_postgresql.sh

# Schedule with cron (daily at 2 AM)
0 2 * * * /path/to/backend/scripts/backup_postgresql.sh >> /var/log/postgresql_backup.log 2>&1

# Run with custom configuration
BACKUP_DIR=/custom/path ./backend/scripts/backup_postgresql.sh
```

### Configuration

Edit the script variables or use environment variables:

```bash
# Database connection
export DB_HOST="localhost"
export DB_PORT="5432"
export DB_NAME="neo_alexandria"
export DB_USER="postgres"
export PGPASSWORD="your_password"

# Backup settings
export BACKUP_DIR="/var/backups/postgresql"
export RETENTION_DAYS="30"
export COMPRESSION_LEVEL="9"
```

---

## Backup Frequency and Retention

### Recommended Backup Schedule

#### Production Environment

| Backup Type | Frequency | Retention | Storage Location |
|-------------|-----------|-----------|------------------|
| Full Backup | Daily | 30 days | Off-site storage |
| Incremental | Hourly | 7 days | Local storage |
| WAL Archive | Continuous | 7 days | Local + off-site |
| Monthly Archive | Monthly | 12 months | Cold storage |

**Implementation:**
```bash
# Daily full backup (2 AM)
0 2 * * * /path/to/backup_postgresql.sh full

# Hourly incremental (WAL archiving handles this)
# Configured in postgresql.conf

# Monthly archive (1st of month, 3 AM)
0 3 1 * * /path/to/backup_postgresql.sh monthly
```

#### Staging Environment

| Backup Type | Frequency | Retention | Storage Location |
|-------------|-----------|-----------|------------------|
| Full Backup | Daily | 7 days | Local storage |
| WAL Archive | Continuous | 3 days | Local storage |

#### Development Environment

| Backup Type | Frequency | Retention | Storage Location |
|-------------|-----------|-----------|------------------|
| Full Backup | Weekly | 2 weeks | Local storage |
| Manual Backup | As needed | 1 week | Local storage |

### Retention Policy Guidelines

**Factors to Consider:**
1. **Compliance Requirements**: Legal/regulatory data retention mandates
2. **Storage Capacity**: Available disk space and costs
3. **Recovery Time Objective (RTO)**: How quickly you need to restore
4. **Recovery Point Objective (RPO)**: Maximum acceptable data loss

**Recommended Retention:**
- **Daily Backups**: 30 days (covers monthly reporting cycles)
- **Weekly Backups**: 12 weeks (covers quarterly reviews)
- **Monthly Backups**: 12 months (covers annual compliance)
- **Yearly Backups**: 7 years (common compliance requirement)

### Storage Recommendations

**Local Storage:**
- Fast SSD for recent backups (7 days)
- Minimum 3x database size
- RAID configuration for redundancy

**Off-site Storage:**
- Cloud storage (AWS S3, Google Cloud Storage, Azure Blob)
- Geographic redundancy
- Encryption at rest and in transit

**Cold Storage:**
- Glacier/Archive tier for long-term retention
- Lower cost per GB
- Longer retrieval times acceptable

### Backup Size Estimation

```bash
# Check current database size
psql -h localhost -U postgres -d neo_alexandria -c "SELECT pg_size_pretty(pg_database_size('neo_alexandria'));"

# Estimate compressed backup size (typically 20-30% of original)
# Example: 10GB database → ~2-3GB compressed backup

# Calculate monthly storage requirements
# Daily backups: 30 days × 3GB = 90GB
# Weekly backups: 12 weeks × 3GB = 36GB
# Monthly backups: 12 months × 3GB = 36GB
# Total: ~162GB for full retention policy
```

---

## Monitoring and Verification

### Backup Verification

Always verify backups after creation:

```bash
# Verify custom format backup
pg_restore -l backup.dump > /dev/null
echo $?  # Should return 0 for success

# Verify compressed backup
gunzip -t backup.sql.gz
echo $?  # Should return 0 for success

# Test restore to temporary database
createdb -h localhost -U postgres test_restore
pg_restore -h localhost -U postgres -d test_restore backup.dump
# Verify data integrity
psql -h localhost -U postgres -d test_restore -c "SELECT COUNT(*) FROM resources;"
dropdb -h localhost -U postgres test_restore
```

### Monitoring Backup Health

```bash
# Check last backup timestamp
ls -lht /var/backups/postgresql/ | head -n 5

# Verify backup file sizes
du -sh /var/backups/postgresql/*.dump

# Check WAL archive status
psql -h localhost -U postgres -c "SELECT * FROM pg_stat_archiver;"

# Monitor disk space
df -h /var/backups/postgresql/
```

### Automated Verification Script

```bash
#!/bin/bash
# verify_backups.sh

BACKUP_DIR="/var/backups/postgresql"
LATEST_BACKUP=$(ls -t ${BACKUP_DIR}/*.dump | head -n 1)

echo "Verifying backup: ${LATEST_BACKUP}"

# Test backup integrity
if pg_restore -l ${LATEST_BACKUP} > /dev/null 2>&1; then
    echo "✓ Backup integrity check passed"
else
    echo "✗ Backup integrity check FAILED"
    exit 1
fi

# Test restore to temporary database
TEST_DB="verify_restore_$(date +%s)"
createdb ${TEST_DB}

if pg_restore -d ${TEST_DB} ${LATEST_BACKUP} > /dev/null 2>&1; then
    echo "✓ Test restore successful"
    
    # Verify table counts
    TABLES=$(psql -d ${TEST_DB} -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';")
    echo "✓ Restored ${TABLES} tables"
    
    dropdb ${TEST_DB}
else
    echo "✗ Test restore FAILED"
    dropdb ${TEST_DB}
    exit 1
fi

echo "Backup verification complete"
```

### Backup Alerts

Configure email notifications for backup status:

```bash
# Add to backup script
if [ $? -eq 0 ]; then
    echo "Backup completed successfully" | mail -s "PostgreSQL Backup Success" admin@example.com
else
    echo "Backup FAILED - immediate attention required" | mail -s "PostgreSQL Backup FAILURE" admin@example.com
fi
```

---

## Troubleshooting

### Common Backup Issues

#### Issue: "permission denied" Error

**Cause**: Insufficient file system permissions

**Solution:**
```bash
# Ensure backup directory is writable
chmod 755 /var/backups/postgresql
chown postgres:postgres /var/backups/postgresql

# Or run as postgres user
sudo -u postgres pg_dump -d neo_alexandria -Fc -f backup.dump
```

#### Issue: "out of memory" During Backup

**Cause**: Large database or insufficient system memory

**Solution:**
```bash
# Use custom format with compression
pg_dump -d neo_alexandria -Fc -Z6 -f backup.dump

# Or use directory format with parallel jobs
pg_dump -d neo_alexandria -Fd -j 4 -f backup_dir/

# Increase maintenance_work_mem temporarily
psql -c "SET maintenance_work_mem = '1GB';"
```

#### Issue: Backup Takes Too Long

**Cause**: Large database, slow disk, or network latency

**Solution:**
```bash
# Use parallel dump
pg_dump -d neo_alexandria -Fc -j 4 -f backup.dump

# Exclude large tables that can be regenerated
pg_dump -d neo_alexandria -T 'prediction_logs' -T 'user_interactions' -Fc -f backup.dump

# Use directory format for better parallelization
pg_dump -d neo_alexandria -Fd -j 8 -f backup_dir/
```

#### Issue: WAL Archive Directory Filling Up

**Cause**: WAL files not being cleaned up properly

**Solution:**
```bash
# Check archive status
psql -c "SELECT * FROM pg_stat_archiver;"

# Manually clean old WAL files (older than 7 days)
find /var/lib/postgresql/wal_archive/ -name "*.backup" -mtime +7 -delete
find /var/lib/postgresql/wal_archive/ -name "0*" -mtime +7 -delete

# Configure automatic cleanup in postgresql.conf
wal_keep_size = 1GB
```

### Common Restore Issues

#### Issue: "database already exists" Error

**Cause**: Target database exists

**Solution:**
```bash
# Drop existing database first
dropdb -h localhost -U postgres neo_alexandria

# Or use -c flag to clean before restore
pg_restore -d neo_alexandria -c backup.dump
```

#### Issue: Foreign Key Constraint Violations

**Cause**: Data restored in wrong order

**Solution:**
```bash
# Disable triggers during restore
pg_restore -d neo_alexandria --disable-triggers backup.dump

# Or restore with single transaction
pg_restore -d neo_alexandria -1 backup.dump
```

#### Issue: Restore Fails with "role does not exist"

**Cause**: Backup contains role/user references not in target

**Solution:**
```bash
# Restore without owner information
pg_restore -d neo_alexandria --no-owner backup.dump

# Or create missing roles first
psql -c "CREATE ROLE missing_user;"
```

### Recovery Verification

After restore, verify data integrity:

```bash
# Check table counts
psql -d neo_alexandria -c "
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
       (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = tablename) AS columns
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"

# Verify foreign key constraints
psql -d neo_alexandria -c "
SELECT conname, conrelid::regclass, confrelid::regclass
FROM pg_constraint
WHERE contype = 'f';
"

# Check for missing indexes
psql -d neo_alexandria -c "
SELECT schemaname, tablename, indexname
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
"

# Run application health checks
curl http://localhost:8000/health
curl http://localhost:8000/monitoring/database
```

---

## Best Practices

### Security

1. **Encrypt Backups**: Use GPG or database-level encryption
   ```bash
   pg_dump -d neo_alexandria -Fc | gpg --encrypt --recipient admin@example.com > backup.dump.gpg
   ```

2. **Secure Credentials**: Use `.pgpass` file instead of environment variables
   ```bash
   echo "localhost:5432:neo_alexandria:postgres:password" > ~/.pgpass
   chmod 600 ~/.pgpass
   ```

3. **Restrict Backup Access**: Limit file permissions
   ```bash
   chmod 600 /var/backups/postgresql/*.dump
   ```

### Performance

1. **Schedule During Low Traffic**: Run backups during off-peak hours
2. **Use Parallel Operations**: Leverage `-j` flag for large databases
3. **Monitor Impact**: Check `pg_stat_activity` during backups

### Reliability

1. **Test Restores Regularly**: Monthly restore drills
2. **Verify Backup Integrity**: Automated verification after each backup
3. **Multiple Backup Locations**: Local + off-site redundancy
4. **Document Procedures**: Keep runbooks updated

### Compliance

1. **Audit Logs**: Maintain backup/restore logs for compliance
2. **Retention Policies**: Follow regulatory requirements
3. **Access Controls**: Track who performs backup/restore operations
4. **Encryption**: Meet data protection standards

---

## Additional Resources

- [PostgreSQL Backup Documentation](https://www.postgresql.org/docs/current/backup.html)
- [pg_dump Reference](https://www.postgresql.org/docs/current/app-pgdump.html)
- [pg_restore Reference](https://www.postgresql.org/docs/current/app-pgrestore.html)
- [pg_basebackup Reference](https://www.postgresql.org/docs/current/app-pgbasebackup.html)
- [WAL Archiving Guide](https://www.postgresql.org/docs/current/continuous-archiving.html)

---

## Support

For backup and recovery assistance:
- Check logs: `/var/log/postgresql/postgresql-15-main.log`
- Review backup logs: `/var/log/postgresql_backup.log`
- Contact: Database Administrator Team
- Emergency: Follow incident response procedures

---

**Document Version**: 1.0  
**Last Updated**: January 20, 2025  
**Maintained By**: Neo Alexandria DevOps Team
