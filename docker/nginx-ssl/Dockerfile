# Healthcare Voice AI - Nginx SSL/TLS Docker Image
FROM nginx:alpine

# Install certbot and openssl
RUN apk add --no-cache \
    certbot \
    python3 \
    py3-pip \
    openssl \
    curl \
    && pip3 install certbot-nginx

# Create necessary directories
RUN mkdir -p /var/www/certbot \
    && mkdir -p /etc/letsencrypt \
    && mkdir -p /var/www/healthcare-voice-ai/error-pages \
    && mkdir -p /var/log/ssl-renewal

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf
COPY healthcare-voice-ai.conf /etc/nginx/conf.d/default.conf

# Copy SSL setup scripts
COPY ssl-setup.sh /usr/local/bin/ssl-setup.sh
COPY ssl-renew.sh /usr/local/bin/ssl-renew.sh

# Copy error pages
COPY error-pages/ /var/www/dental-voice-ai/error-pages/

# Make scripts executable
RUN chmod +x /usr/local/bin/ssl-setup.sh \
    && chmod +x /usr/local/bin/ssl-renew.sh

# Create log rotation configuration
RUN echo '/var/log/ssl-renewal.log {\n\
    daily\n\
    missingok\n\
    rotate 52\n\
    compress\n\
    delaycompress\n\
    notifempty\n\
    create 644 root root\n\
}' > /etc/logrotate.d/ssl-renewal

# Expose ports
EXPOSE 80 443

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Start nginx and SSL setup
CMD ["/usr/local/bin/ssl-setup.sh"]
