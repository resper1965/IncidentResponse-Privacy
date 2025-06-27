# Configuração simplificada para n.crisisops
bind = "0.0.0.0:5000"
workers = 1
worker_class = "sync"
timeout = 120
keepalive = 2
preload_app = False
reload = False
daemon = False
pidfile = "/opt/privacy/gunicorn.pid"
accesslog = "/opt/privacy/logs/gunicorn_access.log"
errorlog = "/opt/privacy/logs/gunicorn_error.log"
loglevel = "debug"
capture_output = True
