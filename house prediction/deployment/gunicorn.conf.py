"""
Gunicorn Production Server Configuration for House Price Prediction.

Configures workers, network binding, and logging for deployment
behind an Nginx reverse proxy on AWS EC2.
"""

import multiprocessing
import os

# Server socket: Bind strictly to localhost loopback so requests MUST route through Nginx
bind = os.getenv("GUNICORN_BIND", "127.0.0.1:8000")
backlog = 2048

# Worker processes
# Formula: (2 * CPU cores) + 1, capped at sensible bounds for micro/small EC2 instances
workers = int(os.getenv("GUNICORN_WORKERS", (multiprocessing.cpu_count() * 2) + 1))
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Process naming
proc_name = "house-price-prediction"

# Logging
accesslog = os.getenv("GUNICORN_ACCESS_LOG", "/var/log/house-price-prediction/access.log")
errorlog = os.getenv("GUNICORN_ERROR_LOG", "/var/log/house-price-prediction/error.log")
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" (%(L)ss)'

# Preload app code before worker processes are forked to share loaded ML model memory
preload_app = True
