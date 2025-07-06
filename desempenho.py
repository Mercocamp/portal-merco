# desempenho.py

from dash import dcc, html

layout = html.Div([
    html.Div([
        dcc.Link("⬅️ Voltar ao Menu", href="/menu", className="cd-link-button"),
        html.H2("Página de Desempenho", style={'textAlign': 'center', 'marginTop': '20px'}),
        html.P("Esta página está em construção.", style={'textAlign': 'center'}),
    ], style={'maxWidth': '800px', 'margin': 'auto', 'padding': '20px'})
])
