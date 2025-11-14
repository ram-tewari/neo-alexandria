# Quality Degradation Monitoring - Quick Reference

## Quick Start

```python
from app.services.quality_service import QualityService

# Initialize
quality_service = QualityService(db, quality_version="v2.0")

# Monitor degradation (30-day window)
degraded = quality_service.monitor_quality_degradation()

# Custom time window (60 days)
degraded = quality_service.monitor_quality_degradation(time_window_days=60)
```

## Method Signature

```python
def monitor_quality_degradation(
    self, 
    time_window_days: int = 30
) -> list[Dict[str, Any]]
```

## Return Format

```python
[
    {
        "resource_id": "uuid-string",
        "title": "Resource Title",
        "old_quality": 0.85,
        "new_quality": 0.62,
        "degradation_pct": 27.1
    }
]
```

## Key Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `time_window_days` | int | 30 | Lookback period in days |

## Degradation Threshold

- **Threshold:** 20% drop (0.2 absolute difference)
- **Formula:** `old_quality - new_quality > 0.2`
- **Percentage:** `(drop / old_quality) * 100`

## Database Updates

### Fields Read
- `quality_last_computed` - Filter for old scores
- `quality_overall` - Previous quality score

### Fields Written
- `needs_quality_review` - Set to `True` for degraded resources
- All quality fields - Updated via `compute_quality()` recomputation

## Common Use Cases

### 1. Weekly Monitoring
```python
# Run weekly to catch degradation
degraded = quality_service.monitor_quality_degradation(time_window_days=7)
```

### 2. Monthly Review
```python
# Monthly comprehensive check
degraded = quality_service.monitor_quality_degradation(time_window_days=30)
```

### 3. Quarterly Audit
```python
# Quarterly deep audit
degraded = quality_service.monitor_quality_degradation(time_window_days=90)
```

## Degradation Causes

| Cause | Affected Dimension | Example |
|-------|-------------------|---------|
| Broken Links | Accuracy | Citation URLs become invalid |
| Outdated Content | Timeliness | Publication age increases |
| Metadata Loss | Completeness | Author/DOI fields cleared |
| Content Changes | Consistency | Title-content misalignment |
| Relevance Shift | Relevance | Classification confidence drops |

## Error Handling

```python
# Graceful error handling
try:
    degraded = quality_service.monitor_quality_degradation()
    for report in degraded:
        print(f"Degraded: {report['title']}")
except Exception as e:
    print(f"Monitoring failed: {e}")
```

## Integration Examples

### With API Endpoint
```python
@router.get("/quality/degradation")
async def get_degradation_report(
    time_window_days: int = 30,
    db: Session = Depends(get_db)
):
    quality_service = QualityService(db)
    return quality_service.monitor_quality_degradation(time_window_days)
```

### With Scheduled Task
```python
from apscheduler.schedulers.background import BackgroundScheduler

def scheduled_monitoring():
    db = SessionLocal()
    try:
        quality_service = QualityService(db)
        degraded = quality_service.monitor_quality_degradation()
        # Send alerts, log results, etc.
    finally:
        db.close()

scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_monitoring, 'cron', day_of_week='mon', hour=2)
```

### With Curator Dashboard
```python
# Get resources needing review
resources_to_review = db.query(Resource).filter(
    Resource.needs_quality_review == True
).order_by(Resource.quality_overall.asc()).all()
```

## Performance Tips

1. **Batch Processing:** Process in chunks for large datasets
2. **Off-Peak Hours:** Run during low-traffic periods
3. **Parallel Processing:** Use multiprocessing for large batches
4. **Caching:** Cache dimension calculations when possible

## Monitoring Metrics

Track these metrics for system health:

- **Degradation Rate:** % of resources degrading per period
- **Average Drop:** Mean quality drop for degraded resources
- **Recovery Time:** Time to fix degraded resources
- **False Positives:** Resources flagged incorrectly

## Troubleshooting

### No Resources Found
- Check if resources have `quality_last_computed` set
- Verify time window is appropriate
- Ensure resources exist in database

### High Degradation Rate
- Investigate common causes (broken links, etc.)
- Review quality computation algorithm
- Check for data corruption

### Performance Issues
- Reduce batch size
- Increase time window
- Optimize database queries
- Add indexes on quality fields

## Related Documentation

- **Design:** `.kiro/specs/phase9-quality-assessment/design.md`
- **Requirements:** `.kiro/specs/phase9-quality-assessment/requirements.md`
- **Implementation:** `backend/PHASE9_TASK5_DEGRADATION_MONITORING_SUMMARY.md`
- **Service Code:** `backend/app/services/quality_service.py`

## Support

For issues or questions:
1. Check implementation summary
2. Review design document
3. Examine test cases
4. Consult API documentation
