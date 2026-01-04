# Real-Time Model Monitoring System

A complete real-time monitoring solution for machine learning models with Prometheus metrics collection and a live Dash dashboard.

Features

- **Real-time Metrics**: Live model performance tracking (accuracy, precision, recall, F1 score)
- **Prometheus Integration**: Industry-standard metrics collection and storage
- **Alerting System**: Automated alerts for performance degradation, high latency, and resource issues
- **Interactive Dashboard**: Beautiful Dash-based UI with auto-updating charts
- **Prediction Analytics**: Track total predictions and error rates
- **System Monitoring**: CPU and memory usage tracking
- **Alert Visualization**: Real-time display of firing alerts on dashboard
- **Single Container Deployment**: Easy deployment to Render or any Docker platform

Project Structure

```
real-time-monitoring/
├── Dockerfile                 # Main Dockerfile for Render deployment
├── Dockerfile.metrics         # Metrics service (for docker-compose)
├── Dockerfile.dashboard       # Dashboard service (for docker-compose)
├── docker-compose.yml         # Local development with Docker Compose
├── prometheus.yml             # Prometheus configuration
├── prometheus_alerts.yml      # Alert rules configuration
├── metrics_generator.py       # Generates model metrics
├── dashboard.py               # Dash dashboard application
├── requirements.txt           # Python dependencies
├── render.yaml               # Render deployment configuration
└── README.md                 # This file
```

## Setup Options

### Option 1: Deploy to Render (Recommended for Production)

1. **Create a new repository** and push all files:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Real-time monitoring system"
   git remote add origin YOUR_REPO_URL
   git push -u origin main
   ```

2. **Deploy to Render**:
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will automatically detect the `Dockerfile`
   - Set the following:
     - **Name**: real-time-monitoring
     - **Environment**: Docker
     - **Plan**: Free
   - Click "Create Web Service"

3. **Access your dashboard**:
   - Once deployed, visit: `https://YOUR-APP-NAME.onrender.com`
   - The dashboard will be live and updating in real-time!

### Option 2: Local Development with Docker Compose

1. **Install Docker and Docker Compose**

2. **Run the application**:
   ```bash
   docker-compose up --build
   ```

3. **Access the services**:
   - Dashboard: http://localhost:8050
   - Prometheus: http://localhost:9090
   - Metrics: http://localhost:8000/metrics

4. **Stop the application**:
   ```bash
   docker-compose down
   ```

### Option 3: Local Development without Docker

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Download and install Prometheus**:
   - Download from: https://prometheus.io/download/
   - Extract and copy `prometheus.yml` to the prometheus directory

3. **Run services in separate terminals**:

   Terminal 1 - Metrics Generator:
   ```bash
   python metrics_generator.py
   ```

   Terminal 2 - Prometheus:
   ```bash
   ./prometheus --config.file=prometheus.yml
   ```

   Terminal 3 - Dashboard:
   ```bash
   python dashboard.py
   ```

4. **Access**: Dashboard at http://localhost:8050

## Dashboard Features

- **Real-time Metrics Cards**: Display current accuracy, precision, recall, and F1 score
- **Alert Notifications**: Prominent display of active alerts with severity indicators
- **Performance Graph**: Historical trend of all model metrics
- **Prediction Statistics**: Track total predictions and errors over time
- **System Resources**: Monitor CPU and memory usage
- **Auto-refresh**: Updates every 2 seconds

## Alerting System

The system includes automated alerts for:

### Model Performance Alerts:
- **LowModelAccuracy**: Warning when accuracy drops below 80%
- **CriticalModelAccuracy**: Critical alert when accuracy drops below 70%

### Operational Alerts:
- **HighErrorRate**: Warning when error rate exceeds 0.1 errors/second
- **HighPredictionLatency**: Warning when 95th percentile latency exceeds 500ms

### System Resource Alerts:
- **HighCPUUsage**: Warning when CPU usage exceeds 85%
- **HighMemoryUsage**: Warning when memory usage exceeds 750MB

All alerts are:
- Evaluated every 15 seconds
- Displayed prominently on the dashboard
- Color-coded by severity (yellow for warning, red for critical)
- Include detailed descriptions and current metric values

## Configuration

### Prometheus Configuration (`prometheus.yml`)

- Scrape interval: 15 seconds
- Scrape timeout: 10 seconds
- Targets: model-metrics service on port 8000

### Metrics Generator (`metrics_generator.py`)

- Updates metrics every 5 seconds
- Simulates realistic model performance with variance
- Tracks predictions, errors, and system resources

### Dashboard (`dashboard.py`)

- Updates every 2 seconds
- Keeps last 50 data points in history
- Connects to Prometheus API

## Metrics Available

### Model Performance Metrics:
- `model_accuracy`: Current model accuracy (0-1)
- `model_precision`: Current model precision (0-1)
- `model_recall`: Current model recall (0-1)
- `model_f1_score`: Current F1 score (0-1)

### Prediction Metrics:
- `total_predictions`: Total number of predictions made
- `total_errors`: Total number of prediction errors
- `prediction_latency_seconds`: Histogram of prediction latencies

### System Metrics:
- `cpu_usage_percent`: CPU usage percentage
- `memory_usage_mb`: Memory usage in megabytes

## Troubleshooting

### Dashboard shows "Disconnected from Prometheus"
- Check that all services are running
- Verify Prometheus is accessible at the configured URL
- Check container logs: `docker-compose logs prometheus`

### Metrics not updating
- Verify metrics generator is running: `docker-compose logs model-metrics`
- Check Prometheus targets: http://localhost:9090/targets
- Ensure firewall isn't blocking ports

### Render deployment issues
- Check build logs in Render dashboard
- Ensure all files are committed to git
- Verify Dockerfile is in the root directory

## Environment Variables

- `PROM_URL`: Prometheus URL (default: `http://prometheus:9090`)
- `PORT`: Dashboard port (default: `8050`)

## Contributing

Feel free to open issues or submit pull requests for improvements!

## License

MIT License - feel free to use this project for your needs.

## Next Steps

- Add alerting rules in Prometheus
- Integrate with Grafana for advanced visualization
- Add authentication for production deployment
- Implement metric persistence across restarts
- Add more ML-specific metrics (drift detection, data quality, etc.)

