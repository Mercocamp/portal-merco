# desempenho.py (Layout com Carregamento Assíncrono)

from dash import html, dcc

# Este é o layout estático da página. Ele carrega instantaneamente.
# O conteúdo de 'desempenho-content-wrapper' será preenchido por um callback em app.py
# depois que o carregamento pesado dos dados for concluído.
layout = html.Div([
    # Cabeçalho da página
    html.Div([
        html.H1("Desempenho do Cliente", style={'color': 'white'}),
        dcc.Link("⬅️ Voltar ao Menu", href="/menu", className="menu-button")
    ], className="header-dash"),

    # Área de conteúdo principal
    html.Div([
        # Este Loading component mostra um spinner enquanto o conteúdo principal
        # (dropdown, botão, etc.) está sendo gerado pelo callback em app.py.
        dcc.Loading(
            id="loading-desempenho-main",
            type="circle",
            children=html.Div(id="desempenho-content-wrapper")
        )
    ], style={'padding': '20px'})
])
