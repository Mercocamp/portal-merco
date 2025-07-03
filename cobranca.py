# cobranca.py

from dash import dcc, html

layout = html.Div([
    html.H1("Análise de Cobrança e Recuperação", style={'textAlign': 'center', 'color': '#007bff'}),
    
    # Container principal que será preenchido pelo callback
    html.Div(id='cobranca-container'),

    # Novo container para o gráfico de recebimentos diários
    html.Div(id='cobranca-recebimentos-diarios-container', style={'marginTop': '40px'}),

    # Novo container para as tabelas de ranking
    html.Div(id='cobranca-rankings-container', style={'marginTop': '40px'}),

    html.Br(),
    # Botão de voltar
    html.Div(
        dcc.Link(
            "← Voltar ao Menu", 
            href="/menu",
            style={
                'display': 'inline-block',
                'padding': '10px 15px',
                'backgroundColor': '#6c757d',
                'color': 'white',
                'borderRadius': '8px',
                'textDecoration': 'none',
                'fontWeight': 'bold',
                'boxShadow': '0px 2px 4px rgba(0,0,0,0.1)'
            }
        ),
        style={'textAlign': 'center', 'marginTop': '40px'}
    )
], style={'padding': '30px 50px'})
