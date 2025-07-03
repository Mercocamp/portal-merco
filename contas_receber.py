# contas_receber.py

from dash import dcc, html
from datetime import date, timedelta

# Define o período inicial (mês atual)
hoje = date.today()
data_inicio = hoje.replace(day=1)
data_fim = (data_inicio + timedelta(days=31)).replace(day=1) - timedelta(days=1)

layout = html.Div([
    html.H1("Análise de Contas a Receber", style={'textAlign': 'center', 'color': '#007bff'}),

    # Seletor de data
    html.Div([
        html.H4("Selecione o Período de Análise:", style={'marginRight': '20px'}),
        dcc.DatePickerRange(
            id='filtro-data-recebimento',
            min_date_allowed=date(2024, 1, 1),
            max_date_allowed=date(2030, 12, 31),
            initial_visible_month=hoje,
            start_date=data_inicio,
            end_date=data_fim,
            display_format='DD/MM/YYYY'
        ),
    ], style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'marginBottom': '30px'}),

    # Container para os KPIs e gráficos de recebimentos
    html.Div(id='recebimentos-container', style={'marginBottom': '40px'}),

    # Container para a projeção de recebíveis
    html.Div(id='projecao-recebiveis-container', style={'marginTop': '40px'}),

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
        style={'textAlign': 'center', 'marginTop': '20px'}
    )
], style={'padding': '30px 50px'})
