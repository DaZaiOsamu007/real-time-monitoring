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

# Prometheus URL
PROM_URL = os.environ.get("PROM_URL", "http://localhost:9090")
logger.info(f"Connecting to Prometheus at: {PROM_URL}")

# Initialize Dash app with external stylesheet
app = dash.Dash(__name__)
app.title = "ML Model Monitoring"

# Store historical data
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

def get_active_alerts():
    """Get currently firing alerts from Prometheus"""
    try:
        url = f"{PROM_URL}/api/v1/alerts"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        result = response.json()
        
        if result['status'] == 'success':
            alerts = result['data']['alerts']
            firing_alerts = [a for a in alerts if a['state'] == 'firing']
            return firing_alerts
        return []
    except Exception as e:
        logger.error(f"Error querying alerts: {e}")
        return []

# Enhanced color scheme
COLORS = {
    'primary': '#2E86DE',
    'success': '#10B981',
    'warning': '#F59E0B',
    'danger': '#EF4444',
    'purple': '#8B5CF6',
    'dark': '#1F2937',
    'light': '#F9FAFB',
    'gradient_start': '#667eea',
    'gradient_end': '#764ba2'
}

# Define app layout with modern styling
app.layout = html.Div([
    # Header with gradient background
    html.Div([
        html.Div([
            html.Div([
                html.Span('🤖', style={'fontSize': '36px', 'marginRight': '15px'}),
                html.H1("Real-Time Model Monitoring", 
                       style={
                           'display': 'inline-block',
                           'margin': 0,
                           'color': 'white',
                           'fontWeight': '700',
                           'fontSize': '28px'
                       }),
            ], style={'display': 'flex', 'alignItems': 'center'}),
            html.Div(id='last-update', style={
                'color': 'rgba(255,255,255,0.9)',
                'fontSize': '14px',
                'marginTop': '5px'
            })
        ], style={'maxWidth': '1400px', 'margin': '0 auto', 'padding': '0 20px'})
    ], style={
        'background': f'linear-gradient(135deg, {COLORS["gradient_start"]} 0%, {COLORS["gradient_end"]} 100%)',
        'padding': '30px 0',
        'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
        'marginBottom': '30px'
    }),
    
    html.Div([
        # Status and Alerts Row
        html.Div([
            html.Div(id='connection-status', style={'flex': 1}),
            html.Div(id='alerts-section', style={'flex': 2, 'marginLeft': '20px'}),
        ], style={
            'display': 'flex',
            'marginBottom': '30px',
            'gap': '20px'
        }),
        
        # Key Metrics Cards with enhanced styling
        html.Div([
            # Accuracy Card
            html.Div([
                html.Div([
                    html.Div('📊', style={'fontSize': '32px', 'marginBottom': '10px'}),
                    html.H4("Accuracy", style={'color': '#6B7280', 'margin': '0 0 10px 0', 'fontSize': '14px', 'fontWeight': '600', 'textTransform': 'uppercase'}),
                    html.H2(id='accuracy-value', style={'color': COLORS['primary'], 'margin': 0, 'fontSize': '36px', 'fontWeight': '700'}),
                    html.Div(id='accuracy-change', style={'fontSize': '12px', 'marginTop': '8px', 'color': '#6B7280'})
                ])
            ], style={
                'backgroundColor': 'white',
                'padding': '25px',
                'borderRadius': '16px',
                'boxShadow': '0 4px 6px rgba(0,0,0,0.07)',
                'textAlign': 'center',
                'border': f'2px solid {COLORS["primary"]}',
                'transition': 'transform 0.2s, box-shadow 0.2s',
                'cursor': 'pointer'
            }, className='metric-card'),
            
            # Precision Card
            html.Div([
                html.Div([
                    html.Div('🎯', style={'fontSize': '32px', 'marginBottom': '10px'}),
                    html.H4("Precision", style={'color': '#6B7280', 'margin': '0 0 10px 0', 'fontSize': '14px', 'fontWeight': '600', 'textTransform': 'uppercase'}),
                    html.H2(id='precision-value', style={'color': COLORS['purple'], 'margin': 0, 'fontSize': '36px', 'fontWeight': '700'}),
                    html.Div(id='precision-change', style={'fontSize': '12px', 'marginTop': '8px', 'color': '#6B7280'})
                ])
            ], style={
                'backgroundColor': 'white',
                'padding': '25px',
                'borderRadius': '16px',
                'boxShadow': '0 4px 6px rgba(0,0,0,0.07)',
                'textAlign': 'center',
                'border': f'2px solid {COLORS["purple"]}',
                'transition': 'transform 0.2s, box-shadow 0.2s',
                'cursor': 'pointer'
            }, className='metric-card'),
            
            # Recall Card
            html.Div([
                html.Div([
                    html.Div('🔍', style={'fontSize': '32px', 'marginBottom': '10px'}),
                    html.H4("Recall", style={'color': '#6B7280', 'margin': '0 0 10px 0', 'fontSize': '14px', 'fontWeight': '600', 'textTransform': 'uppercase'}),
                    html.H2(id='recall-value', style={'color': COLORS['danger'], 'margin': 0, 'fontSize': '36px', 'fontWeight': '700'}),
                    html.Div(id='recall-change', style={'fontSize': '12px', 'marginTop': '8px', 'color': '#6B7280'})
                ])
            ], style={
                'backgroundColor': 'white',
                'padding': '25px',
                'borderRadius': '16px',
                'boxShadow': '0 4px 6px rgba(0,0,0,0.07)',
                'textAlign': 'center',
                'border': f'2px solid {COLORS["danger"]}',
                'transition': 'transform 0.2s, box-shadow 0.2s',
                'cursor': 'pointer'
            }, className='metric-card'),
            
            # F1 Score Card
            html.Div([
                html.Div([
                    html.Div('⚡', style={'fontSize': '32px', 'marginBottom': '10px'}),
                    html.H4("F1 Score", style={'color': '#6B7280', 'margin': '0 0 10px 0', 'fontSize': '14px', 'fontWeight': '600', 'textTransform': 'uppercase'}),
                    html.H2(id='f1-value', style={'color': COLORS['warning'], 'margin': 0, 'fontSize': '36px', 'fontWeight': '700'}),
                    html.Div(id='f1-change', style={'fontSize': '12px', 'marginTop': '8px', 'color': '#6B7280'})
                ])
            ], style={
                'backgroundColor': 'white',
                'padding': '25px',
                'borderRadius': '16px',
                'boxShadow': '0 4px 6px rgba(0,0,0,0.07)',
                'textAlign': 'center',
                'border': f'2px solid {COLORS["warning"]}',
                'transition': 'transform 0.2s, box-shadow 0.2s',
                'cursor': 'pointer'
            }, className='metric-card'),
        ], style={
            'display': 'grid',
            'gridTemplateColumns': 'repeat(auto-fit, minmax(250px, 1fr))',
            'gap': '20px',
            'marginBottom': '30px'
        }),
        
        # Performance Graph with card wrapper
        html.Div([
            html.Div([
                html.H3("📈 Model Performance Trends", style={
                    'margin': '0 0 20px 0',
                    'color': COLORS['dark'],
                    'fontSize': '20px',
                    'fontWeight': '600'
                }),
                dcc.Graph(id='performance-graph', config={'displayModeBar': False})
            ], style={
                'backgroundColor': 'white',
                'padding': '25px',
                'borderRadius': '16px',
                'boxShadow': '0 4px 6px rgba(0,0,0,0.07)'
            })
        ], style={'marginBottom': '30px'}),
        
        # Predictions and System Metrics
        html.Div([
            # Predictions Graph
            html.Div([
                html.Div([
                    html.H3("📊 Prediction Analytics", style={
                        'margin': '0 0 20px 0',
                        'color': COLORS['dark'],
                        'fontSize': '20px',
                        'fontWeight': '600'
                    }),
                    dcc.Graph(id='predictions-graph', config={'displayModeBar': False})
                ], style={
                    'backgroundColor': 'white',
                    'padding': '25px',
                    'borderRadius': '16px',
                    'boxShadow': '0 4px 6px rgba(0,0,0,0.07)',
                    'height': '100%'
                })
            ], style={'flex': 1}),
            
            # System Resources Graph
            html.Div([
                html.Div([
                    html.H3("💻 System Resources", style={
                        'margin': '0 0 20px 0',
                        'color': COLORS['dark'],
                        'fontSize': '20px',
                        'fontWeight': '600'
                    }),
                    dcc.Graph(id='resources-graph', config={'displayModeBar': False})
                ], style={
                    'backgroundColor': 'white',
                    'padding': '25px',
                    'borderRadius': '16px',
                    'boxShadow': '0 4px 6px rgba(0,0,0,0.07)',
                    'height': '100%'
                })
            ], style={'flex': 1, 'marginLeft': '20px'})
        ], style={'display': 'flex', 'gap': '20px'}),
        
        # Auto-refresh interval
        dcc.Interval(
            id='interval-component',
            interval=2000,
            n_intervals=0
        )
    ], style={
        'maxWidth': '1400px',
        'margin': '0 auto',
        'padding': '0 20px 40px 20px',
        'backgroundColor': COLORS['light'],
        'minHeight': '100vh'
    })
], style={
    'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    'backgroundColor': COLORS['light']
})

# Add custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                margin: 0;
                padding: 0;
            }
            .metric-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 12px 24px rgba(0,0,0,0.15) !important;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .metric-card {
                animation: fadeIn 0.5s ease-out;
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
     Output('accuracy-change', 'children'),
     Output('precision-change', 'children'),
     Output('recall-change', 'children'),
     Output('f1-change', 'children'),
     Output('connection-status', 'children'),
     Output('alerts-section', 'children'),
     Output('last-update', 'children'),
     Output('performance-graph', 'figure'),
     Output('predictions-graph', 'figure'),
     Output('resources-graph', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    # Query metrics
    accuracy = query_prometheus('model_accuracy')
    precision = query_prometheus('model_precision')
    recall = query_prometheus('model_recall')
    f1 = query_prometheus('model_f1_score')
    predictions = query_prometheus('total_predictions')
    errors = query_prometheus('total_errors')
    cpu = query_prometheus('cpu_usage_percent')
    memory = query_prometheus('memory_usage_mb')
    
    # Get alerts
    active_alerts = get_active_alerts()
    
    # Connection status with modern design
    if accuracy is not None:
        status = html.Div([
            html.Div([
                html.Span('●', style={'color': COLORS['success'], 'fontSize': '20px', 'marginRight': '10px', 'animation': 'pulse 2s infinite'}),
                html.Div([
                    html.Strong("Connected", style={'display': 'block', 'fontSize': '16px'}),
                    html.Span("Real-time data streaming", style={'fontSize': '12px', 'color': '#6B7280'})
                ])
            ], style={'display': 'flex', 'alignItems': 'center'})
        ], style={
            'backgroundColor': 'white',
            'padding': '20px',
            'borderRadius': '12px',
            'boxShadow': '0 4px 6px rgba(0,0,0,0.07)',
            'border': f'2px solid {COLORS["success"]}'
        })
    else:
        status = html.Div([
            html.Div([
                html.Span('●', style={'color': COLORS['danger'], 'fontSize': '20px', 'marginRight': '10px'}),
                html.Div([
                    html.Strong("Disconnected", style={'display': 'block', 'fontSize': '16px'}),
                    html.Span("Waiting for Prometheus...", style={'fontSize': '12px', 'color': '#6B7280'})
                ])
            ], style={'display': 'flex', 'alignItems': 'center'})
        ], style={
            'backgroundColor': 'white',
            'padding': '20px',
            'borderRadius': '12px',
            'boxShadow': '0 4px 6px rgba(0,0,0,0.07)',
            'border': f'2px solid {COLORS["danger"]}'
        })
    
    # Alerts display with modern design
    if active_alerts:
        alert_cards = []
        for alert in active_alerts:
            severity = alert['labels'].get('severity', 'info')
            color = COLORS['danger'] if severity == 'critical' else COLORS['warning']
            icon = '🚨' if severity == 'critical' else '⚠️'
            
            alert_cards.append(
                html.Div([
                    html.Div([
                        html.Span(icon, style={'fontSize': '24px', 'marginRight': '15px'}),
                        html.Div([
                            html.Strong(alert['labels'].get('alertname', 'Alert'), 
                                       style={'fontSize': '16px', 'display': 'block', 'marginBottom': '5px'}),
                            html.P(alert['annotations'].get('description', 'No description'),
                                  style={'margin': 0, 'fontSize': '14px', 'opacity': '0.9'})
                        ], style={'flex': 1})
                    ], style={'display': 'flex', 'alignItems': 'flex-start'})
                ], style={
                    'backgroundColor': color,
                    'color': 'white',
                    'padding': '20px',
                    'borderRadius': '12px',
                    'marginBottom': '10px',
                    'boxShadow': '0 4px 12px rgba(0,0,0,0.15)',
                    'animation': 'fadeIn 0.3s ease-out'
                })
            )
        alerts_display = html.Div([
            html.H4("Active Alerts", style={'color': COLORS['dark'], 'marginBottom': '15px', 'fontSize': '18px', 'fontWeight': '600'}),
            html.Div(alert_cards)
        ], style={
            'backgroundColor': 'white',
            'padding': '20px',
            'borderRadius': '12px',
            'boxShadow': '0 4px 6px rgba(0,0,0,0.07)'
        })
    else:
        alerts_display = html.Div([
            html.Div([
                html.Span('✓', style={'fontSize': '32px', 'color': COLORS['success'], 'marginRight': '15px'}),
                html.Div([
                    html.Strong("All Systems Normal", style={'display': 'block', 'fontSize': '16px', 'color': COLORS['dark']}),
                    html.Span("No active alerts detected", style={'fontSize': '14px', 'color': '#6B7280'})
                ])
            ], style={'display': 'flex', 'alignItems': 'center'})
        ], style={
            'backgroundColor': 'white',
            'padding': '20px',
            'borderRadius': '12px',
            'boxShadow': '0 4px 6px rgba(0,0,0,0.07)',
            'border': f'2px solid {COLORS["success"]}'
        })
    
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
    
    # Calculate changes
    def get_change(history_key):
        if len(metrics_history[history_key]) >= 2:
            prev = metrics_history[history_key][-2]
            curr = metrics_history[history_key][-1]
            if prev and curr:
                change = ((curr - prev) / prev) * 100
                arrow = '↑' if change > 0 else '↓' if change < 0 else '→'
                color = COLORS['success'] if change > 0 else COLORS['danger'] if change < 0 else '#6B7280'
                return html.Span(f"{arrow} {abs(change):.2f}%", style={'color': color, 'fontWeight': '600'})
        return html.Span("—", style={'color': '#6B7280'})
    
    # Format display values
    acc_display = f"{accuracy:.4f}" if accuracy else "N/A"
    prec_display = f"{precision:.4f}" if precision else "N/A"
    rec_display = f"{recall:.4f}" if recall else "N/A"
    f1_display = f"{f1:.4f}" if f1 else "N/A"
    
    # Last update time
    from datetime import datetime
    last_update = f"Last updated: {datetime.now().strftime('%H:%M:%S')}"
    
    # Enhanced performance graph
    performance_fig = go.Figure()
    
    colors_map = {
        'accuracy': COLORS['primary'],
        'precision': COLORS['purple'],
        'recall': COLORS['danger'],
        'f1_score': COLORS['warning']
    }
    
    for metric, color in colors_map.items():
        performance_fig.add_trace(go.Scatter(
            y=list(metrics_history[metric]),
            mode='lines+markers',
            name=metric.replace('_', ' ').title(),
            line=dict(color=color, width=3),
            marker=dict(size=6),
            hovertemplate='<b>%{fullData.name}</b><br>Value: %{y:.4f}<extra></extra>'
        ))
    
    performance_fig.update_layout(
        yaxis_title="Score",
        yaxis_range=[0, 1],
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='inherit', size=12),
        margin=dict(l=50, r=20, t=10, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis=dict(showgrid=True, gridcolor='#E5E7EB'),
        yaxis=dict(showgrid=True, gridcolor='#E5E7EB')
    )
    
    # Enhanced predictions graph
    predictions_fig = go.Figure()
    predictions_fig.add_trace(go.Scatter(
        y=list(metrics_history['predictions']),
        mode='lines+markers',
        name='Total Predictions',
        line=dict(color=COLORS['success'], width=3),
        fill='tozeroy',
        fillcolor=f'rgba(16, 185, 129, 0.1)'
    ))
    predictions_fig.add_trace(go.Scatter(
        y=list(metrics_history['errors']),
        mode='lines+markers',
        name='Errors',
        line=dict(color=COLORS['danger'], width=3),
        fill='tozeroy',
        fillcolor=f'rgba(239, 68, 68, 0.1)'
    ))
    
    predictions_fig.update_layout(
        yaxis_title="Count",
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='inherit', size=12),
        margin=dict(l=50, r=20, t=10, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=True, gridcolor='#E5E7EB'),
        yaxis=dict(showgrid=True, gridcolor='#E5E7EB')
    )
    
    # Enhanced resources graph
    resources_fig = go.Figure()
    resources_fig.add_trace(go.Scatter(
        y=list(metrics_history['cpu']),
        mode='lines+markers',
        name='CPU Usage (%)',
        line=dict(color='#F59E0B', width=3),
        fill='tozeroy',
        fillcolor='rgba(245, 158, 11, 0.1)'
    ))
    resources_fig.add_trace(go.Scatter(
        y=list(metrics_history['memory']),
        mode='lines+markers',
        name='Memory (MB)',
        line=dict(color='#10B981', width=3),
        yaxis='y2'
    ))
    
    resources_fig.update_layout(
        yaxis_title="CPU %",
        yaxis2=dict(title="Memory MB", overlaying='y', side='right'),
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='inherit', size=12),
        margin=dict(l=50, r=50, t=10, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=True, gridcolor='#E5E7EB'),
        yaxis=dict(showgrid=True, gridcolor='#E5E7EB')
    )
    
    return (acc_display, prec_display, rec_display, f1_display,
            get_change('accuracy'), get_change('precision'), get_change('recall'), get_change('f1_score'),
            status, alerts_display, last_update,
            performance_fig, predictions_fig, resources_fig)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"Starting dashboard server on port {port}...")
    app.run_server(host='0.0.0.0', port=port, debug=False)
