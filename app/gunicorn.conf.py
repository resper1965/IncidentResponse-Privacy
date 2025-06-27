# Gunicorn configuration for n.crisisops
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 300
keepalive = 5
user = "privacy"
group = "privacy"
tmp_upload_dir = None
logfile = "/opt/privacy/logs/gunicorn.log"
loglevel = "info"
pidfile = "/opt/privacy/gunicorn.pid"
daemon = False
