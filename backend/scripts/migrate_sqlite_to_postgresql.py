#!/usr/bin/env python3
"""
Neo Alexandria 2.0 - SQLite to PostgreSQL Data Migration Script

This script migrates all data from a SQLite database to PostgreSQL with validation
and progress reporting. It handles table dependencies, batch processing, and
provides detailed migration statistics.

Usage:
    python migrate_sqlite_to_postgresql.py \\
        --source sqlite:///backend.db \\
        --target postgresql://user:pass@localhost:5432/neo_alexandria \\
        --validate

Features:
- Automatic table dependency resolution
- Batch processing (1000 records per batch) to prevent memory exhaustion
- Progress reporting with row counts
- Schema validation before migration
- Data validation after migration
- Detailed migration report with statistics and errors
- Dry-run mode for testing

Related files:
- app/database/models.py: Database models defining table structure
- app/database/base.py: Database engine configuration
- alembic/versions/: Schema migration scripts
"""

import argparse
import sys
import logging
from datetime import datetime
from typing import Dict, List, Any

from sqlalchemy import create_engine, inspect, MetaData, select, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)


class DatabaseMigrator:
    """
    Handles data migration from SQLite to PostgreSQL with validation and reporting.
    
    This class manages the complete migration process including:
    - Schema validation
    - Table dependency ordering
    - Batch data transfer
    - Progress reporting
    - Data validation
    - Error handling and reporting
    """
    
    # Table migration order respecting foreign key dependencies
    # Tables with no dependencies first, then tables that depend on them
    TABLE_ORDER = [
        # Independent tables (no foreign keys)
        'classification_codes',
        'authority_subjects',
        'authority_creators',
        'authority_publishers',
        'users',
        'model_versions',
        
        # Tables depending on users
        'user_profiles',
        
        # Resources (depends on nothing, but many tables depend on it)
        'resources',
        
        # Tables depending on resources
        'citations',
        'annotations',
        'graph_embeddings',
        'user_interactions',
        'recommendation_feedback',
        
        # Collections (can have self-reference via parent_id)
        'collections',
        
        # Tables depending on collections and resources
        'collection_resources',
        
        # Taxonomy (can have self-reference via parent_id)
        'taxonomy_nodes',
        
        # Tables depending on taxonomy and resources
        'resource_taxonomy',
        
        # Graph edges (depends on resources)
        'graph_edges',
        
        # Discovery hypotheses (depends on resources)
        'discovery_hypotheses',
        
        # A/B testing tables
        'ab_test_experiments',  # depends on model_versions
        'prediction_logs',       # depends on experiments, model_versions, users
        
        # Retraining runs (depends on model_versions)
        'retraining_runs',
    ]
    
    def __init__(self, source_url: str, target_url: str, batch_size: int = 1000, dry_run: bool = False):
        """
        Initialize the database migrator.
        
        Args:
            source_url: SQLite database connection URL
            target_url: PostgreSQL database connection URL
            batch_size: Number of records to process per batch (default: 1000)
            dry_run: If True, validate but don't migrate data
        """
        self.source_url = source_url
        self.target_url = target_url
        self.batch_size = batch_size
        self.dry_run = dry_run
        
        # Statistics tracking
        self.stats: Dict[str, Dict[str, Any]] = {}
        self.errors: List[Dict[str, Any]] = []
        self.start_time: datetime | None = None
        self.end_time: datetime | None = None
        
        # Database connections
        self.source_engine = None
        self.target_engine = None
        self.source_session = None
        self.target_session = None
        
        logger.info("Initialized DatabaseMigrator")
        logger.info(f"Source: {source_url}")
        logger.info(f"Target: {target_url}")
        logger.info(f"Batch size: {batch_size}")
        logger.info(f"Dry run: {dry_run}")
    
    def connect(self) -> None:
        """Establish connections to source and target databases."""
        try:
            logger.info("Connecting to source database...")
            self.source_engine = create_engine(self.source_url, echo=False)
            self.source_session = sessionmaker(bind=self.source_engine)()
            
            logger.info("Connecting to target database...")
            self.target_engine = create_engine(self.target_url, echo=False)
            self.target_session = sessionmaker(bind=self.target_engine)()
            
            logger.info("Database connections established successfully")
        except SQLAlchemyError as e:
            logger.error(f"Failed to connect to databases: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close database connections."""
        if self.source_session:
            self.source_session.close()
        if self.target_session:
            self.target_session.close()
        if self.source_engine:
            self.source_engine.dispose()
        if self.target_engine:
            self.target_engine.dispose()
        logger.info("Database connections closed")
    
    def validate_schemas(self) -> bool:
        """
        Validate that all required tables exist in both databases.
        
        Returns:
            True if all tables exist in both databases, False otherwise
        """
        logger.info("Validating database schemas...")
        
        source_inspector = inspect(self.source_engine)
        target_inspector = inspect(self.target_engine)
        
        source_tables = set(source_inspector.get_table_names())
        target_tables = set(target_inspector.get_table_names())
        
        logger.info(f"Source database tables: {len(source_tables)}")
        logger.info(f"Target database tables: {len(target_tables)}")
        
        # Check for missing tables in target
        missing_in_target = source_tables - target_tables
        if missing_in_target:
            logger.error(f"Tables missing in target database: {missing_in_target}")
            return False
        
        # Validate each table in migration order
        validation_passed = True
        for table_name in self.TABLE_ORDER:
            if table_name not in source_tables:
                logger.warning(f"Table '{table_name}' not found in source database (skipping)")
                continue
            
            if table_name not in target_tables:
                logger.error(f"Table '{table_name}' not found in target database")
                validation_passed = False
                continue
            
            # Get column information
            source_columns = {col['name']: col for col in source_inspector.get_columns(table_name)}
            target_columns = {col['name']: col for col in target_inspector.get_columns(table_name)}
            
            # Check for missing columns
            missing_columns = set(source_columns.keys()) - set(target_columns.keys())
            if missing_columns:
                logger.warning(f"Table '{table_name}': columns in source but not in target: {missing_columns}")
            
            logger.debug(f"Table '{table_name}': validated successfully")
        
        if validation_passed:
            logger.info("Schema validation passed")
        else:
            logger.error("Schema validation failed")
        
        return validation_passed
    
    def get_row_count(self, session: Session, table_name: str) -> int:
        """
        Get the number of rows in a table.
        
        Args:
            session: Database session
            table_name: Name of the table
            
        Returns:
            Number of rows in the table
        """
        try:
            result = session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            return result.scalar() or 0
        except SQLAlchemyError as e:
            logger.error(f"Error counting rows in {table_name}: {e}")
            return 0
    
    def migrate_table(self, table_name: str) -> Dict[str, Any]:
        """
        Migrate a single table from source to target database.
        
        Args:
            table_name: Name of the table to migrate
            
        Returns:
            Dictionary with migration statistics for this table
        """
        logger.info(f"Starting migration of table: {table_name}")
        
        stats = {
            'table_name': table_name,
            'source_count': 0,
            'migrated_count': 0,
            'target_count': 0,
            'success': False,
            'errors': [],
            'start_time': datetime.now()
        }
        
        try:
            # Get source row count
            stats['source_count'] = self.get_row_count(self.source_session, table_name)
            logger.info(f"Table '{table_name}': {stats['source_count']} rows in source")
            
            if stats['source_count'] == 0:
                logger.info(f"Table '{table_name}': no data to migrate")
                stats['success'] = True
                stats['end_time'] = datetime.now()
                return stats
            
            if self.dry_run:
                logger.info(f"Table '{table_name}': dry run mode, skipping data migration")
                stats['success'] = True
                stats['end_time'] = datetime.now()
                return stats
            
            # Get table metadata
            metadata = MetaData()
            metadata.reflect(bind=self.source_engine, only=[table_name])
            table = metadata.tables[table_name]
            
            # Migrate in batches
            offset = 0
            migrated = 0
            
            while offset < stats['source_count']:
                try:
                    # Fetch batch from source
                    batch_query = select(table).limit(self.batch_size).offset(offset)
                    batch_result = self.source_session.execute(batch_query)
                    batch_rows = batch_result.fetchall()
                    
                    if not batch_rows:
                        break
                    
                    # Convert rows to dictionaries
                    batch_data = [dict(row._mapping) for row in batch_rows]
                    
                    # Insert batch into target
                    self.target_session.execute(table.insert(), batch_data)
                    self.target_session.commit()
                    
                    migrated += len(batch_rows)
                    offset += self.batch_size
                    
                    # Progress reporting
                    progress_pct = (migrated / stats['source_count']) * 100
                    logger.info(f"Table '{table_name}': migrated {migrated}/{stats['source_count']} rows ({progress_pct:.1f}%)")
                    
                except SQLAlchemyError as e:
                    logger.error(f"Error migrating batch at offset {offset} for table '{table_name}': {e}")
                    self.target_session.rollback()
                    stats['errors'].append({
                        'offset': offset,
                        'error': str(e)
                    })
                    # Continue with next batch
                    offset += self.batch_size
            
            stats['migrated_count'] = migrated
            
            # Verify target row count
            stats['target_count'] = self.get_row_count(self.target_session, table_name)
            stats['success'] = (stats['source_count'] == stats['target_count'])
            
            if stats['success']:
                logger.info(f"Table '{table_name}': migration completed successfully")
            else:
                logger.warning(f"Table '{table_name}': row count mismatch (source: {stats['source_count']}, target: {stats['target_count']})")
            
        except Exception as e:
            logger.error(f"Fatal error migrating table '{table_name}': {e}")
            stats['errors'].append({
                'type': 'fatal',
                'error': str(e)
            })
            stats['success'] = False
        
        stats['end_time'] = datetime.now()
        return stats
    
    def migrate_tables(self) -> None:
        """Migrate all tables in dependency order."""
        logger.info("Starting table migration...")
        logger.info(f"Tables to migrate: {len(self.TABLE_ORDER)}")
        
        # Get list of tables that exist in source
        source_inspector = inspect(self.source_engine)
        source_tables = set(source_inspector.get_table_names())
        
        for table_name in self.TABLE_ORDER:
            if table_name not in source_tables:
                logger.info(f"Table '{table_name}' not found in source database, skipping")
                continue
            
            table_stats = self.migrate_table(table_name)
            self.stats[table_name] = table_stats
            
            if table_stats['errors']:
                self.errors.extend([
                    {'table': table_name, **error}
                    for error in table_stats['errors']
                ])
        
        logger.info("Table migration completed")
    
    def validate_data(self) -> bool:
        """
        Validate that row counts match between source and target for all tables.
        
        Returns:
            True if all row counts match, False otherwise
        """
        logger.info("Validating migrated data...")
        
        validation_passed = True
        
        for table_name, stats in self.stats.items():
            if stats['source_count'] != stats['target_count']:
                logger.error(
                    f"Table '{table_name}': row count mismatch "
                    f"(source: {stats['source_count']}, target: {stats['target_count']})"
                )
                validation_passed = False
            else:
                logger.debug(f"Table '{table_name}': row counts match ({stats['source_count']} rows)")
        
        if validation_passed:
            logger.info("Data validation passed")
        else:
            logger.error("Data validation failed")
        
        return validation_passed
    
    def generate_report(self) -> str:
        """
        Generate a detailed migration report.
        
        Returns:
            Formatted migration report as a string
        """
        report_lines = [
            "=" * 80,
            "DATABASE MIGRATION REPORT",
            "=" * 80,
            "",
            f"Migration Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Source Database: {self.source_url}",
            f"Target Database: {self.target_url}",
            f"Batch Size: {self.batch_size}",
            f"Dry Run: {self.dry_run}",
            ""
        ]
        
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            report_lines.extend([
                f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}",
                f"End Time: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}",
                f"Duration: {duration}",
                ""
            ])
        
        # Summary statistics
        total_source = sum(stats['source_count'] for stats in self.stats.values())
        total_target = sum(stats['target_count'] for stats in self.stats.values())
        successful_tables = sum(1 for stats in self.stats.values() if stats['success'])
        failed_tables = len(self.stats) - successful_tables
        
        report_lines.extend([
            "SUMMARY",
            "-" * 80,
            f"Tables Processed: {len(self.stats)}",
            f"Successful: {successful_tables}",
            f"Failed: {failed_tables}",
            f"Total Rows (Source): {total_source:,}",
            f"Total Rows (Target): {total_target:,}",
            f"Total Errors: {len(self.errors)}",
            ""
        ])
        
        # Per-table statistics
        report_lines.extend([
            "TABLE STATISTICS",
            "-" * 80,
            f"{'Table':<30} {'Source':<12} {'Target':<12} {'Status':<10} {'Errors':<8}",
            "-" * 80
        ])
        
        for table_name in self.TABLE_ORDER:
            if table_name not in self.stats:
                continue
            
            stats = self.stats[table_name]
            status = "✓ Success" if stats['success'] else "✗ Failed"
            error_count = len(stats['errors'])
            
            report_lines.append(
                f"{table_name:<30} {stats['source_count']:<12,} {stats['target_count']:<12,} "
                f"{status:<10} {error_count:<8}"
            )
        
        report_lines.append("")
        
        # Error details
        if self.errors:
            report_lines.extend([
                "ERRORS",
                "-" * 80
            ])
            for i, error in enumerate(self.errors, 1):
                report_lines.append(f"{i}. Table: {error['table']}")
                if 'offset' in error:
                    report_lines.append(f"   Offset: {error['offset']}")
                report_lines.append(f"   Error: {error['error']}")
                report_lines.append("")
        
        report_lines.append("=" * 80)
        
        return "\n".join(report_lines)
    
    def migrate(self) -> bool:
        """
        Execute the complete migration process.
        
        Returns:
            True if migration completed successfully, False otherwise
        """
        self.start_time = datetime.now()
        success = False
        
        try:
            # Connect to databases
            self.connect()
            
            # Validate schemas
            if not self.validate_schemas():
                logger.error("Schema validation failed, aborting migration")
                return False
            
            # Migrate tables
            self.migrate_tables()
            
            # Validate data (unless dry run)
            if not self.dry_run:
                success = self.validate_data()
            else:
                success = True
            
        except Exception as e:
            logger.error(f"Migration failed with error: {e}")
            success = False
        finally:
            self.end_time = datetime.now()
            
            # Generate and display report
            report = self.generate_report()
            logger.info("\n" + report)
            
            # Save report to file
            report_filename = f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(report_filename, 'w') as f:
                f.write(report)
            logger.info(f"Migration report saved to: {report_filename}")
            
            # Disconnect
            self.disconnect()
        
        return success


def main():
    """Main entry point for the migration script."""
    parser = argparse.ArgumentParser(
        description='Migrate data from SQLite to PostgreSQL',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic migration
  python migrate_sqlite_to_postgresql.py \\
      --source sqlite:///backend.db \\
      --target postgresql://user:pass@localhost:5432/neo_alexandria

  # Migration with validation
  python migrate_sqlite_to_postgresql.py \\
      --source sqlite:///backend.db \\
      --target postgresql://user:pass@localhost:5432/neo_alexandria \\
      --validate

  # Dry run (validation only, no data migration)
  python migrate_sqlite_to_postgresql.py \\
      --source sqlite:///backend.db \\
      --target postgresql://user:pass@localhost:5432/neo_alexandria \\
      --dry-run

  # Custom batch size
  python migrate_sqlite_to_postgresql.py \\
      --source sqlite:///backend.db \\
      --target postgresql://user:pass@localhost:5432/neo_alexandria \\
      --batch-size 500
        """
    )
    
    parser.add_argument(
        '--source',
        required=True,
        help='Source database URL (SQLite)'
    )
    parser.add_argument(
        '--target',
        required=True,
        help='Target database URL (PostgreSQL)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=1000,
        help='Number of records to process per batch (default: 1000)'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Perform data validation after migration'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Validate schemas without migrating data'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create migrator
    migrator = DatabaseMigrator(
        source_url=args.source,
        target_url=args.target,
        batch_size=args.batch_size,
        dry_run=args.dry_run
    )
    
    # Run migration
    success = migrator.migrate()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
