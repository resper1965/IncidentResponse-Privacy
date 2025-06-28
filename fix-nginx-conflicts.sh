#!/bin/bash

# Fix Nginx port conflicts and configuration issues
echo "🔧 Resolving Nginx conflicts..."

# Stop nginx completely
systemctl stop nginx
pkill -f nginx

# Check what's using ports 80 and 443
echo "📋 Checking port usage:"
netstat -tlnp | grep ':80\|:443'

# Remove conflicting configurations
rm -f /etc/nginx/sites-enabled/*

# Create clean privacy configuration
cat > /etc/nginx/sites-available/privacy << 'EOF'
server {
    listen 80;
    server_name monster.e-ness.com.br;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name monster.e-ness.com.br;

    ssl_certificate /etc/letsencrypt/live/monster.e-ness.com.br/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/monster.e-ness.com.br/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    client_max_body_size 100M;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

# Enable only our site
ln -sf /etc/nginx/sites-available/privacy /etc/nginx/sites-enabled/

# Test configuration
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx configuration valid"
    
    # Start nginx
    systemctl start nginx
    
    # Test connections
    echo "🧪 Testing connections..."
    curl -I http://localhost:5000
    curl -I https://monster.e-ness.com.br
    
    echo "✅ Nginx conflicts resolved!"
else
    echo "❌ Nginx configuration still has errors"
    nginx -t
fi

echo "📊 Final status:"
systemctl status nginx --no-pager -l