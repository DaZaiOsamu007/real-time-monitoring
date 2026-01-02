# Multi-stage build to create a single container with all services
FROM python:3.9-slim as base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Install Prometheus
RUN wget https://github.com/prometheus/prometheus/releases/download/v2.48.0/prometheus-2.48.0.linux-amd64.tar.gz \
    && tar xvfz prometheus-2.48.0.linux-amd64.tar.gz \
    && mv prometheus-2.48.0.linux-amd64 /opt/prometheus \
    && rm prometheus-2.48.0.linux-amd64.tar.gz

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY metrics_generator.py .
COPY dashboard.py .
COPY prometheus.yml /opt/prometheus/prometheus.yml

# Update prometheus.yml to use localhost
RUN sed -i 's/model-metrics:8000/localhost:8000/g' /opt/prometheus/prometheus.yml

# Create supervisor configuration that starts dashboard on Render's PORT
RUN printf '[supervisord]\n\
nodaemon=true\n\
user=root\n\
\n\
[program:metrics]\n\
command=python /app/metrics_generator.py\n\
autostart=true\n\
autorestart=true\n\
stdout_logfile=/dev/stdout\n\
stdout_logfile_maxbytes=0\n\
stderr_logfile=/dev/stderr\n\
stderr_logfile_maxbytes=0\n\
priority=1\n\
\n\
[program:prometheus]\n\
command=/opt/prometheus/prometheus --config.file=/opt/prometheus/prometheus.yml --storage.tsdb.path=/tmp/prometheus --web.listen-address=:9090\n\
autostart=true\n\
autorestart=true\n\
stdout_logfile=/dev/stdout\n\
stdout_logfile_maxbytes=0\n\
stderr_logfile=/dev/stderr\n\
stderr_logfile_maxbytes=0\n\
priority=2\n\
\n\
[program:dashboard]\n\
command=python /app/dashboard.py\n\
autostart=true\n\
autorestart=true\n\
stdout_logfile=/dev/stdout\n\
stdout_logfile_maxbytes=0\n\
stderr_logfile=/dev/stderr\n\
stderr_logfile_maxbytes=0\n\
priority=3\n' > /etc/supervisor/conf.d/supervisord.conf

# Expose port 8050 for the dashboard
EXPOSE 8050

# Health check for the dashboard
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8050/ || exit 1

# Start all services with supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
