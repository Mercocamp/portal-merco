# faturamento.py (Com atalho para a tela de Desempenho)

from dash import dcc, html

layout = html.Div([
    # Linha 1: Título, Novo Botão de Atalho e Dropdown
    html.Div([
        html.H1(id='titulo-pagina-faturamento', style={'textAlign': 'left', 'color': '#007bff', 'flex': '1', 'margin': '0'}),
        
        # NOVO BOTÃO DE ATALHO
        dcc.Link(
            "Análise de Cliente 🔍",
            href="/desempenho",
            style={
                'padding': '8px 15px',
                'backgroundColor': '#17a2b8', # Uma cor diferente para destacar
                'color': 'white',
                'borderRadius': '8px',
                'textDecoration': 'none',
                'fontWeight': 'bold',
                'whiteSpace': 'nowrap', # Evita que o texto quebre
                'marginLeft': '20px'
            }
        ),
        
        dcc.Dropdown(
            id='dropdown-competencia',
            options=[],
            placeholder="Selecione a competência",
            className='dropdown-competencia',
            style={'width': '250px', 'marginLeft': '20px'} # Estilo para o dropdown
        )
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'marginBottom': '20px'}),

    # Container para os KPIs principais (Gauge e Comparativo de Valor)
    html.Div(id='kpi-container', style={
        'display': 'flex',
        'gap': '20px',
        'justifyContent': 'center',
        'alignItems': 'center',
        'flexWrap': 'wrap',
        'marginBottom': '30px'
    }),

    # Cards
    html.Div(id='cards-faturamento', style={
        'display': 'flex', 'gap': '20px', 'justifyContent': 'center', 'marginBottom': '30px', 'flexWrap': 'wrap'
    }),

    # Container para a lista de faturas individuais
    html.Div(id='clientes-faturados-container', style={'marginTop': '30px'}),

    # Container para o ranking de clientes
    html.Div(id='ranking-container', style={'marginTop': '40px'}),

    # Container para os gráficos avançados
    html.Div(id='analise-avancada-container', style={'marginTop': '40px'}),

    # Container para o gráfico de faturamento diário.
    html.Div(id='faturamento-diario-container', style={'marginTop': '40px'}),

    # Container para o gráfico de evolução anual
    html.Div(id='evolucao-anual-container', style={'marginTop': '40px'}),

    html.Br(),

    # Botão de voltar
    html.Div(
        dcc.Link(
            "← Voltar", 
            id='botao-voltar',
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
        style={'textAlign': 'center', 'marginTop': '20px'}
    )
], style={'padding': '30px 50px'})
