import os
import multiprocessing

# Gunicorn config variables
loglevel = "info"
errorlog = "-"  # stderr
accesslog = "-"  # stdout
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

bind = "0.0.0.0:" + os.getenv("PORT", "8000")

# Workers
# Render automatically sets WEB_CONCURRENCY. If not, we default to a reasonable calculation.
workers = int(os.getenv("WEB_CONCURRENCY", multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"

# Timeouts
timeout = 120
keepalive = 5

print(f"Starting Gunicorn with {workers} workers on {bind}")
