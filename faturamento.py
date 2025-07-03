# faturamento.py (VERSÃO COM ESTILO DE KPI AJUSTADO)

from dash import dcc, html

layout = html.Div([
    # Linha 1: Título dinâmico e Dropdown
    html.Div([
        html.H1(id='titulo-pagina-faturamento', style={'textAlign': 'left', 'color': '#007bff', 'flex': '1'}),
        dcc.Dropdown(
            id='dropdown-competencia',
            options=[],
            placeholder="Selecione a competência",
            className='dropdown-competencia'
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
