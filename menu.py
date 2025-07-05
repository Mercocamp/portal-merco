# menu.py (COM BOTÃO DE ATUALIZAR)

from dash import dcc, html

menu_items = [
    {"href": "/faturamento", "icon": "📊", "label": "Faturamento"},
    {"href": "/contas_receber", "icon": "💰", "label": "Contas a Receber"},
    {"href": "/cobranca", "icon": "📞", "label": "Cobrança"},
    {"href": "/comercial", "icon": "📈", "label": "Comercial"},
    {"href": "/evolucao", "icon": "🚀", "label": "Evolução"},
    {"href": "/operacao", "icon": "⚙️", "label": "Operação"},
]

links = [
    dcc.Link(
        href=item["href"],
        className='menu-button',
        children=[
            html.Span(item["icon"], className='menu-icon'),
            html.Span(item["label"], className='menu-text')
        ]
    ) for item in menu_items
]

layout = html.Div(className='menu-page-container', children=[
    html.Div(className='menu-header', children=[
        html.H1("PORTAL MERCOCAMP", className='menu-title'),
        html.P(id='greeting-message', className='greeting-text') # Adicionado ID para o JS
    ]),
    
    html.Div(className='menu-grid', children=links),

    # Botão de Atualização
    html.Div([
        html.Button("🔄 Atualizar Dados Agora", id="btn-refresh-cache", n_clicks=0, 
            style={'backgroundColor': '#6c757d', 'marginTop': '40px'}),
        html.P(id='refresh-status', style={'fontSize': '12px', 'color': 'gray', 'marginTop': '10px'})
    ], style={'textAlign': 'center'})
])
