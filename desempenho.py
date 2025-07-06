# desempenho.py (Layout com Spinner de Carregamento)

from dash import html, dcc

layout = html.Div([
    # Cabeçalho da página
    html.Div([
        html.H1("Desempenho do Cliente", style={'color': 'white'}),
        dcc.Link("⬅️ Voltar ao Menu", href="/menu", className="menu-button")
    ], className="header-dash"),

    # Área de conteúdo principal
    html.Div([
        
        # Seção de Filtros/Busca
        html.Div([
            html.H3("Buscar Cliente"),
            dcc.Dropdown(
                id='dropdown-busca-cliente-desempenho',
                placeholder="Digite ou selecione um cliente...",
            ),
            html.Button('Buscar', id='botao-buscar-cliente-desempenho', n_clicks=0, className="menu-button", style={'marginTop': '10px'})
        ], className="card-filtro", style={'marginBottom': '20px'}),

        # SPINNER LOCAL PARA PROTEGER CONTRA TIMEOUT
        # Esta área mostrará um spinner enquanto o callback de busca estiver rodando
        dcc.Loading(
            id="loading-desempenho-resultados",
            type="circle", # Um spinner diferente para diferenciar do global
            children=html.Div(id='container-resultados-desempenho')
        )

    ], style={'padding': '20px'})
])
