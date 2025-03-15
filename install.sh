#!/bin/bash

# Create the certificate for the first time
docker-compose -f ./docker-compose.prod.init.yaml up -d nginx
docker-compose -f ./docker-compose.prod.init.yaml up certbot
docker-compose -f ./docker-compose.prod.init.yaml down

# Copy the configuration files down
curl -L --create-dirs -o nginx/certbot/etc/letsencrypt/options-ssl-nginx.conf https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf
openssl dhparam -out nginx/certbot/etc/letsencrypt/ssl-dhparams.pem 2048

# Start the production services
docker-compose -f ./docker-compose.prod.yaml up -d

# Add the cron job
echo "0 5 * * *  $(pwd)/renew_cert.sh" | crontab -
