# desempenho.py (CORRIGIDO com a função create_layout)

from dash import html, dcc

def create_layout(client_options):
    """
    Cria dinamicamente o layout da página de desempenho,
    recebendo a lista de clientes para popular o dropdown.
    """
    return html.Div([
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
                    options=[{'label': client, 'value': client} for client in client_options],
                    placeholder="Digite ou selecione um cliente...",
                ),
                html.Button('Buscar', id='botao-buscar-cliente-desempenho', n_clicks=0, className="menu-button", style={'marginTop': '10px'})
            ], className="card-filtro", style={'marginBottom': '20px'}),

            # SPINNER LOCAL PARA PROTEGER CONTRA TIMEOUT
            dcc.Loading(
                id="loading-desempenho-resultados",
                type="circle",
                children=html.Div(id='container-resultados-desempenho')
            )

        ], style={'padding': '20px'})
    ])
