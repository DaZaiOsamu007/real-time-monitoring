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

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "ML Model Monitoring"

# Store historical data
history_length = 50
metrics_history = {
    'accuracy': deque(maxlen=history_length),
    'precision': deque(maxlen=history_length),
    'recall': deque(maxlen=history_length),
    'f1_score': deque(maxlen=history_length),
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

# Color scheme
COLORS = {
    'primary': '#3B82F6',
    'success': '#10B981', 
    'warning': '#F59E0B',
    'danger': '#EF4444',
    'purple': '#8B5CF6',
    'dark': '#111827',
    'gray': '#6B7280',
    'light_bg': '#F9FAFB',
    'card_bg': '#FFFFFF'
}

# Define app layout
app.layout = html.Div([
    # Minimalist Header
    html.Div([
        html.Div([
            html.H1([
                html.Span('🤖 ', style={'marginRight': '12px'}),
                'Model Monitor'
            ], style={
                'margin': 0,
                'color': COLORS['dark'],
                'fontSize': '32px',
                'fontWeight': '700',
                'letterSpacing': '-0.5px'
            }),
            html.Div([
                html.Span(id='connection-status-dot', style={
                    'width': '8px',
                    'height': '8px',
                    'borderRadius': '50%',
                    'backgroundColor': COLORS['success'],
                    'marginRight': '8px',
                    'display': 'inline-block'
                }),
                html.Span(id='connection-text', style={
                    'color': COLORS['gray'],
                    'fontSize': '14px',
                    'fontWeight': '500'
                })
            ], style={'display': 'flex', 'alignItems': 'center', 'marginTop': '8px'})
        ], style={
            'maxWidth': '1600px',
            'margin': '0 auto',
            'padding': '0 40px'
        })
    ], style={
        'backgroundColor': COLORS['card_bg'],
        'borderBottom': '1px solid #E5E7EB',
        'padding': '32px 0',
        'marginBottom': '40px'
    }),
    
    html.Div([
        # Alerts Section (if any)
        html.Div(id='alerts-section', style={'marginBottom': '32px'}),
        
        # Metric Cards - More Spacious
        html.Div([
            # Accuracy
            html.Div([
                html.Div('📊', style={'fontSize': '40px', 'marginBottom': '16px', 'opacity': '0.9'}),
                html.Div('Accuracy', style={
                    'fontSize': '13px',
                    'fontWeight': '600',
                    'color': COLORS['gray'],
                    'textTransform': 'uppercase',
                    'letterSpacing': '0.5px',
                    'marginBottom': '12px'
                }),
                html.Div(id='accuracy-value', style={
                    'fontSize': '48px',
                    'fontWeight': '700',
                    'color': COLORS['primary'],
                    'lineHeight': '1',
                    'marginBottom': '8px'
                }),
                html.Div(id='accuracy-change', style={
                    'fontSize': '14px',
                    'fontWeight': '500'
                })
            ], style={
                'backgroundColor': COLORS['card_bg'],
                'padding': '40px 32px',
                'borderRadius': '12px',
                'textAlign': 'center',
                'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
                'border': '1px solid #E5E7EB',
                'transition': 'all 0.3s ease'
            }, className='metric-card'),
            
            # Precision
            html.Div([
                html.Div('🎯', style={'fontSize': '40px', 'marginBottom': '16px', 'opacity': '0.9'}),
                html.Div('Precision', style={
                    'fontSize': '13px',
                    'fontWeight': '600',
                    'color': COLORS['gray'],
                    'textTransform': 'uppercase',
                    'letterSpacing': '0.5px',
                    'marginBottom': '12px'
                }),
                html.Div(id='precision-value', style={
                    'fontSize': '48px',
                    'fontWeight': '700',
                    'color': COLORS['purple'],
                    'lineHeight': '1',
                    'marginBottom': '8px'
                }),
                html.Div(id='precision-change', style={
                    'fontSize': '14px',
                    'fontWeight': '500'
                })
            ], style={
                'backgroundColor': COLORS['card_bg'],
                'padding': '40px 32px',
                'borderRadius': '12px',
                'textAlign': 'center',
                'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
                'border': '1px solid #E5E7EB',
                'transition': 'all 0.3s ease'
            }, className='metric-card'),
            
            # Recall
            html.Div([
                html.Div('🔍', style={'fontSize': '40px', 'marginBottom': '16px', 'opacity': '0.9'}),
                html.Div('Recall', style={
                    'fontSize': '13px',
                    'fontWeight': '600',
                    'color': COLORS['gray'],
                    'textTransform': 'uppercase',
                    'letterSpacing': '0.5px',
                    'marginBottom': '12px'
                }),
                html.Div(id='recall-value', style={
                    'fontSize': '48px',
                    'fontWeight': '700',
                    'color': COLORS['danger'],
                    'lineHeight': '1',
                    'marginBottom': '8px'
                }),
                html.Div(id='recall-change', style={
                    'fontSize': '14px',
                    'fontWeight': '500'
                })
            ], style={
                'backgroundColor': COLORS['card_bg'],
                'padding': '40px 32px',
                'borderRadius': '12px',
                'textAlign': 'center',
                'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
                'border': '1px solid #E5E7EB',
                'transition': 'all 0.3s ease'
            }, className='metric-card'),
            
            # F1 Score
            html.Div([
                html.Div('⚡', style={'fontSize': '40px', 'marginBottom': '16px', 'opacity': '0.9'}),
                html.Div('F1 Score', style={
                    'fontSize': '13px',
                    'fontWeight': '600',
                    'color': COLORS['gray'],
                    'textTransform': 'uppercase',
                    'letterSpacing': '0.5px',
                    'marginBottom': '12px'
                }),
                html.Div(id='f1-value', style={
                    'fontSize': '48px',
                    'fontWeight': '700',
                    'color': COLORS['warning'],
                    'lineHeight': '1',
                    'marginBottom': '8px'
                }),
                html.Div(id='f1-change', style={
                    'fontSize': '14px',
                    'fontWeight': '500'
                })
            ], style={
                'backgroundColor': COLORS['card_bg'],
                'padding': '40px 32px',
                'borderRadius': '12px',
                'textAlign': 'center',
                'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
                'border': '1px solid #E5E7EB',
                'transition': 'all 0.3s ease'
            }, className='metric-card'),
        ], style={
            'display': 'grid',
            'gridTemplateColumns': 'repeat(auto-fit, minmax(280px, 1fr))',
            'gap': '24px',
            'marginBottom': '48px'
        }),
        
        # Performance Graph - Full Width
        html.Div([
            html.Div([
                html.H2('Performance Trends', style={
                    'fontSize': '20px',
                    'fontWeight': '600',
                    'color': COLORS['dark'],
                    'margin': '0 0 24px 0'
                }),
                dcc.Graph(
                    id='performance-graph',
                    config={'displayModeBar': False},
                    style={'height': '400px'}
                )
            ], style={
                'backgroundColor': COLORS['card_bg'],
                'padding': '32px',
                'borderRadius': '12px',
                'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
                'border': '1px solid #E5E7EB'
            })
        ], style={'marginBottom': '32px'}),
        
        # Bottom Row - Side by Side
        html.Div([
            # Predictions
            html.Div([
                html.Div([
                    html.H2('Predictions', style={
                        'fontSize': '18px',
                        'fontWeight': '600',
                        'color': COLORS['dark'],
                        'margin': '0 0 24px 0'
                    }),
                    dcc.Graph(
                        id='predictions-graph',
                        config={'displayModeBar': False},
                        style={'height': '300px'}
                    )
                ], style={
                    'backgroundColor': COLORS['card_bg'],
                    'padding': '28px',
                    'borderRadius': '12px',
                    'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
                    'border': '1px solid #E5E7EB',
                    'height': '100%'
                })
            ], style={'flex': '1'}),
            
            # Resources
            html.Div([
                html.Div([
                    html.H2('Resources', style={
                        'fontSize': '18px',
                        'fontWeight': '600',
                        'color': COLORS['dark'],
                        'margin': '0 0 24px 0'
                    }),
                    dcc.Graph(
                        id='resources-graph',
                        config={'displayModeBar': False},
                        style={'height': '300px'}
                    )
                ], style={
                    'backgroundColor': COLORS['card_bg'],
                    'padding': '28px',
                    'borderRadius': '12px',
                    'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
                    'border': '1px solid #E5E7EB',
                    'height': '100%'
                })
            ], style={'flex': '1'})
        ], style={
            'display': 'flex',
            'gap': '24px',
            'marginBottom': '40px'
        }),
        
        # Auto-refresh
        dcc.Interval(id='interval-component', interval=2000, n_intervals=0)
        
    ], style={
        'maxWidth': '1600px',
        'margin': '0 auto',
        'padding': '0 40px 60px 40px'
    })
], style={
    'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    'backgroundColor': COLORS['light_bg'],
    'minHeight': '100vh'
})

# Custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            * { box-sizing: border-box; }
            body { margin: 0; padding: 0; }
            .metric-card:hover {
                transform: translateY(-4px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
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
     Output('connection-status-dot', 'style'),
     Output('connection-text', 'children'),
     Output('alerts-section', 'children'),
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
    
    # Connection status
    if accuracy is not None:
        dot_style = {
            'width': '8px',
            'height': '8px',
            'borderRadius': '50%',
            'backgroundColor': COLORS['success'],
            'marginRight': '8px',
            'display': 'inline-block'
        }
        conn_text = 'Connected • Live data'
    else:
        dot_style = {
            'width': '8px',
            'height': '8px',
            'borderRadius': '50%',
            'backgroundColor': COLORS['danger'],
            'marginRight': '8px',
            'display': 'inline-block'
        }
        conn_text = 'Disconnected'
    
    # Alerts display
    if active_alerts:
        alert_items = []
        for alert in active_alerts:
            severity = alert['labels'].get('severity', 'info')
            color = COLORS['danger'] if severity == 'critical' else COLORS['warning']
            
            alert_items.append(
                html.Div([
                    html.Div([
                        html.Strong(alert['labels'].get('alertname', 'Alert'), style={
                            'fontSize': '16px',
                            'color': color,
                            'display': 'block',
                            'marginBottom': '4px'
                        }),
                        html.Span(alert['annotations'].get('description', ''), style={
                            'fontSize': '14px',
                            'color': COLORS['gray']
                        })
                    ])
                ], style={
                    'padding': '16px 24px',
                    'backgroundColor': COLORS['card_bg'],
                    'borderLeft': f'4px solid {color}',
                    'marginBottom': '12px',
                    'borderRadius': '8px',
                    'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'
                })
            )
        
        alerts_display = html.Div([
            html.H3('⚠️ Active Alerts', style={
                'fontSize': '18px',
                'fontWeight': '600',
                'color': COLORS['dark'],
                'marginBottom': '16px'
            }),
            html.Div(alert_items)
        ])
    else:
        alerts_display = html.Div()
    
    # Update history
    import time
    metrics_history['timestamps'].append(time.time())
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
            if prev and curr and prev != 0:
                change = ((curr - prev) / prev) * 100
                if abs(change) < 0.01:
                    return html.Span('—', style={'color': COLORS['gray']})
                arrow = '↑' if change > 0 else '↓'
                color = COLORS['success'] if change > 0 else COLORS['danger']
                return html.Span(f"{arrow} {abs(change):.1f}%", style={'color': color})
        return html.Span('—', style={'color': COLORS['gray']})
    
    # Format values
    acc_display = f"{accuracy:.4f}" if accuracy else "—"
    prec_display = f"{precision:.4f}" if precision else "—"
    rec_display = f"{recall:.4f}" if recall else "—"
    f1_display = f"{f1:.4f}" if f1 else "—"
    
    # Performance graph
    performance_fig = go.Figure()
    
    metrics_config = [
        ('accuracy', 'Accuracy', COLORS['primary']),
        ('precision', 'Precision', COLORS['purple']),
        ('recall', 'Recall', COLORS['danger']),
        ('f1_score', 'F1 Score', COLORS['warning'])
    ]
    
    for metric, name, color in metrics_config:
        performance_fig.add_trace(go.Scatter(
            y=list(metrics_history[metric]),
            mode='lines',
            name=name,
            line=dict(color=color, width=2.5),
            hovertemplate='%{y:.4f}<extra></extra>'
        ))
    
    performance_fig.update_layout(
        yaxis=dict(range=[0, 1], title='', showgrid=True, gridcolor='#F3F4F6'),
        xaxis=dict(title='', showgrid=False),
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='inherit', size=13, color=COLORS['gray']),
        margin=dict(l=60, r=20, t=20, b=40),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5
        ),
        height=400
    )
    
    # Predictions graph
    predictions_fig = go.Figure()
    predictions_fig.add_trace(go.Scatter(
        y=list(metrics_history['predictions']),
        mode='lines',
        name='Predictions',
        line=dict(color=COLORS['success'], width=2.5),
        fill='tozeroy',
        fillcolor='rgba(16, 185, 129, 0.1)'
    ))
    predictions_fig.add_trace(go.Scatter(
        y=list(metrics_history['errors']),
        mode='lines',
        name='Errors',
        line=dict(color=COLORS['danger'], width=2.5)
    ))
    
    predictions_fig.update_layout(
        yaxis=dict(title='', showgrid=True, gridcolor='#F3F4F6'),
        xaxis=dict(title='', showgrid=False),
        hovermode='x',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='inherit', size=12, color=COLORS['gray']),
        margin=dict(l=50, r=20, t=10, b=40),
        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
        height=300
    )
    
    # Resources graph
    resources_fig = go.Figure()
    resources_fig.add_trace(go.Scatter(
        y=list(metrics_history['cpu']),
        mode='lines',
        name='CPU %',
        line=dict(color=COLORS['warning'], width=2.5)
    ))
    resources_fig.add_trace(go.Scatter(
        y=list(metrics_history['memory']),
        mode='lines',
        name='Memory (MB)',
        line=dict(color=COLORS['success'], width=2.5),
        yaxis='y2'
    ))
    
    resources_fig.update_layout(
        yaxis=dict(title='CPU %', showgrid=True, gridcolor='#F3F4F6'),
        yaxis2=dict(title='Memory MB', overlaying='y', side='right', showgrid=False),
        xaxis=dict(title='', showgrid=False),
        hovermode='x',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='inherit', size=12, color=COLORS['gray']),
        margin=dict(l=50, r=60, t=10, b=40),
        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
        height=300
    )
    
    return (acc_display, prec_display, rec_display, f1_display,
            get_change('accuracy'), get_change('precision'), 
            get_change('recall'), get_change('f1_score'),
            dot_style, conn_text, alerts_display,
            performance_fig, predictions_fig, resources_fig)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"Starting dashboard server on port {port}...")
    app.run_server(host='0.0.0.0', port=port, debug=False)
