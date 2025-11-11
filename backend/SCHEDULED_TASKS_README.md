# Neo Alexandria - Scheduled Quality Monitoring Tasks

This document describes the scheduled background tasks for quality monitoring and maintenance in Neo Alexandria Phase 9.

## Overview

Phase 9 introduces automated quality monitoring through two scheduled tasks:

1. **Outlier Detection** - Identifies resources with anomalous quality scores (recommended: daily)
2. **Quality Degradation Monitoring** - Detects resources whose quality has degraded over time (recommended: weekly)

## Task Descriptions

### Outlier Detection

**Purpose**: Automatically identify resources with unusual quality patterns that may indicate data quality issues.

**Algorithm**: Uses Isolation Forest machine learning algorithm to detect anomalies across quality dimensions.

**Configuration**:
- Default batch size: 1000 resources
- Recommended schedule: Daily
- Contamination rate: 10% (expects ~10% outliers)

**Outputs**:
- Flags outliers with `is_quality_outlier = True`
- Sets `needs_quality_review = True` for human review
- Stores anomaly score and specific reasons

### Quality Degradation Monitoring

**Purpose**: Detect resources whose quality has significantly decreased over time, indicating potential issues like broken links or outdated content.

**Algorithm**: Recomputes quality for resources older than the time window and compares to historical scores.

**Configuration**:
- Default time window: 30 days
- Recommended schedule: Weekly
- Degradation threshold: 20% drop in quality score

**Outputs**:
- Identifies degraded resources
- Sets `needs_quality_review = True`
- Returns degradation report with old/new quality scores

## Running Scheduled Tasks

### Manual Execution

Run all tasks:
```bash
cd backend
python run_scheduled_tasks.py all
```

Run specific task:
```bash
python run_scheduled_tasks.py outlier-detection
python run_scheduled_tasks.py degradation-monitoring
```

With custom parameters:
```bash
python run_scheduled_tasks.py outlier-detection --batch-size 500
python run_scheduled_tasks.py degradation-monitoring --time-window 60
```

Get JSON output:
```bash
python run_scheduled_tasks.py all --json
```

### Cron Configuration

Add to crontab (`crontab -e`):

```cron
# Daily outlier detection at 2 AM
0 2 * * * cd /path/to/neo-alexandria/backend && /path/to/python run_scheduled_tasks.py outlier-detection >> /var/log/neo-alexandria/outlier-detection.log 2>&1

# Weekly degradation monitoring on Sundays at 3 AM
0 3 * * 0 cd /path/to/neo-alexandria/backend && /path/to/python run_scheduled_tasks.py degradation-monitoring >> /var/log/neo-alexandria/degradation-monitoring.log 2>&1
```

### Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (daily/weekly)
4. Action: Start a program
   - Program: `python.exe`
   - Arguments: `run_scheduled_tasks.py outlier-detection`
   - Start in: `C:\path\to\neo-alexandria\backend`

### Docker/Kubernetes

Add to docker-compose.yml:
```yaml
services:
  scheduled-tasks:
    build: ./backend
    command: python run_scheduled_tasks.py all
    environment:
      - DATABASE_URL=${DATABASE_URL}
    depends_on:
      - db
    restart: "no"
```

Run with cron-like scheduler:
```bash
# Using ofelia (Docker cron scheduler)
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  mcuadros/ofelia:latest daemon --config=/etc/ofelia/config.ini
```

## Configuration

Edit `backend/app/services/scheduled_tasks.py` to customize:

```python
class ScheduledTaskConfig:
    # Outlier detection configuration
    OUTLIER_DETECTION_ENABLED = True
    OUTLIER_DETECTION_BATCH_SIZE = 1000
    OUTLIER_DETECTION_SCHEDULE = "daily"
    
    # Quality degradation monitoring configuration
    DEGRADATION_MONITORING_ENABLED = True
    DEGRADATION_MONITORING_TIME_WINDOW_DAYS = 30
    DEGRADATION_MONITORING_SCHEDULE = "weekly"
```

## Monitoring and Alerts

### Logs

Tasks log to standard output and Python logging system:
- INFO: Normal execution progress
- WARNING: Degraded resources detected
- ERROR: Task failures

Configure logging in your application:
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/neo-alexandria/scheduled-tasks.log'),
        logging.StreamHandler()
    ]
)
```

### Metrics

Task execution returns metrics:
```json
{
  "success": true,
  "outlier_count": 42,
  "batch_size": 1000,
  "duration_seconds": 12.34,
  "timestamp": "2025-11-11T02:00:00Z"
}
```

### Alerting

Set up alerts based on:
- High outlier count (>20% of batch)
- Degradation spike (>50 resources)
- Task failures
- Long execution times

Example with monitoring tools:
```bash
# Check exit code
python run_scheduled_tasks.py outlier-detection
if [ $? -ne 0 ]; then
    # Send alert (email, Slack, PagerDuty, etc.)
    echo "Outlier detection failed" | mail -s "Alert" admin@example.com
fi
```

## Review Queue

Resources flagged by scheduled tasks appear in the review queue:

```bash
# API endpoint
GET /quality/review-queue?sort_by=outlier_score&limit=50
```

Review queue includes:
- Resources with `needs_quality_review = True`
- Outlier score and reasons
- Quality dimension breakdown
- Last computation timestamp

## Performance Considerations

### Outlier Detection
- Processes 1000 resources in ~30 seconds
- Memory usage: ~500MB for feature matrix
- CPU intensive during Isolation Forest training
- Consider running during low-traffic periods

### Degradation Monitoring
- Recomputes quality for resources older than time window
- Duration depends on number of stale resources
- I/O intensive (database queries)
- Consider batching for large datasets

### Optimization Tips
1. Run during off-peak hours (2-4 AM)
2. Adjust batch sizes based on system resources
3. Monitor execution times and adjust schedules
4. Use database indexes on quality fields
5. Consider parallel processing for large datasets

## Troubleshooting

### Task Fails with "Insufficient Data"
- Outlier detection requires minimum 10 resources with quality scores
- Run quality computation on existing resources first

### High Memory Usage
- Reduce batch size for outlier detection
- Process in smaller chunks

### Long Execution Times
- Check database indexes on quality fields
- Optimize quality computation queries
- Consider caching frequently accessed data

### No Outliers Detected
- Verify quality scores are computed for resources
- Check contamination parameter (may need adjustment)
- Review quality score distribution

## Integration with Other Systems

### Prometheus Metrics
```python
from prometheus_client import Counter, Histogram

outlier_detection_counter = Counter(
    'neo_alexandria_outliers_detected_total',
    'Total number of quality outliers detected'
)

task_duration = Histogram(
    'neo_alexandria_scheduled_task_duration_seconds',
    'Duration of scheduled tasks',
    ['task_name']
)
```

### Grafana Dashboard
Create dashboard with:
- Outlier detection rate over time
- Quality degradation trends
- Task execution duration
- Review queue size

### Slack Notifications
```python
import requests

def send_slack_alert(message):
    webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    requests.post(webhook_url, json={"text": message})

# In scheduled task
if degraded_count > 50:
    send_slack_alert(f"⚠️ High degradation detected: {degraded_count} resources")
```

## Future Enhancements

- Web UI for task management and scheduling
- Real-time task status monitoring
- Automatic quality improvement suggestions
- Machine learning-based degradation prediction
- Integration with content management workflows
- Automated remediation for common issues
