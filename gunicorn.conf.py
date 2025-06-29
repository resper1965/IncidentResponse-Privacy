# Configuração do Gunicorn para VPS
bind = "0.0.0.0:5000"
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 300
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
preload_app = True
reload = False
accesslog = "-"
errorlog = "-"
loglevel = "info"
