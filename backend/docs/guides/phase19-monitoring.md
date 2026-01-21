# Phase 19 Monitoring Guide

## Overview

This guide covers monitoring the Neo Alexandria hybrid edge-cloud architecture. The system consists of a Cloud API (Render) and Edge Worker (local GPU), connected via Redis queue. Effective monitoring ensures smooth operation and quick issue detection.

## Architecture Monitoring Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Monitoring Stack                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Cloud API (Render)          Edge Worker (Local)           │
│  ├─ Health Check             ├─ Worker Status              │
│  ├─ Request Metrics          ├─ GPU Utilization            │
│  ├─ Error Logs               ├─ Job History                │
│  └─ Service Status           └─ System Resources           │
│                                                             │
│  Redis Queue (Upstash)                                      │
│  ├─ Queue Length                                            │
│  ├─ Task TTL                                                │
│  └─ Worker Status                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Worker Status Monitoring

### Real-Time Status via API

The Cloud API provides a real-time status endpoint that shows what the edge worker is currently doing:

```bash
curl https://your-app.onrender.com/api/v1/ingestion/worker/status
```

**Response Examples**:

```json
// Worker is idle and waiting for tasks
{
  "status": "Idle"
}

// Worker is processing a repository
{
  "status": "Training Graph on github.com/user/awesome-project"
}

// Worker encountered an error
{
  "status": "Error: Failed to clone repository"
}

// Worker is offline
{
  "status": "Offline"
}
```

### Status Patterns

The worker status follows a predictable pattern:

```
Idle → Training Graph on {repo} → Idle
  ↓
Error: {message} → Idle (after recovery)
```

**Status Meanings**:

| Status | Meaning | Action Required |
|--------|---------|-----------------|
| `Idle` | Worker is waiting for tasks | None - normal operation |
| `Training Graph on {repo}` | Worker is processing repository | None - normal operation |
| `Error: {message}` | Worker encountered an error | Check logs, may auto-recover |
| `Offline` | Worker is not running | Start worker service |

### Polling for Updates

For UI integration, poll the status endpoint:

```javascript
// Poll every 2 seconds
setInterval(async () => {
  const response = await fetch('/api/v1/ingestion/worker/status');
  const data = await response.json();
  updateUI(data.status);
}, 2000);
```

**Best Practices**:
- Poll every 2-5 seconds (not faster)
- Show visual indicator (spinner, progress bar)
- Display status text to user
- Alert on "Error" or "Offline" status

## Job History Monitoring

### View Recent Jobs

Get the last N completed jobs:

```bash
curl https://your-app.onrender.com/api/v1/ingestion/jobs/history?limit=10
```

**Response**:

```json
{
  "jobs": [
    {
      "repo_url": "github.com/user/repo1",
      "status": "complete",
      "duration_seconds": 127.5,
      "files_processed": 342,
      "embeddings_generated": 342,
      "timestamp": "2024-01-20T10:30:00Z"
    },
    {
      "repo_url": "github.com/user/repo2",
      "status": "failed",
      "error": "Failed to clone repository",
      "timestamp": "2024-01-20T10:25:00Z"
    },
    {
      "repo_url": "github.com/user/repo3",
      "status": "skipped",
      "reason": "Task exceeded TTL",
      "age_seconds": 90000,
      "timestamp": "2024-01-20T10:20:00Z"
    }
  ]
}
```

### Job Status Types

**Complete**:
- Repository processed successfully
- Embeddings uploaded to Qdrant
- Includes performance metrics

**Failed**:
- Processing encountered an error
- Includes error message
- Worker continues to next job

**Skipped**:
- Task was older than TTL (24 hours)
- Prevents processing stale tasks
- Includes age in seconds

### Metrics to Track

From job history, track:

1. **Success Rate**: `complete / (complete + failed)`
2. **Average Duration**: Mean of `duration_seconds` for complete jobs
3. **Throughput**: Jobs per hour
4. **Error Rate**: `failed / total`
5. **Skip Rate**: `skipped / total` (should be low)

### Example Analysis Script

```python
import requests
from datetime import datetime, timedelta

def analyze_job_history(api_url, hours=24):
    """Analyze job history for the last N hours."""
    response = requests.get(f"{api_url}/api/v1/ingestion/jobs/history?limit=100")
    jobs = response.json()["jobs"]
    
    # Filter by time
    cutoff = datetime.now() - timedelta(hours=hours)
    recent_jobs = [
        j for j in jobs 
        if datetime.fromisoformat(j["timestamp"]) > cutoff
    ]
    
    # Calculate metrics
    total = len(recent_jobs)
    complete = sum(1 for j in recent_jobs if j["status"] == "complete")
    failed = sum(1 for j in recent_jobs if j["status"] == "failed")
    skipped = sum(1 for j in recent_jobs if j["status"] == "skipped")
    
    durations = [j["duration_seconds"] for j in recent_jobs if j["status"] == "complete"]
    avg_duration = sum(durations) / len(durations) if durations else 0
    
    print(f"Last {hours} hours:")
    print(f"  Total Jobs: {total}")
    print(f"  Complete: {complete} ({complete/total*100:.1f}%)")
    print(f"  Failed: {failed} ({failed/total*100:.1f}%)")
    print(f"  Skipped: {skipped} ({skipped/total*100:.1f}%)")
    print(f"  Avg Duration: {avg_duration:.1f}s")
    print(f"  Throughput: {total/hours:.1f} jobs/hour")

# Usage
analyze_job_history("https://your-app.onrender.com", hours=24)
```

## GPU Monitoring

### Using nvidia-smi

Monitor GPU utilization in real-time:

```bash
# Basic monitoring
nvidia-smi

# Continuous monitoring (update every 1 second)
watch -n 1 nvidia-smi

# Detailed query
nvidia-smi --query-gpu=timestamp,name,temperature.gpu,utilization.gpu,utilization.memory,memory.used,memory.total,power.draw --format=csv -l 1
```

**Expected Output During Training**:

```
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 530.30.02    Driver Version: 530.30.02    CUDA Version: 12.1   |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|===============================+======================+======================|
|   0  NVIDIA GeForce ...  Off  | 00000000:01:00.0  On |                  N/A |
| 45%   72C    P2   180W / 220W |   6842MiB / 16384MiB |     85%      Default |
+-------------------------------+----------------------+----------------------+
```

**Key Metrics**:

| Metric | Normal Range | Alert If |
|--------|--------------|----------|
| GPU Utilization | 70-95% during training | <50% (underutilized) or 100% (bottleneck) |
| Memory Usage | 4-12GB | >14GB (risk of OOM) |
| Temperature | 60-80°C | >85°C (thermal throttling) |
| Power Draw | 150-200W | >210W (sustained) |

### GPU Monitoring Script

```bash
#!/bin/bash
# gpu_monitor.sh - Monitor GPU and alert on issues

while true; do
    # Get GPU metrics
    temp=$(nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader)
    util=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader | tr -d '%')
    mem=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader | tr -d ' MiB')
    
    # Check thresholds
    if [ $temp -gt 85 ]; then
        echo "⚠️  WARNING: GPU temperature high: ${temp}°C"
    fi
    
    if [ $util -lt 50 ] && [ $util -gt 0 ]; then
        echo "⚠️  WARNING: GPU underutilized: ${util}%"
    fi
    
    if [ $mem -gt 14000 ]; then
        echo "⚠️  WARNING: GPU memory high: ${mem}MB"
    fi
    
    # Log metrics
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Temp: ${temp}°C, Util: ${util}%, Mem: ${mem}MB"
    
    sleep 5
done
```

### GPU Monitoring Tools

**Linux**:
- `nvidia-smi` - Built-in NVIDIA tool
- `nvtop` - Interactive GPU monitoring (like htop)
- `gpustat` - Python-based GPU monitoring

```bash
# Install nvtop
sudo apt install nvtop

# Install gpustat
pip install gpustat

# Run
nvtop
gpustat -i 1
```

**Windows**:
- Task Manager → Performance → GPU
- NVIDIA Control Panel
- GPU-Z (third-party)
- MSI Afterburner (third-party)

## Log Monitoring

### Cloud API Logs (Render)

**Via Render Dashboard**:
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Select your service
3. Click "Logs" tab
4. View real-time logs

**Via Render CLI**:

```bash
# Install Render CLI
npm install -g render-cli

# Login
render login

# View logs
render logs -s neo-alexandria-cloud-api

# Follow logs
render logs -s neo-alexandria-cloud-api -f
```

**Log Levels**:
- `INFO` - Normal operations
- `WARNING` - Non-critical issues
- `ERROR` - Errors that need attention
- `CRITICAL` - System failures

**Key Log Patterns**:

```
# Successful task dispatch
INFO: Task dispatched: github.com/user/repo (job_id=123)

# Queue full
WARNING: Queue full (10 pending tasks), rejecting new task

# Redis connection error
ERROR: Failed to connect to Redis: Connection timeout

# Authentication failure
WARNING: Authentication failed: Invalid token
```

### Edge Worker Logs

**Manual Mode** (stdout/stderr):

```bash
# Run with output redirection
python worker.py > worker.log 2>&1

# Follow logs
tail -f worker.log
```

**Systemd (Linux)**:

```bash
# Follow logs
sudo journalctl -u neo-alexandria-worker -f

# View recent logs
sudo journalctl -u neo-alexandria-worker -n 100

# Filter by priority
sudo journalctl -u neo-alexandria-worker -p err

# Filter by time
sudo journalctl -u neo-alexandria-worker --since "1 hour ago"

# Export logs
sudo journalctl -u neo-alexandria-worker --since "2024-01-20" > worker-logs.txt
```

**NSSM (Windows)**:

```powershell
# View stdout
Get-Content C:\path\to\logs\worker-stdout.log -Tail 50 -Wait

# View stderr
Get-Content C:\path\to\logs\worker-stderr.log -Tail 50 -Wait

# Search for errors
Select-String -Path C:\path\to\logs\worker-stderr.log -Pattern "ERROR"
```

**Key Log Patterns**:

```
# Worker startup
🔥 Edge Worker Online
   Hardware: NVIDIA GeForce RTX 4070
   Device: cuda

# Job received
⚡ Received Job: github.com/user/repo

# Processing stages
📥 Cloning github.com/user/repo...
📊 Building dependency graph...
🧠 Training Node2Vec...
☁️  Uploading embeddings to Qdrant...

# Job complete
✅ Job Complete (127.5s)

# Errors
❌ Error: Failed to clone repository
⚠️  Failed to parse src/utils/parser.py: SyntaxError
```

### Log Aggregation

For production, consider log aggregation:

**Options**:
- **Papertrail** - Free tier available
- **Loggly** - Free tier available
- **ELK Stack** - Self-hosted
- **Grafana Loki** - Self-hosted

**Example: Papertrail Integration**

```bash
# Install remote_syslog2
wget https://github.com/papertrail/remote_syslog2/releases/download/v0.20/remote_syslog_linux_amd64.tar.gz
tar xzf remote_syslog_linux_amd64.tar.gz
sudo cp remote_syslog/remote_syslog /usr/local/bin

# Configure
sudo nano /etc/log_files.yml
```

```yaml
files:
  - /var/log/neo-worker.log
destination:
  host: logs.papertrailapp.com
  port: YOUR_PORT
  protocol: tls
```

```bash
# Start
sudo remote_syslog
```

## Queue Monitoring

### Check Queue Length

Monitor the Redis queue directly:

```bash
# Using redis-cli (if you have direct access)
redis-cli -u redis://your-redis-url LLEN ingest_queue

# Using Upstash REST API
curl https://xxx.upstash.io/llen/ingest_queue \
  -H "Authorization: Bearer YOUR_REST_TOKEN"
```

**Interpretation**:
- `0` - Queue is empty (normal when idle)
- `1-5` - Normal operation
- `6-9` - Queue building up
- `10` - Queue full (rejecting new tasks)

### Monitor Queue Health

```python
import requests
import os

def check_queue_health(redis_url, redis_token):
    """Check Redis queue health."""
    headers = {"Authorization": f"Bearer {redis_token}"}
    
    # Check queue length
    response = requests.get(f"{redis_url}/llen/ingest_queue", headers=headers)
    queue_length = int(response.json()["result"])
    
    # Check worker status
    response = requests.get(f"{redis_url}/get/worker_status", headers=headers)
    worker_status = response.json()["result"]
    
    # Check job history
    response = requests.get(f"{redis_url}/lrange/job_history/0/9", headers=headers)
    recent_jobs = response.json()["result"]
    
    print(f"Queue Length: {queue_length}")
    print(f"Worker Status: {worker_status}")
    print(f"Recent Jobs: {len(recent_jobs)}")
    
    # Alert conditions
    if queue_length >= 10:
        print("⚠️  ALERT: Queue is full!")
    
    if worker_status == "Offline":
        print("⚠️  ALERT: Worker is offline!")
    
    if worker_status and worker_status.startswith("Error"):
        print(f"⚠️  ALERT: Worker error: {worker_status}")

# Usage
check_queue_health(
    os.getenv("UPSTASH_REDIS_REST_URL"),
    os.getenv("UPSTASH_REDIS_REST_TOKEN")
)
```

## System Resource Monitoring

### Edge Worker System Resources

**CPU Monitoring**:

```bash
# Linux
top -p $(pgrep -f worker.py)
htop -p $(pgrep -f worker.py)

# macOS
top -pid $(pgrep -f worker.py)

# Windows
Get-Process python | Where-Object {$_.CommandLine -like "*worker.py*"}
```

**Memory Monitoring**:

```bash
# Linux
ps aux | grep worker.py
free -h

# macOS
ps aux | grep worker.py
vm_stat

# Windows
Get-Process python | Select-Object WorkingSet,VirtualMemorySize
```

**Disk Monitoring**:

```bash
# Check disk space
df -h  # Linux/macOS
Get-PSDrive  # Windows

# Check temp directory size
du -sh /tmp/neo_repo_*  # Linux/macOS
Get-ChildItem C:\Temp\neo_repo_* | Measure-Object -Property Length -Sum  # Windows
```

**Network Monitoring**:

```bash
# Monitor network connections
netstat -an | grep ESTABLISHED

# Monitor bandwidth (Linux)
iftop
nethogs

# Monitor bandwidth (Windows)
Get-NetAdapterStatistics
```

### Cloud API System Resources

Monitor via Render dashboard:

1. Go to service page
2. Click "Metrics" tab
3. View:
   - CPU usage
   - Memory usage
   - Request count
   - Response time
   - Error rate

**Metrics to Watch**:
- CPU: Should be <50% average
- Memory: Should be <400MB (512MB limit)
- Response time: Should be <200ms P95
- Error rate: Should be <1%

## Alerting

### Manual Alerts

Create a monitoring script that checks key metrics:

```python
#!/usr/bin/env python3
"""
monitor.py - Monitor Neo Alexandria system health
"""

import requests
import os
import sys
from datetime import datetime

def check_health(api_url):
    """Check system health and alert on issues."""
    issues = []
    
    # Check Cloud API health
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code != 200:
            issues.append(f"Cloud API unhealthy: {response.status_code}")
    except Exception as e:
        issues.append(f"Cloud API unreachable: {e}")
    
    # Check worker status
    try:
        response = requests.get(f"{api_url}/api/v1/ingestion/worker/status", timeout=5)
        status = response.json()["status"]
        
        if status == "Offline":
            issues.append("Worker is offline")
        elif status.startswith("Error"):
            issues.append(f"Worker error: {status}")
    except Exception as e:
        issues.append(f"Cannot check worker status: {e}")
    
    # Check queue
    try:
        redis_url = os.getenv("UPSTASH_REDIS_REST_URL")
        redis_token = os.getenv("UPSTASH_REDIS_REST_TOKEN")
        headers = {"Authorization": f"Bearer {redis_token}"}
        
        response = requests.get(f"{redis_url}/llen/ingest_queue", headers=headers)
        queue_length = int(response.json()["result"])
        
        if queue_length >= 10:
            issues.append(f"Queue is full: {queue_length} tasks")
    except Exception as e:
        issues.append(f"Cannot check queue: {e}")
    
    # Report
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if issues:
        print(f"[{timestamp}] ⚠️  ALERTS:")
        for issue in issues:
            print(f"  - {issue}")
        return 1
    else:
        print(f"[{timestamp}] ✅ All systems healthy")
        return 0

if __name__ == "__main__":
    api_url = sys.argv[1] if len(sys.argv) > 1 else "https://your-app.onrender.com"
    exit(check_health(api_url))
```

Run periodically:

```bash
# Run every 5 minutes
*/5 * * * * /path/to/monitor.py https://your-app.onrender.com
```

### Email Alerts

Use a service like Mailgun or SendGrid:

```python
import smtplib
from email.mime.text import MIMEText

def send_alert(subject, body):
    """Send email alert."""
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'alerts@neoalexandria.com'
    msg['To'] = 'admin@neoalexandria.com'
    
    with smtplib.SMTP('smtp.mailgun.org', 587) as server:
        server.starttls()
        server.login('your-username', 'your-password')
        server.send_message(msg)

# Usage
if issues:
    send_alert(
        "Neo Alexandria Alert",
        f"System issues detected:\n" + "\n".join(issues)
    )
```

### Slack Alerts

Use Slack webhooks:

```python
import requests

def send_slack_alert(webhook_url, message):
    """Send Slack alert."""
    payload = {
        "text": message,
        "username": "Neo Alexandria Monitor",
        "icon_emoji": ":warning:"
    }
    requests.post(webhook_url, json=payload)

# Usage
if issues:
    send_slack_alert(
        "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
        f"⚠️ System issues:\n" + "\n".join(f"• {i}" for i in issues)
    )
```

## Dashboard

### Simple Web Dashboard

Create a simple monitoring dashboard:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Neo Alexandria Monitor</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .metric { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .healthy { background-color: #d4edda; }
        .warning { background-color: #fff3cd; }
        .error { background-color: #f8d7da; }
    </style>
</head>
<body>
    <h1>Neo Alexandria Monitor</h1>
    
    <div id="worker-status" class="metric">
        <strong>Worker Status:</strong> <span id="status">Loading...</span>
    </div>
    
    <div id="queue-length" class="metric">
        <strong>Queue Length:</strong> <span id="queue">Loading...</span>
    </div>
    
    <div id="recent-jobs" class="metric">
        <strong>Recent Jobs:</strong>
        <ul id="jobs"></ul>
    </div>
    
    <script>
        const API_URL = 'https://your-app.onrender.com';
        
        async function updateStatus() {
            // Worker status
            const statusRes = await fetch(`${API_URL}/api/v1/ingestion/worker/status`);
            const statusData = await statusRes.json();
            document.getElementById('status').textContent = statusData.status;
            
            const statusDiv = document.getElementById('worker-status');
            if (statusData.status === 'Idle') {
                statusDiv.className = 'metric healthy';
            } else if (statusData.status.startsWith('Training')) {
                statusDiv.className = 'metric warning';
            } else {
                statusDiv.className = 'metric error';
            }
            
            // Job history
            const jobsRes = await fetch(`${API_URL}/api/v1/ingestion/jobs/history?limit=5`);
            const jobsData = await jobsRes.json();
            
            const jobsList = document.getElementById('jobs');
            jobsList.innerHTML = '';
            jobsData.jobs.forEach(job => {
                const li = document.createElement('li');
                li.textContent = `${job.repo_url} - ${job.status} (${job.timestamp})`;
                jobsList.appendChild(li);
            });
        }
        
        // Update every 2 seconds
        updateStatus();
        setInterval(updateStatus, 2000);
    </script>
</body>
</html>
```

## Best Practices

### Monitoring Checklist

Daily:
- [ ] Check worker status
- [ ] Review job history
- [ ] Check for errors in logs
- [ ] Verify GPU temperature

Weekly:
- [ ] Review success/failure rates
- [ ] Check disk space
- [ ] Review average processing time
- [ ] Check for stale tasks

Monthly:
- [ ] Review overall system health
- [ ] Analyze performance trends
- [ ] Update monitoring scripts
- [ ] Review alert thresholds

### Alert Thresholds

Set appropriate thresholds:

| Metric | Warning | Critical |
|--------|---------|----------|
| Queue Length | 7 | 10 |
| GPU Temperature | 80°C | 85°C |
| GPU Memory | 12GB | 14GB |
| Error Rate | 5% | 10% |
| Worker Offline | 5 min | 15 min |

### Monitoring Tools Comparison

| Tool | Cost | Features | Best For |
|------|------|----------|----------|
| Manual Scripts | Free | Custom | Small deployments |
| Papertrail | Free tier | Log aggregation | Startups |
| Datadog | $15/host | Full stack | Production |
| Grafana | Free (self-hosted) | Dashboards | Advanced users |
| Prometheus | Free (self-hosted) | Metrics | Kubernetes |

## Next Steps

- [Cloud Deployment Guide](phase19-deployment.md) - Deploy Cloud API
- [Edge Setup Guide](phase19-edge-setup.md) - Set up edge worker
- [Troubleshooting Guide](troubleshooting.md) - Common issues

## Support

- **Documentation**: [Neo Alexandria Docs](../README.md)
- **Issues**: [GitHub Issues](https://github.com/your-org/neo-alexandria-2.0/issues)
