import os
import requests
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
from collections import deque
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PROM_URL = os.environ.get("PROM_URL", "http://localhost:9090")
logger.info(f"Connecting to Prometheus at: {PROM_URL}")

app = dash.Dash(__name__)
app.title = "ML Model Monitoring"

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

COLORS = {
    'primary': '#3B82F6',
    'success': '#10B981', 
    'warning': '#F59E0B',
    'danger': '#EF4444',
    'purple': '#8B5CF6',
    'dark': '#111827',
    'gray': '#6B7280',
    'light_gray': '#9CA3AF',
    'card_bg': '#FFFFFF'
}

app.layout = html.Div([
    html.Div([
        html.Div([
            html.Div([
                html.Span('🤖', style={'fontSize': '56px', 'marginRight': '20px'}),
                html.Div([
                    html.H1('Real-Time Model Monitoring', style={
                        'margin': 0,
                        'color': 'white',
                        'fontSize': '42px',
                        'fontWeight': '800',
                        'letterSpacing': '-1px',
                        'textShadow': '0 2px 4px rgba(0,0,0,0.1)'
                    }),
                    html.P('Live performance metrics and analytics', style={
                        'margin': '8px 0 0 0',
                        'color': 'rgba(255,255,255,0.9)',
                        'fontSize': '18px',
                        'fontWeight': '400'
                    })
                ])
            ], style={'display': 'flex', 'alignItems': 'center'}),
            
            html.Div([
                html.Div([
                    html.Span(id='connection-status-dot', style={
                        'width': '12px',
                        'height': '12px',
                        'borderRadius': '50%',
                        'backgroundColor': '#10B981',
                        'marginRight': '10px',
                        'display': 'inline-block',
                        'boxShadow': '0 0 10px rgba(16, 185, 129, 0.5)'
                    }),
                    html.Span(id='connection-text', style={
                        'color': 'white',
                        'fontSize': '16px',
                        'fontWeight': '500'
                    })
                ], style={'display': 'flex', 'alignItems': 'center'}),
                html.Div(id='last-update-time', style={
                    'color': 'rgba(255,255,255,0.8)',
                    'fontSize': '14px',
                    'marginTop': '6px'
                })
            ], style={'textAlign': 'right'})
        ], style={
            'display': 'flex',
            'justifyContent': 'space-between',
            'alignItems': 'center',
            'padding': '0 60px'
        })
    ], style={
        'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'padding': '50px 0',
        'marginBottom': '40px',
        'boxShadow': '0 4px 20px rgba(0,0,0,0.1)'
    }),
    
    html.Div([
        html.Div(id='alerts-section', style={'marginBottom': '30px'}),
        
        html.Div([
            html.Div([
                html.Div('📊', style={'fontSize': '48px', 'marginBottom': '16px'}),
                html.Div('ACCURACY', style={
                    'fontSize': '12px',
                    'fontWeight': '700',
                    'color': COLORS['gray'],
                    'letterSpacing': '1.5px',
                    'marginBottom': '12px'
                }),
                html.Div(id='accuracy-value', style={
                    'fontSize': '52px',
                    'fontWeight': '800',
                    'color': COLORS['primary'],
                    'lineHeight': '1',
                    'marginBottom': '8px'
                }),
                html.Div(id='accuracy-change', style={
                    'fontSize': '15px',
                    'fontWeight': '600'
                })
            ], style={
                'backgroundColor': COLORS['card_bg'],
                'padding': '40px',
                'borderRadius': '20px',
                'textAlign': 'center',
                'boxShadow': '0 10px 30px rgba(0,0,0,0.08)',
                'border': '1px solid rgba(0,0,0,0.05)',
                'transition': 'transform 0.3s ease, box-shadow 0.3s ease',
                'cursor': 'pointer'
            }, className='metric-card'),
            
            html.Div([
                html.Div('🎯', style={'fontSize': '48px', 'marginBottom': '16px'}),
                html.Div('PRECISION', style={
                    'fontSize': '12px',
                    'fontWeight': '700',
                    'color': COLORS['gray'],
                    'letterSpacing': '1.5px',
                    'marginBottom': '12px'
                }),
                html.Div(id='precision-value', style={
                    'fontSize': '52px',
                    'fontWeight': '800',
                    'color': COLORS['purple'],
                    'lineHeight': '1',
                    'marginBottom': '8px'
                }),
                html.Div(id='precision-change', style={
                    'fontSize': '15px',
                    'fontWeight': '600'
                })
            ], style={
                'backgroundColor': COLORS['card_bg'],
                'padding': '40px',
                'borderRadius': '20px',
                'textAlign': 'center',
                'boxShadow': '0 10px 30px rgba(0,0,0,0.08)',
                'border': '1px solid rgba(0,0,0,0.05)',
                'transition': 'transform 0.3s ease, box-shadow 0.3s ease',
                'cursor': 'pointer'
            }, className='metric-card'),
            
            html.Div([
                html.Div('🔍', style={'fontSize': '48px', 'marginBottom': '16px'}),
                html.Div('RECALL', style={
                    'fontSize': '12px',
                    'fontWeight': '700',
                    'color': COLORS['gray'],
                    'letterSpacing': '1.5px',
                    'marginBottom': '12px'
                }),
                html.Div(id='recall-value', style={
                    'fontSize': '52px',
                    'fontWeight': '800',
                    'color': COLORS['danger'],
                    'lineHeight': '1',
                    'marginBottom': '8px'
                }),
                html.Div(id='recall-change', style={
                    'fontSize': '15px',
                    'fontWeight': '600'
                })
            ], style={
                'backgroundColor': COLORS['card_bg'],
                'padding': '40px',
                'borderRadius': '20px',
                'textAlign': 'center',
                'boxShadow': '0 10px 30px rgba(0,0,0,0.08)',
                'border': '1px solid rgba(0,0,0,0.05)',
                'transition': 'transform 0.3s ease, box-shadow 0.3s ease',
                'cursor': 'pointer'
            }, className='metric-card'),
            
            html.Div([
                html.Div('⚡', style={'fontSize': '48px', 'marginBottom': '16px'}),
                html.Div('F1 SCORE', style={
                    'fontSize': '12px',
                    'fontWeight': '700',
                    'color': COLORS['gray'],
                    'letterSpacing': '1.5px',
                    'marginBottom': '12px'
                }),
                html.Div(id='f1-value', style={
                    'fontSize': '52px',
                    'fontWeight': '800',
                    'color': COLORS['warning'],
                    'lineHeight': '1',
                    'marginBottom': '8px'
                }),
                html.Div(id='f1-change', style={
                    'fontSize': '15px',
                    'fontWeight': '600'
                })
            ], style={
                'backgroundColor': COLORS['card_bg'],
                'padding': '40px',
                'borderRadius': '20px',
                'textAlign': 'center',
                'boxShadow': '0 10px 30px rgba(0,0,0,0.08)',
                'border': '1px solid rgba(0,0,0,0.05)',
                'transition': 'transform 0.3s ease, box-shadow 0.3s ease',
                'cursor': 'pointer'
            }, className='metric-card'),
        ], style={
            'display': 'grid',
            'gridTemplateColumns': 'repeat(4, 1fr)',
            'gap': '30px',
            'marginBottom': '40px'
        }),
        
        html.Div([
            html.Div([
                html.Div([
                    html.H2('📈 Performance Trends', style={
                        'fontSize': '24px',
                        'fontWeight': '700',
                        'color': COLORS['dark'],
                        'margin': 0
                    }),
                    html.P('Real-time model performance metrics', style={
                        'fontSize': '14px',
                        'color': COLORS['light_gray'],
                        'margin': '4px 0 0 0'
                    })
                ]),
                dcc.Graph(
                    id='performance-graph',
                    config={'displayModeBar': False},
                    style={'height': '450px', 'marginTop': '20px'}
                )
            ], style={
                'backgroundColor': COLORS['card_bg'],
                'padding': '35px',
                'borderRadius': '20px',
                'boxShadow': '0 10px 30px rgba(0,0,0,0.08)',
                'border': '1px solid rgba(0,0,0,0.05)'
            })
        ], style={'marginBottom': '30px'}),
        
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.H2('📊 Prediction Analytics', style={
                            'fontSize': '20px',
                            'fontWeight': '700',
                            'color': COLORS['dark'],
                            'margin': 0
                        }),
                        html.P('Total predictions and error rates', style={
                            'fontSize': '13px',
                            'color': COLORS['light_gray'],
                            'margin': '4px 0 0 0'
                        })
                    ]),
                    dcc.Graph(
                        id='predictions-graph',
                        config={'displayModeBar': False},
                        style={'height': '320px', 'marginTop': '20px'}
                    )
                ], style={
                    'backgroundColor': COLORS['card_bg'],
                    'padding': '30px',
                    'borderRadius': '20px',
                    'boxShadow': '0 10px 30px rgba(0,0,0,0.08)',
                    'border': '1px solid rgba(0,0,0,0.05)',
                    'height': '100%'
                })
            ], style={'flex': '1'}),
            
            html.Div([
                html.Div([
                    html.Div([
                        html.H2('💻 System Resources', style={
                            'fontSize': '20px',
                            'fontWeight': '700',
                            'color': COLORS['dark'],
                            'margin': 0
                        }),
                        html.P('CPU and memory utilization', style={
                            'fontSize': '13px',
                            'color': COLORS['light_gray'],
                            'margin': '4px 0 0 0'
                        })
                    ]),
                    dcc.Graph(
                        id='resources-graph',
                        config={'displayModeBar': False},
                        style={'height': '320px', 'marginTop': '20px'}
                    )
                ], style={
                    'backgroundColor': COLORS['card_bg'],
                    'padding': '30px',
                    'borderRadius': '20px',
                    'boxShadow': '0 10px 30px rgba(0,0,0,0.08)',
                    'border': '1px solid rgba(0,0,0,0.05)',
                    'height': '100%'
                })
            ], style={'flex': '1'})
        ], style={
            'display': 'flex',
            'gap': '30px',
            'marginBottom': '50px'
        }),
        
        dcc.Interval(id='interval-component', interval=2000, n_intervals=0)
        
    ], style={
        'padding': '0 60px 60px 60px'
    })
], style={
    'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    'background': 'linear-gradient(to bottom, #f8f9fa 0%, #e9ecef 100%)',
    'minHeight': '100vh'
})

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
                transform: translateY(-8px);
                box-shadow: 0 20px 40px rgba(0,0,0,0.15) !important;
            }
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
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
     Output('last-update-time', 'children'),
     Output('alerts-section', 'children'),
     Output('performance-graph', 'figure'),
     Output('predictions-graph', 'figure'),
     Output('resources-graph', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    accuracy = query_prometheus('model_accuracy')
    precision = query_prometheus('model_precision')
    recall = query_prometheus('model_recall')
    f1 = query_prometheus('model_f1_score')
    predictions = query_prometheus('total_predictions')
    errors = query_prometheus('total_errors')
    cpu = query_prometheus('cpu_usage_percent')
    memory = query_prometheus('memory_usage_mb')
    
    active_alerts = get_active_alerts()
    
    if accuracy is not None:
        dot_style = {
            'width': '12px',
            'height': '12px',
            'borderRadius': '50%',
            'backgroundColor': '#10B981',
            'marginRight': '10px',
            'display': 'inline-block',
            'boxShadow': '0 0 10px rgba(16, 185, 129, 0.5)',
            'animation': 'pulse 2s infinite'
        }
        conn_text = 'Connected • Live'
    else:
        dot_style = {
            'width': '12px',
            'height': '12px',
            'borderRadius': '50%',
            'backgroundColor': '#EF4444',
            'marginRight': '10px',
            'display': 'inline-block',
            'boxShadow': '0 0 10px rgba(239, 68, 68, 0.5)'
        }
        conn_text = 'Disconnected'
    
    from datetime import datetime
    update_time = f"Updated {datetime.now().strftime('%I:%M:%S %p')}"
    
    if active_alerts:
        alert_items = []
        for alert in active_alerts:
            severity = alert['labels'].get('severity', 'info')
            color = COLORS['danger'] if severity == 'critical' else COLORS['warning']
            
            alert_items.append(
                html.Div([
                    html.Div([
                        html.Div('⚠️', style={'fontSize': '24px', 'marginRight': '16px'}),
                        html.Div([
                            html.Strong(alert['labels'].get('alertname', 'Alert'), style={
                                'fontSize': '18px',
                                'color': COLORS['dark'],
                                'display': 'block',
                                'marginBottom': '6px'
                            }),
                            html.Span(alert['annotations'].get('description', ''), style={
                                'fontSize': '14px',
                                'color': COLORS['gray']
                            })
                        ], style={'flex': 1})
                    ], style={'display': 'flex', 'alignItems': 'flex-start'})
                ], style={
                    'padding': '20px 24px',
                    'backgroundColor': COLORS['card_bg'],
                    'borderLeft': f'5px solid {color}',
                    'marginBottom': '12px',
                    'borderRadius': '12px',
                    'boxShadow': '0 4px 12px rgba(0,0,0,0.08)'
                })
            )
        
        alerts_display = html.Div([
            html.H3('Active Alerts', style={
                'fontSize': '20px',
                'fontWeight': '700',
                'color': COLORS['dark'],
                'marginBottom': '16px'
            }),
            html.Div(alert_items)
        ])
    else:
        alerts_display = html.Div()
    
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
    
    def get_change(history_key):
        if len(metrics_history[history_key]) >= 2:
            prev = metrics_history[history_key][-2]
            curr = metrics_history[history_key][-1]
            if prev and curr and prev != 0:
                change = ((curr - prev) / prev) * 100
                if abs(change) < 0.01:
                    return html.Span('—', style={'color': COLORS['light_gray']})
                arrow = '↑' if change > 0 else '↓'
                color = COLORS['success'] if change > 0 else COLORS['danger']
                return html.Span(f"{arrow} {abs(change):.1f}%", style={'color': color})
        return html.Span('—', style={'color': COLORS['light_gray']})
    
    acc_display = f"{accuracy:.4f}" if accuracy else "—"
    prec_display = f"{precision:.4f}" if precision else "—"
    rec_display = f"{recall:.4f}" if recall else "—"
    f1_display = f"{f1:.4f}" if f1 else "—"
    
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
            line=dict(color=color, width=3),
            hovertemplate='%{y:.4f}<extra></extra>'
        ))
    
    performance_fig.update_layout(
        yaxis=dict(range=[0, 1], title='Score', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
        xaxis=dict(title='', showgrid=False),
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='inherit', size=13, color=COLORS['gray']),
        margin=dict(l=60, r=30, t=20, b=50),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(size=13)
        ),
        height=450
    )
    
    predictions_fig = go.Figure()
    predictions_fig.add_trace(go.Scatter(
        y=list(metrics_history['predictions']),
        mode='lines',
        name='Predictions',
        line=dict(color=COLORS['success'], width=3),
        fill='tozeroy',
        fillcolor='rgba(16, 185, 129, 0.1)'
    ))
    predictions_fig.add_trace(go.Scatter(
        y=list(metrics_history['errors']),
        mode='lines',
        name='Errors',
        line=dict(color=COLORS['danger'], width=3)
    ))
    
    predictions_fig.update_layout(
        yaxis=dict(title='', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
        xaxis=dict(title='', showgrid=False),
        hovermode='x',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='inherit', size=12, color=COLORS['gray']),
        margin=dict(l=50, r=20, t=10, b=50),
        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
        height=320
    )
    
    resources_fig = go.Figure()
    resources_fig.add_trace(go.Scatter(
        y=list(metrics_history['cpu']),
        mode='lines',
        name='CPU %',
        line=dict(color=COLORS['warning'], width=3)
    ))
    resources_fig.add_trace(go.Scatter(
        y=list(metrics_history['memory']),
        mode='lines',
        name='Memory (MB)',
        line=dict(color=COLORS['success'], width=3),
        yaxis='y2'
    ))
    
    resources_fig.update_layout(
        yaxis=dict(title='CPU %', showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
        yaxis2=dict(title='Memory MB', overlaying='y', side='right', showgrid=False),
        xaxis=dict(title='', showgrid=False),
        hovermode='x',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='inherit', size=12, color=COLORS['gray']),
        margin=dict(l=50, r=70, t=10, b=50),
        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
        height=320
    )
    
    return (acc_display, prec_display, rec_display, f1_display,
            get_change('accuracy'), get_change('precision'), 
            get_change('recall'), get_change('f1_score'),
            dot_style, conn_text, update_time, alerts_display,
            performance_fig, predictions_fig, resources_fig)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"Starting dashboard server on port {port}...")
    app.run_server(host='0.0.0.0', port=port, debug=False)
