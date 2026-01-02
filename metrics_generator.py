import time
import random
from prometheus_client import start_http_server, Gauge, Counter, Histogram
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define Prometheus metrics
model_accuracy = Gauge('model_accuracy', 'Current model accuracy')
model_precision = Gauge('model_precision', 'Current model precision')
model_recall = Gauge('model_recall', 'Current model recall')
model_f1_score = Gauge('model_f1_score', 'Current model F1 score')

prediction_latency = Histogram(
    'prediction_latency_seconds',
    'Latency of model predictions',
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 2.0)
)

total_predictions = Counter('total_predictions', 'Total number of predictions made')
total_errors = Counter('total_errors', 'Total number of prediction errors')

# CPU and Memory simulation
cpu_usage = Gauge('cpu_usage_percent', 'CPU usage percentage')
memory_usage = Gauge('memory_usage_mb', 'Memory usage in MB')

def generate_metrics():
    """Generate realistic model metrics with some variance"""
    
    # Base values with realistic ranges
    base_accuracy = 0.85
    base_precision = 0.83
    base_recall = 0.87
    base_f1 = 0.85
    
    # Add some realistic variance
    accuracy = max(0.0, min(1.0, base_accuracy + random.uniform(-0.05, 0.05)))
    precision = max(0.0, min(1.0, base_precision + random.uniform(-0.04, 0.04)))
    recall = max(0.0, min(1.0, base_recall + random.uniform(-0.04, 0.04)))
    f1 = max(0.0, min(1.0, base_f1 + random.uniform(-0.04, 0.04)))
    
    # Update metrics
    model_accuracy.set(accuracy)
    model_precision.set(precision)
    model_recall.set(recall)
    model_f1_score.set(f1)
    
    # Simulate predictions with varying latency
    if random.random() > 0.3:  # 70% chance of prediction
        latency = random.uniform(0.001, 0.1)
        prediction_latency.observe(latency)
        total_predictions.inc()
        
        # Occasional errors (5% chance)
        if random.random() < 0.05:
            total_errors.inc()
    
    # Simulate resource usage
    cpu = random.uniform(20, 80)
    memory = random.uniform(200, 800)
    cpu_usage.set(cpu)
    memory_usage.set(memory)
    
    logger.info(f"Updated metrics - Accuracy: {accuracy:.4f}, Precision: {precision:.4f}, "
                f"Recall: {recall:.4f}, F1: {f1:.4f}")

if __name__ == '__main__':
    # Start Prometheus metrics server on port 8000
    logger.info("Starting metrics server on port 8000...")
    start_http_server(8000)
    logger.info("Metrics server started successfully!")
    
    # Generate metrics continuously
    while True:
        try:
            generate_metrics()
            time.sleep(5)  # Update every 5 seconds
        except Exception as e:
            logger.error(f"Error generating metrics: {e}")
            time.sleep(5)
