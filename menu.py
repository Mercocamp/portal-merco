# menu.py (REESTRUTURADO COM LINKS)

from dash import dcc, html

# Lista de itens do menu. O 'href' é a URL para a qual cada link irá apontar.
menu_items = [
    {"href": "/faturamento", "icon": "📊", "label": "Faturamento"},
    {"href": "/contas_receber", "icon": "💰", "label": "Contas a Receber"},
    {"href": "/cobranca", "icon": "📞", "label": "Cobrança"},
    {"href": "/comercial", "icon": "📈", "label": "Comercial"},
    {"href": "/evolucao", "icon": "🚀", "label": "Evolução"},
    {"href": "/operacao", "icon": "⚙️", "label": "Operação"},
]

# Cria a lista de componentes de link a partir da lista acima.
# Usamos dcc.Link em vez de html.Button.
links = [
    dcc.Link(
        href=item["href"],
        className='menu-button', # Usamos a mesma classe para manter o estilo
        children=[
            html.Span(item["icon"], className='menu-icon'),
            html.Span(item["label"], className='menu-text')
        ]
    ) for item in menu_items
]

# Layout final da página de menu
layout = html.Div(className='menu-page-container', children=[
    html.Div(className='menu-header', children=[
        html.H1("PORTAL MERCOCAMP", className='menu-title'),
        html.P("Bem-vindo!", className='greeting-text')
    ]),
    
    html.Div(className='menu-grid', children=links)
])
