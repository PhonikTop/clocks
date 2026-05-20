FROM nginx:1.25-alpine

WORKDIR /usr/share/nginx/html

RUN cat > /etc/nginx/conf.d/default.conf <<'EOF'
server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;
    proxy_read_timeout 300s;
    send_timeout 300s;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://watchy-api:8000;
    }

    location /admin {
        proxy_pass http://watchy-api:8000;
    }

    location /ws {
        proxy_pass http://watchy-api:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";

        proxy_connect_timeout 7d;
        proxy_send_timeout 7d;
        proxy_read_timeout 7d;
    }

    location /static {
        alias /static;
        expires 365d;
        access_log off;
        add_header Cache-Control "public, immutable";
    }

    location ~* \.(?:css|js|json|jpg|jpeg|gif|png|svg|ico|woff2?|ttf|eot)$ {
        try_files $uri =404;
        access_log off;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000, immutable";
    }

    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}
EOF

COPY dist/ /usr/share/nginx/html
