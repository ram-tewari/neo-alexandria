"""
Neo Alexandria - Scheduled Background Tasks (Phase 9)

This module provides scheduled background tasks for quality monitoring and maintenance.
Tasks include daily outlier detection and weekly quality degradation monitoring.

Related files:
- app/services/quality_service.py: Quality assessment and outlier detection
- app/database/models.py: Resource model with quality fields

Features:
- Daily outlier detection to identify anomalous quality scores
- Weekly quality degradation monitoring to detect content issues
- Configurable batch sizes and scheduling frequencies
- Graceful error handling to prevent task failures from blocking system
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from backend.app.database.base import SessionLocal
from backend.app.services.quality_service import QualityService

logger = logging.getLogger(__name__)


class ScheduledTaskConfig:
    """Configuration for scheduled quality monitoring tasks."""
    
    # Outlier detection configuration
    OUTLIER_DETECTION_ENABLED = True
    OUTLIER_DETECTION_BATCH_SIZE = 1000
    OUTLIER_DETECTION_SCHEDULE = "daily"  # Run daily
    
    # Quality degradation monitoring configuration
    DEGRADATION_MONITORING_ENABLED = True
    DEGRADATION_MONITORING_TIME_WINDOW_DAYS = 30
    DEGRADATION_MONITORING_SCHEDULE = "weekly"  # Run weekly


def run_outlier_detection(
    db: Optional[Session] = None,
    batch_size: Optional[int] = None
) -> dict:
    """Run scheduled outlier detection task.
    
    This task identifies resources with anomalous quality scores using
    Isolation Forest algorithm. Detected outliers are flagged for human review.
    
    Args:
        db: Database session (optional, creates new session if not provided)
        batch_size: Number of resources to process (optional, uses config default)
        
    Returns:
        Dictionary with task execution results including outlier count
    """
    session = db or SessionLocal()
    close_session = db is None
    
    try:
        logger.info("Starting scheduled outlier detection task")
        start_time = datetime.now(timezone.utc)
        
        # Initialize quality service
        quality_service = QualityService(db=session)
        
        # Run outlier detection
        batch_size = batch_size or ScheduledTaskConfig.OUTLIER_DETECTION_BATCH_SIZE
        outlier_count = quality_service.detect_quality_outliers(batch_size=batch_size)
        
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()
        
        logger.info(
            f"Outlier detection completed: {outlier_count} outliers detected "
            f"in {duration:.2f} seconds"
        )
        
        return {
            "success": True,
            "outlier_count": outlier_count,
            "batch_size": batch_size,
            "duration_seconds": duration,
            "timestamp": end_time.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Outlier detection task failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    finally:
        if close_session:
            session.close()


def run_degradation_monitoring(
    db: Optional[Session] = None,
    time_window_days: Optional[int] = None
) -> dict:
    """Run scheduled quality degradation monitoring task.
    
    This task identifies resources whose quality has degraded significantly
    over time, indicating potential content issues like broken links or
    outdated information.
    
    Args:
        db: Database session (optional, creates new session if not provided)
        time_window_days: Lookback period in days (optional, uses config default)
        
    Returns:
        Dictionary with task execution results including degraded resource count
    """
    session = db or SessionLocal()
    close_session = db is None
    
    try:
        logger.info("Starting scheduled quality degradation monitoring task")
        start_time = datetime.now(timezone.utc)
        
        # Initialize quality service
        quality_service = QualityService(db=session)
        
        # Run degradation monitoring
        time_window = time_window_days or ScheduledTaskConfig.DEGRADATION_MONITORING_TIME_WINDOW_DAYS
        degradation_report = quality_service.monitor_quality_degradation(
            time_window_days=time_window
        )
        
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()
        
        degraded_count = len(degradation_report)
        logger.info(
            f"Degradation monitoring completed: {degraded_count} degraded resources "
            f"detected in {duration:.2f} seconds"
        )
        
        # Log details of degraded resources for alerting
        if degraded_count > 0:
            logger.warning(
                f"Quality degradation detected in {degraded_count} resources. "
                f"Review queue updated."
            )
            for item in degradation_report[:5]:  # Log first 5 for visibility
                logger.warning(
                    f"  - {item['title'][:50]}: "
                    f"{item['old_quality']:.2f} → {item['new_quality']:.2f} "
                    f"({item['degradation_pct']:.1f}% drop)"
                )
        
        return {
            "success": True,
            "degraded_count": degraded_count,
            "time_window_days": time_window,
            "duration_seconds": duration,
            "timestamp": end_time.isoformat(),
            "degraded_resources": degradation_report
        }
        
    except Exception as e:
        logger.error(f"Degradation monitoring task failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    finally:
        if close_session:
            session.close()


def run_all_scheduled_tasks(db: Optional[Session] = None) -> dict:
    """Run all enabled scheduled quality monitoring tasks.
    
    This is a convenience function for running all scheduled tasks together,
    useful for manual execution or testing.
    
    Args:
        db: Database session (optional, creates new session if not provided)
        
    Returns:
        Dictionary with results from all executed tasks
    """
    results = {}
    
    if ScheduledTaskConfig.OUTLIER_DETECTION_ENABLED:
        results["outlier_detection"] = run_outlier_detection(db=db)
    
    if ScheduledTaskConfig.DEGRADATION_MONITORING_ENABLED:
        results["degradation_monitoring"] = run_degradation_monitoring(db=db)
    
    return results
