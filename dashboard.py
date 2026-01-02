import os
import requests
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
from collections import deque
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus URL from environment variable or default
PROM_URL = os.environ.get("PROM_URL", "http://prometheus:9090")
logger.info(f"Connecting to Prometheus at: {PROM_URL}")

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Real-Time Model Monitoring"

# Store historical data (keep last 50 points)
history_length = 50
metrics_history = {
    'accuracy': deque(maxlen=history_length),
    'precision': deque(maxlen=history_length),
    'recall': deque(maxlen=history_length),
    'f1_score': deque(maxlen=history_length),
    'latency': deque(maxlen=history_length),
    'predictions': deque(maxlen=history_length),
    'errors': deque(maxlen=history_length),
    'cpu': deque(maxlen=history_length),
    'memory': deque(maxlen=history_length),
    'timestamps': deque(maxlen=history_length)
}

def query_prometheus(metric_name):
    """Query Prometheus for a specific metric"""
    try:
        url = f"{PROM_URL}/api/v1/query"
        response = requests.get(url, params={'query': metric_name}, timeout=5)
        response.raise_for_status()
        result = response.json()
        
        if result['status'] == 'success' and result['data']['result']:
            value = float(result['data']['result'][0]['value'][1])
            return value
        return None
    except Exception as e:
        logger.error(f"Error querying Prometheus for {metric_name}: {e}")
        return None

# Define app layout
app.layout = html.Div([
    html.Div([
        html.H1("🤖 Real-Time Model Monitoring Dashboard", 
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 30}),
        
        # Status indicator
        html.Div(id='connection-status', style={'textAlign': 'center', 'marginBottom': 20}),
        
        # Key Metrics Cards
        html.Div([
            html.Div([
                html.H3("Accuracy", style={'color': '#3498db'}),
                html.H2(id='accuracy-value', style={'color': '#2c3e50'})
            ], className='metric-card'),
            
            html.Div([
                html.H3("Precision", style={'color': '#9b59b6'}),
                html.H2(id='precision-value', style={'color': '#2c3e50'})
            ], className='metric-card'),
            
            html.Div([
                html.H3("Recall", style={'color': '#e74c3c'}),
                html.H2(id='recall-value', style={'color': '#2c3e50'})
            ], className='metric-card'),
            
            html.Div([
                html.H3("F1 Score", style={'color': '#f39c12'}),
                html.H2(id='f1-value', style={'color': '#2c3e50'})
            ], className='metric-card'),
        ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': 30}),
        
        # Performance Metrics Graph
        html.Div([
            html.H3("Model Performance Over Time", style={'textAlign': 'center'}),
            dcc.Graph(id='performance-graph')
        ], style={'marginBottom': 30}),
        
        # Predictions and System Metrics
        html.Div([
            html.Div([
                html.H3("Prediction Statistics", style={'textAlign': 'center'}),
                dcc.Graph(id='predictions-graph')
            ], style={'width': '48%', 'display': 'inline-block'}),
            
            html.Div([
                html.H3("System Resources", style={'textAlign': 'center'}),
                dcc.Graph(id='resources-graph')
            ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '4%'})
        ]),
        
        # Auto-refresh interval
        dcc.Interval(
            id='interval-component',
            interval=2000,  # Update every 2 seconds
            n_intervals=0
        )
    ], style={'padding': 20})
], style={'fontFamily': 'Arial, sans-serif', 'backgroundColor': '#ecf0f1'})

# Add CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            .metric-card {
                backgroundColor: white;
                padding: 20px;
                borderRadius: 10px;
                boxShadow: 0 2px 4px rgba(0,0,0,0.1);
                textAlign: center;
                minWidth: 200px;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

@app.callback(
    [Output('accuracy-value', 'children'),
     Output('precision-value', 'children'),
     Output('recall-value', 'children'),
     Output('f1-value', 'children'),
     Output('connection-status', 'children'),
     Output('performance-graph', 'figure'),
     Output('predictions-graph', 'figure'),
     Output('resources-graph', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    """Update all dashboard components"""
    
    # Query current metrics
    accuracy = query_prometheus('model_accuracy')
    precision = query_prometheus('model_precision')
    recall = query_prometheus('model_recall')
    f1 = query_prometheus('model_f1_score')
    predictions = query_prometheus('total_predictions')
    errors = query_prometheus('total_errors')
    cpu = query_prometheus('cpu_usage_percent')
    memory = query_prometheus('memory_usage_mb')
    
    # Connection status
    if accuracy is not None:
        status = html.Div("🟢 Connected to Prometheus", 
                         style={'color': 'green', 'fontWeight': 'bold'})
    else:
        status = html.Div("🔴 Disconnected from Prometheus", 
                         style={'color': 'red', 'fontWeight': 'bold'})
    
    # Update history
    import time
    current_time = time.time()
    metrics_history['timestamps'].append(current_time)
    metrics_history['accuracy'].append(accuracy if accuracy else 0)
    metrics_history['precision'].append(precision if precision else 0)
    metrics_history['recall'].append(recall if recall else 0)
    metrics_history['f1_score'].append(f1 if f1 else 0)
    metrics_history['predictions'].append(predictions if predictions else 0)
    metrics_history['errors'].append(errors if errors else 0)
    metrics_history['cpu'].append(cpu if cpu else 0)
    metrics_history['memory'].append(memory if memory else 0)
    
    # Format display values
    acc_display = f"{accuracy:.4f}" if accuracy else "N/A"
    prec_display = f"{precision:.4f}" if precision else "N/A"
    rec_display = f"{recall:.4f}" if recall else "N/A"
    f1_display = f"{f1:.4f}" if f1 else "N/A"
    
    # Performance graph
    performance_fig = go.Figure()
    performance_fig.add_trace(go.Scatter(
        y=list(metrics_history['accuracy']),
        mode='lines+markers',
        name='Accuracy',
        line=dict(color='#3498db', width=2)
    ))
    performance_fig.add_trace(go.Scatter(
        y=list(metrics_history['precision']),
        mode='lines+markers',
        name='Precision',
        line=dict(color='#9b59b6', width=2)
    ))
    performance_fig.add_trace(go.Scatter(
        y=list(metrics_history['recall']),
        mode='lines+markers',
        name='Recall',
        line=dict(color='#e74c3c', width=2)
    ))
    performance_fig.add_trace(go.Scatter(
        y=list(metrics_history['f1_score']),
        mode='lines+markers',
        name='F1 Score',
        line=dict(color='#f39c12', width=2)
    ))
    performance_fig.update_layout(
        yaxis_title="Score",
        yaxis_range=[0, 1],
        hovermode='x unified',
        plot_bgcolor='white'
    )
    
    # Predictions graph
    predictions_fig = go.Figure()
    predictions_fig.add_trace(go.Scatter(
        y=list(metrics_history['predictions']),
        mode='lines+markers',
        name='Total Predictions',
        line=dict(color='#27ae60', width=2)
    ))
    predictions_fig.add_trace(go.Scatter(
        y=list(metrics_history['errors']),
        mode='lines+markers',
        name='Errors',
        line=dict(color='#e74c3c', width=2)
    ))
    predictions_fig.update_layout(
        yaxis_title="Count",
        hovermode='x unified',
        plot_bgcolor='white'
    )
    
    # Resources graph
    resources_fig = go.Figure()
    resources_fig.add_trace(go.Scatter(
        y=list(metrics_history['cpu']),
        mode='lines+markers',
        name='CPU Usage (%)',
        line=dict(color='#e67e22', width=2)
    ))
    resources_fig.add_trace(go.Scatter(
        y=list(metrics_history['memory']),
        mode='lines+markers',
        name='Memory (MB)',
        line=dict(color='#1abc9c', width=2),
        yaxis='y2'
    ))
    resources_fig.update_layout(
        yaxis_title="CPU %",
        yaxis2=dict(title="Memory MB", overlaying='y', side='right'),
        hovermode='x unified',
        plot_bgcolor='white'
    )
    
    return (acc_display, prec_display, rec_display, f1_display, status,
            performance_fig, predictions_fig, resources_fig)

if __name__ == '__main__':
    logger.info("Starting dashboard server on port 8050...")
    app.run_server(host='0.0.0.0', port=8050, debug=False)
