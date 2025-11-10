"""
Neo Alexandria 2.0 - Production Gunicorn Configuration

This configuration file provides optimized settings for running Neo Alexandria 2.0
in production with Gunicorn and Uvicorn workers. It follows the performance best
practices outlined in the FastAPI performance article.

Usage:
    gunicorn backend.app.main:app -c gunicorn.conf.py

Features:
- Optimized worker count based on CPU cores
- Proper async worker configuration
- Memory and timeout optimizations
- Logging configuration
- Health check endpoints
- Graceful shutdown handling
"""

import multiprocessing

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
# Rule of thumb: (2 × number of CPUs) + 1 for optimal concurrency
workers = (2 * multiprocessing.cpu_count()) + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000

# Timeouts
timeout = 30
keepalive = 2
graceful_timeout = 30

# Memory management
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "backend"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Performance tuning
worker_tmp_dir = "/dev/shm"  # Use shared memory for worker temp files

# Environment variables
raw_env = [
    "ENV=prod",
    "ENABLE_METRICS=true",
]

# SSL (uncomment and configure for HTTPS)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("Neo Alexandria 2.0 server is ready. Workers: %s", workers)

def worker_int(worker):
    """Called just after a worker has been forked."""
    worker.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info("Worker will be spawned")

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal."""
    worker.log.info("Worker received SIGABRT signal")

def on_exit(server):
    """Called just before exiting."""
    server.log.info("Neo Alexandria 2.0 server is shutting down")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    server.log.info("Neo Alexandria 2.0 server is reloading")
