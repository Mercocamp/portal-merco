# app.py (VERSÃO FINAL COM CACHE INTELIGENTE E BOTÃO DE ATUALIZAÇÃO)

import dash
from dash import Dash, dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate
import time
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import plotly.graph_objects as go
from functools import lru_cache

# Importe os layouts e a função de carregar dados
import login
import menu 
import operacao
from faturamento import layout as layout_faturamento
from contas_receber import layout as layout_contas_receber
from cobranca import layout as layout_cobranca
from sheets_api import carregar_dados

app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server
app.title = "Portal MercoCamp"

# --- LAYOUT PRINCIPAL ---
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='competencia-store'),
    dcc.Loading(
        id="global-spinner",
        type="default",
        color="#007bff",
        fullscreen=True,
        children=html.Div(id='pagina-container')
    )
])

# --- CALLBACKS ---

# Callback de Roteamento
@app.callback(Output('pagina-container', 'children'), Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/menu': return menu.layout
    if pathname == '/faturamento': return layout_faturamento
    if pathname == '/operacao': return operacao.layout
    if pathname and pathname.startswith('/operacao/'): return layout_faturamento
    if pathname == '/contas_receber': return layout_contas_receber
    if pathname == '/cobranca': return layout_cobranca

    if pathname in ['/comercial', '/evolucao']:
        nome = pathname.strip('/').replace('_', ' ').title()
        return html.Div([
            html.H2(f"Página '{nome}' em construção..."),
            html.Br(),
            dcc.Link("⬅️ Voltar ao Menu", href="/menu", className="menu-button")
        ], style={'textAlign': 'center', 'padding': '50px'})
    if pathname == '/login' or pathname == '/': return login.layout
    return html.Div("Página não encontrada", style={'textAlign': 'center', 'padding': '50px'})

# Callback de Login
@app.callback(
    Output('url', 'pathname'), 
    Output('mensagem-erro', 'children'), 
    Input('botao-login', 'n_clicks'), 
    Input('senha', 'n_submit'), 
    State('usuario', 'value'), 
    State('senha', 'value'), 
    prevent_initial_call=True
)
def fazer_login(n_clicks_btn, n_submit_senha, usuario, senha):
    if not n_clicks_btn and not n_submit_senha: raise PreventUpdate
    if usuario == 'admin' and senha == '123':
        time.sleep(1)
        return '/menu', ""
    return dash.no_update, html.P("Usuário ou Senha incorreta", style={'color': 'red'})

# --- FUNÇÃO AUXILIAR PARA PREPARAR O DATAFRAME COMPLETO ---
@lru_cache(maxsize=8)
def _preparar_dataframe_com_cache(cache_key: str):
    """
    Esta é a função que realmente faz o trabalho pesado e cujo resultado é cacheado.
    O 'cache_key' garante que ela só seja executada quando a hora mudar.
    """
    print(f"CACHE MISS: Gerando novos dados para a chave: {cache_key}")
    df = carregar_dados("BaseReceber2025", "BaseReceber")
    if 'Cliente' in df.columns and 'Clientes' not in df.columns:
        df.rename(columns={'Cliente': 'Clientes'}, inplace=True)
    
    text_cols = ['Clientes', 'Competencia', 'Tipo_Resumido', 'Lotacao']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            if col == 'Tipo_Resumido':
                df[col] = df[col].str.lower()
    
    numeric_cols = ['Vlr_Titulo', 'Vlr_Recebido']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    def parse_mixed_date(date_val):
        if pd.isna(date_val) or str(date_val).strip() == '':
            return pd.NaT
        try:
            return pd.to_datetime('1899-12-30') + pd.to_timedelta(int(float(date_val)), 'D')
        except (ValueError, TypeError):
            try:
                return pd.to_datetime(date_val, dayfirst=True, errors='coerce')
            except Exception:
                return pd.NaT

    date_cols = ['Vencimento', 'Data_Pagamento', 'Emissao']
    for col in date_cols:
        if col in df.columns:
            df[col] = df[col].apply(parse_mixed_date)

    if 'Vencimento' in df.columns and 'Data_Pagamento' in df.columns:
        df['DIAS_DE_ATRASO'] = 0
        pagas = df['Data_Pagamento'].notna() & df['Vencimento'].notna()
        df.loc[pagas, 'DIAS_DE_ATRASO'] = (df.loc[pagas, 'Data_Pagamento'] - df.loc[pagas, 'Vencimento']).dt.days
        hoje = pd.to_datetime("today").normalize()
        em_aberto_vencidas = df['Data_Pagamento'].isna() & (df['Vencimento'] < hoje)
        df.loc[em_aberto_vencidas, 'DIAS_DE_ATRASO'] = (hoje - df.loc[em_aberto_vencidas, 'Vencimento']).dt.days
    
    print("DADOS CARREGADOS E PROCESSADOS COM SUCESSO.")
    return df

def get_cache_key():
    """Cria uma chave de cache baseada na hora atual, arredondada para baixo a cada 3 horas."""
    hora_arredondada = (datetime.now().hour // 3) * 3
    return datetime.now().strftime(f'%Y-%m-%d-{hora_arredondada}')

def preparar_dataframe_completo():
    """Função principal que chama a versão em cache."""
    return _preparar_dataframe_com_cache(get_cache_key())

# --- FUNÇÃO AUXILIAR PARA FILTRAR DADOS ---
def filtrar_dados_por_contexto(df, pathname):
    if 'Lotacao' not in df.columns:
        return df, "Faturamento Geral", html.Div("Erro Crítico: A coluna 'Lotacao' não foi encontrada.", style={'color': 'red'})
    if pathname == '/faturamento':
        return df, "Faturamento Geral", None
    if pathname and pathname.startswith('/operacao/'):
        cd_bruto = pathname.split('/')[-1].replace('-', ' ').upper()
        titulo_pagina = f"Visão Operacional: {cd_bruto}"
        df_filtrado = df[df['Lotacao'].str.strip().str.upper() == cd_bruto].copy()
        return df_filtrado, titulo_pagina, None
    return df, "Faturamento Geral", None

# --- LÓGICA DE CALLBACKS DE COMPETÊNCIA PARA FATURAMENTO/OPERAÇÃO ---
@app.callback(
    Output('dropdown-competencia', 'options'),
    Output('dropdown-competencia', 'value'),
    Input('url', 'pathname')
)
def popular_e_definir_competencia_inicial(pathname):
    if not (pathname == "/faturamento" or pathname.startswith("/operacao/")):
        raise PreventUpdate
    df_full = preparar_dataframe_completo()
    df_contexto, _, _ = filtrar_dados_por_contexto(df_full, pathname)
    if 'Competencia' not in df_contexto.columns:
        return [], None
    competencias = df_contexto['Competencia'].dropna().unique()
    competencias_sorted = sorted(competencias, key=lambda x: (x.split('/')[1], x.split('/')[0]), reverse=True)
    options = [{'label': c, 'value': c} for c in competencias_sorted]
    initial_value = competencias_sorted[0] if competencias_sorted else None
    return options, initial_value

@app.callback(
    Output('competencia-store', 'data'),
    Input('dropdown-competencia', 'value')
)
def atualizar_store_competencia(selected_competence):
    if not selected_competence:
        raise PreventUpdate
    return selected_competence

# --- CALLBACKS DE CONTEÚDO PARA FATURAMENTO/OPERAÇÃO ---
@app.callback(
    [Output('kpi-container', 'children'),
     Output('cards-faturamento', 'children'),
     Output('titulo-pagina-faturamento', 'children'),
     Output('botao-voltar', 'href')],
    [Input('competencia-store', 'data'),
     Input('url', 'pathname')]
)
def gerar_kpis_e_cards(competencia, pathname):
    if not (pathname.startswith('/faturamento') or pathname.startswith('/operacao/')):
        raise PreventUpdate
    voltar_href = "/operacao" if pathname.startswith("/operacao/") else "/menu"
    if not competencia:
        titulo = "Visão Operacional" if pathname.startswith("/operacao/") else "Faturamento Geral"
        return html.Div("Carregando dados...", style={'textAlign': 'center'}), [], titulo, voltar_href
    df_full = preparar_dataframe_completo()
    df_contexto, titulo_pagina, erro_filtro = filtrar_dados_por_contexto(df_full.copy(), pathname)
    if erro_filtro: return erro_filtro, [], titulo_pagina, voltar_href
    try:
        current_date = datetime.strptime(f"01/{competencia}", "%d/%m/%Y")
        previous_date = current_date - relativedelta(months=1)
        previous_competencia_str = previous_date.strftime("%m/%Y")
    except ValueError:
        return html.Div("Formato de competência inválido."), [], titulo_pagina, voltar_href
    
    df_competencia_atual = df_contexto[df_contexto["Competencia"] == competencia]
    df_competencia_anterior = df_contexto[df_contexto["Competencia"] == previous_competencia_str]

    df_armazenagem_atual = df_competencia_atual[df_competencia_atual["Tipo_Resumido"] == "armazenagem"]
    df_armazenagem_anterior = df_competencia_anterior[df_competencia_anterior["Tipo_Resumido"] == "armazenagem"]
    
    clientes_atuais = df_armazenagem_atual['Clientes'].nunique()
    meta_clientes = df_armazenagem_anterior['Clientes'].nunique()

    gauge_fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=clientes_atuais,
        title={'text': f"<b>Clientes de Armazenagem</b><br><span style='font-size:0.8em;color:gray'>Meta: {meta_clientes}</span>"},
        delta={'reference': meta_clientes, 'increasing': {'color': "#28a745"}},
        gauge={
            'axis': {'range': [0, meta_clientes * 1.5]},
            'bar': {'color': "#007bff"},
            'steps': [
                {'range': [0, meta_clientes * 0.7], 'color': 'lightgray'},
                {'range': [meta_clientes * 0.7, meta_clientes * 0.9], 'color': 'gray'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': meta_clientes
            }
        }
    ))
    gauge_fig.update_layout(height=200, margin={'t': 40, 'b': 20, 'l': 30, 'r': 30})
    gauge_kpi = dcc.Graph(figure=gauge_fig, config={'displayModeBar': False}, style={'flex': '1.5'})
    
    total_current = df_competencia_atual["Vlr_Titulo"].sum()
    total_previous = df_competencia_anterior["Vlr_Titulo"].sum()
    kpi_faturamento = None
    if total_previous > 0:
        percentage_change = ((total_current - total_previous) / total_previous) * 100
        color = '#28a745' if percentage_change >= 0 else '#dc3545'
        arrow = '▲' if percentage_change >= 0 else '▼'
        kpi_faturamento = html.Div([
            html.H4(f"Faturamento vs. {previous_competencia_str}", style={'margin': '0', 'fontSize': '16px', 'color': '#6c757d', 'fontWeight': 'bold'}),
            html.P(f"{arrow} {abs(percentage_change):.1f}%", style={'color': color, 'fontSize': '28px', 'fontWeight': 'bold', 'margin': '0'})
        ], style={'textAlign': 'center', 'padding': '20px'})
    else:
        kpi_faturamento = html.Div(f"Sem dados de faturamento para {previous_competencia_str}.", style={'color': '#6c757d', 'fontSize': '14px', 'padding': '20px'})

    aluguel_current = df_competencia_atual[df_competencia_atual["Tipo_Resumido"] == "aluguel"]
    armazenagem_current = df_armazenagem_atual
    aluguel_previous_total = df_competencia_anterior[df_competencia_anterior["Tipo_Resumido"] == "aluguel"]["Vlr_Titulo"].sum()
    armazenagem_previous_total = df_armazenagem_anterior["Vlr_Titulo"].sum()
    
    def formatar(valor): return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    def card(titulo, qtd, valor_atual, valor_anterior=0, competencia_anterior=None, flex_size='1'):
        comparison_text = html.P(f"(sem dados em {competencia_anterior})", style={'fontSize': '12px', 'color': '#6c757d', 'marginTop': '8px'})
        if valor_anterior > 0:
            comparison_text = html.P(f"(vs. {formatar(valor_anterior)} em {competencia_anterior})", style={'fontSize': '12px', 'color': '#6c757d', 'marginTop': '8px'})
        return html.Div([html.P(titulo, style={'fontWeight': 'bold', 'color': '#007bff'}), html.H3(f"{qtd} faturas", style={'margin': '5px 0'}), html.H2(formatar(valor_atual), style={'color': '#333'}), comparison_text], style={'padding': '20px', 'borderRadius': '16px', 'backgroundColor': '#fff', 'boxShadow': '0 4px 10px rgba(0,0,0,0.1)', 'textAlign': 'center', 'minWidth': '220px', 'flex': flex_size})
    
    card_total = card("Total", len(df_competencia_atual), total_current, total_previous, previous_competencia_str, flex_size='1')
    total_e_gauge_group = html.Div([card_total, gauge_kpi], style={'display': 'flex', 'gap': '20px', 'flex': '2', 'alignItems': 'center'})
    cards_layout = [
        card("Aluguel", len(aluguel_current), aluguel_current["Vlr_Titulo"].sum(), aluguel_previous_total, previous_competencia_str),
        card("Armazenagem", len(armazenagem_current), armazenagem_current["Vlr_Titulo"].sum(), armazenagem_previous_total, previous_competencia_str),
        total_e_gauge_group
    ]
    return kpi_faturamento, cards_layout, titulo_pagina, voltar_href

@app.callback(Output('clientes-faturados-container', 'children'), [Input('competencia-store', 'data'), Input('url', 'pathname')])
def gerar_lista_faturas_tabela(competencia, pathname):
    if not (pathname.startswith('/faturamento') or pathname.startswith('/operacao/')): raise PreventUpdate
    if not competencia: raise PreventUpdate
    df_full = preparar_dataframe_completo()
    df_contexto, _, erro_filtro = filtrar_dados_por_contexto(df_full.copy(), pathname)
    if erro_filtro: return erro_filtro
    def calcular_score(df_cliente, data_referencia_hoje):
        historico = df_cliente[(df_cliente['Vencimento'] >= (data_referencia_hoje - relativedelta(months=6))) & (df_cliente['Vencimento'] < data_referencia_hoje)]
        if historico.empty: return 1000, "Novo"
        score = 1000
        for _, row in historico.iterrows():
            dias = row['DIAS_DE_ATRASO']
            if dias < -5: score += 10
            elif 1 <= dias <= 10: score -= 20
            elif 11 <= dias <= 30: score -= 50
            elif dias > 30: score -= 100
        if score >= 950: return score, "Excelente"
        if score >= 800: return score, "Bom"
        if score >= 600: return score, "Atenção"
        return score, "Crítico"
    def get_score_visual(score_tuple):
        score, categoria = score_tuple
        cor_score = {"Excelente": "#28a745", "Bom": "#198754", "Atenção": "#ffc107", "Crítico": "#dc3545"}.get(categoria, 'grey')
        return html.Span(f"{categoria} ({score})", style={'color': cor_score, 'fontWeight': 'bold'})

    df_competencia = df_contexto[df_contexto['Competencia'] == competencia].copy()
    if df_competencia.empty: return html.Div("Nenhuma fatura emitida nesta competência.", style={'textAlign': 'center', 'padding': '20px'})
    df_competencia = df_competencia.sort_values(by='Vlr_Titulo', ascending=False)
    scores = {nome: calcular_score(df_full[df_full['Clientes'] == nome], datetime.today()) for nome in df_competencia['Clientes'].unique()}
    df_competencia['Score'] = df_competencia['Clientes'].map(scores)
    header = html.Div([html.Div("Cliente", style={'flex': '3', 'fontWeight': 'bold'}), html.Div("Vencimento", style={'flex': '1.5', 'fontWeight': 'bold', 'textAlign': 'center'}), html.Div("Fatura", style={'flex': '1.5', 'fontWeight': 'bold', 'textAlign': 'right'}), html.Div("Score", style={'flex': '1.5', 'fontWeight': 'bold', 'textAlign': 'right'})], style={'display': 'flex', 'padding': '10px 15px', 'borderBottom': '2px solid #333', 'backgroundColor': '#f8f9fa'})
    rows = [html.Div([html.Div(row['Clientes'], style={'flex': '3'}), html.Div(row['Vencimento'].strftime('%d/%m/%Y') if pd.notna(row['Vencimento']) else '-', style={'flex': '1.5', 'textAlign': 'center'}), html.Div(f"R$ {row['Vlr_Titulo']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), style={'flex': '1.5', 'textAlign': 'right', 'color': '#007bff'}), html.Div(get_score_visual(row['Score']), style={'flex': '1.5', 'textAlign': 'right'})], style={'display': 'flex', 'padding': '15px', 'borderBottom': '1px solid #eee', 'alignItems': 'center'}) for _, row in df_competencia.iterrows()]
    return html.Div([html.H4("Faturas Emitidas", style={'marginBottom': '10px'}), html.Div([header, html.Div(children=rows, style={'maxHeight': '500px', 'overflowY': 'auto'})], style={'border': '1px solid #ddd', 'borderRadius': '8px', 'overflow': 'hidden'})])

@app.callback(Output('ranking-container', 'children'), [Input('competencia-store', 'data'), Input('url', 'pathname')])
def gerar_ranking_armazenagem(competencia, pathname):
    if not (pathname.startswith('/faturamento') or pathname.startswith('/operacao/')): raise PreventUpdate
    if not competencia: raise PreventUpdate
    df_full = preparar_dataframe_completo()
    df_contexto, _, erro_filtro = filtrar_dados_por_contexto(df_full.copy(), pathname)
    if erro_filtro: return erro_filtro
    df_armazenagem = df_contexto[(df_contexto['Competencia'] == competencia) & (df_contexto['Tipo_Resumido'] == 'armazenagem')]
    if df_armazenagem.empty: return html.H5("Nenhum faturamento de armazenagem nesta competência.", style={'textAlign': 'center', 'marginTop': '20px'})
    ranking = df_armazenagem.groupby('Clientes')['Vlr_Titulo'].sum().reset_index()
    ranking.rename(columns={'Vlr_Titulo': 'Total_Faturado'}, inplace=True)
    melhores = ranking.sort_values(by='Total_Faturado', ascending=False).head(10)
    piores_df = ranking.sort_values(by='Total_Faturado', ascending=True).head(10)
    piores = piores_df.sort_values(by='Total_Faturado', ascending=False)
    def criar_tabela_ranking(titulo, dados, cor_titulo):
        rows = []
        for i, (_, row) in enumerate(dados.reset_index(drop=True).iterrows()):
            rows.append(html.Tr([html.Td(f"{i+1}º", style={'fontWeight': 'bold', 'padding': '8px'}), html.Td(row['Clientes'], style={'padding': '8px'}), html.Td(f"R$ {row['Total_Faturado']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), style={'textAlign': 'right', 'padding': '8px', 'fontWeight': 'bold'})]))
        return html.Div([html.H5(titulo, style={'color': 'white', 'backgroundColor': cor_titulo, 'padding': '10px', 'borderRadius': '8px 8px 0 0', 'margin': '0', 'textAlign': 'center'}), html.Table([html.Thead(html.Tr([html.Th("#", style={'padding': '10px', 'width': '40px'}), html.Th("Cliente", style={'textAlign': 'left', 'padding': '10px'}), html.Th("Total Faturado", style={'textAlign': 'right', 'padding': '10px'})])), html.Tbody(rows)], style={'width': '100%', 'borderCollapse': 'collapse'})], style={'flex': '1', 'border': '1px solid #ddd', 'borderRadius': '8px', 'overflow': 'hidden'})
    tabela_melhores = criar_tabela_ranking("🏆 Top 10 Melhores Clientes", melhores, '#28a745')
    tabela_piores = criar_tabela_ranking("📉 Top 10 Piores Clientes", piores, '#dc3545')
    return html.Div([html.H3("Ranking de Clientes (Apenas Armazenagem)", style={'width': '100%', 'textAlign': 'center', 'marginBottom': '20px'}), html.Div([tabela_melhores, tabela_piores], style={'display': 'flex', 'gap': '30px', 'flexWrap': 'wrap'})])

@app.callback(Output('analise-avancada-container', 'children'), [Input('competencia-store', 'data'), Input('url', 'pathname')])
def gerar_analises_avancadas(competencia, pathname):
    if not (pathname.startswith('/faturamento') or pathname.startswith('/operacao/')): raise PreventUpdate
    if not competencia: raise PreventUpdate
    df_full = preparar_dataframe_completo()
    df_contexto, _, erro_filtro = filtrar_dados_por_contexto(df_full.copy(), pathname)
    if erro_filtro: return erro_filtro
    df_competencia = df_contexto[df_contexto['Competencia'] == competencia]
    if df_competencia.empty: return None
    concentracao_data = df_competencia.groupby('Clientes')['Vlr_Titulo'].sum().sort_values(ascending=False)
    top_n = 5
    chart_data_series = concentracao_data.head(top_n)
    if len(concentracao_data) > top_n:
        outros_sum = concentracao_data.iloc[top_n:].sum()
        chart_data_series['Outros'] = outros_sum
    fig_donut = go.Figure(go.Pie(labels=chart_data_series.index, values=chart_data_series.values, hole=.4, textinfo='percent+label', hovertemplate='<b>%{label}</b><br>Faturamento: R$ %{value:,.2f}<br>(%{percent})<extra></extra>'))
    fig_donut.update_layout(title_text="<b>Concentração de Receita</b>", showlegend=False, margin=dict(t=50, b=20, l=20, r=20), uniformtext_minsize=10, uniformtext_mode='hide')
    concentracao_graph = html.Div(dcc.Graph(figure=fig_donut, config={'displayModeBar': False}), style={'flex': '1', 'minWidth': '300px', 'border': '1px solid #ddd', 'borderRadius': '8px', 'padding': '10px'})
    lotacao_graph = None
    if pathname == '/faturamento':
        lotacao_data = df_competencia.groupby('Lotacao')['Vlr_Titulo'].sum().sort_values(ascending=True)
        fig_lotacao = go.Figure(go.Bar(x=lotacao_data.values, y=lotacao_data.index, orientation='h', text=lotacao_data.apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")), textposition='auto', marker_color='#0d6efd'))
        fig_lotacao.update_layout(title_text="<b>Faturamento por CD</b>", xaxis_title="Faturamento (R$)", yaxis_title=None, template="plotly_white", margin=dict(t=50, b=20, l=20, r=20))
        lotacao_graph = html.Div(dcc.Graph(figure=fig_lotacao, config={'displayModeBar': False}), style={'flex': '1', 'minWidth': '300px', 'border': '1px solid #ddd', 'borderRadius': '8px', 'padding': '10px'})
    return html.Div([html.H3("Análises da Competência", style={'width': '100%', 'textAlign': 'center', 'marginBottom': '20px'}), html.Div([concentracao_graph, lotacao_graph], style={'display': 'flex', 'gap': '30px', 'flexWrap': 'wrap', 'alignItems': 'stretch'})])

@app.callback(Output('faturamento-diario-container', 'children'), [Input('competencia-store', 'data'), Input('url', 'pathname')])
def gerar_grafico_faturamento_diario(competencia, pathname):
    if not (pathname.startswith('/faturamento') or pathname.startswith('/operacao/')): raise PreventUpdate
    if not competencia: raise PreventUpdate
    df_full = preparar_dataframe_completo()
    df_contexto, _, erro_filtro = filtrar_dados_por_contexto(df_full.copy(), pathname)
    if erro_filtro: return erro_filtro
    df_competencia = df_contexto[df_contexto['Competencia'] == competencia]
    if df_competencia.empty: return None
    daily_data = df_competencia.groupby(df_competencia['Emissao'].dt.date).agg(Faturamento_Dia=('Vlr_Titulo', 'sum'), Qtd_Faturas=('Vlr_Titulo', 'size')).reset_index()
    daily_data.rename(columns={'Emissao': 'Dia'}, inplace=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily_data['Dia'], y=daily_data['Faturamento_Dia'], mode='lines+markers', fill='tozeroy', line=dict(color='#0d6efd'), fillcolor='rgba(13, 110, 253, 0.2)', customdata=daily_data['Qtd_Faturas'], hovertemplate='<b>%{x|%d/%m/%Y}</b><br>Faturamento: R$ %{y:,.2f}<br>Qtd. Faturas: %{customdata}<extra></extra>'))
    fig.update_layout(title="<b>Evolução do Faturamento Diário na Competência</b>", template="plotly_white", xaxis_title="Dia da Emissão", yaxis_title="Faturamento (R$)", margin=dict(t=50, b=20, l=20, r=20))
    return html.Div(dcc.Graph(figure=fig, config={'displayModeBar': False}), style={'border': '1px solid #ddd', 'borderRadius': '8px', 'padding': '10px', 'marginTop': '20px'})

@app.callback(
    Output('evolucao-anual-container', 'children'),
    [Input('competencia-store', 'data'),
     Input('url', 'pathname')]
)
def gerar_grafico_evolucao_anual(competencia, pathname):
    if not (pathname.startswith('/faturamento') or pathname.startswith('/operacao/')):
        raise PreventUpdate
    if not competencia:
        raise PreventUpdate
    df_full = preparar_dataframe_completo()
    df_contexto, _, erro_filtro = filtrar_dados_por_contexto(df_full.copy(), pathname)
    if erro_filtro: return erro_filtro
    try:
        ano_selecionado = int(competencia.split('/')[1])
        mes_selecionado = int(competencia.split('/')[0])
    except (ValueError, IndexError):
        return html.Div("Formato de competência inválido para análise anual.")
    competencias_periodo = [f"{str(m).zfill(2)}/{ano_selecionado}" for m in range(1, mes_selecionado + 1)]
    df_periodo = df_contexto[df_contexto['Competencia'].isin(competencias_periodo)]
    if df_periodo.empty:
        return html.H5(f"Nenhum faturamento encontrado em {ano_selecionado} até {competencia} para esta visão.", style={'textAlign': 'center', 'marginTop': '20px'})
    top_10_clientes = df_periodo.groupby('Clientes')['Vlr_Titulo'].sum().nlargest(10).index
    df_top_10 = df_periodo[df_periodo['Clientes'].isin(top_10_clientes)].copy()
    df_top_10.loc[:, 'Mes'] = pd.to_datetime(df_top_10['Competencia'], format='%m/%Y').dt.to_period('M')
    df_mensal = df_top_10.groupby(['Mes', 'Clientes'])['Vlr_Titulo'].sum().unstack(fill_value=0)
    df_acumulado = df_mensal.cumsum()
    df_acumulado.index = df_acumulado.index.to_timestamp()
    fig = go.Figure()
    for cliente in df_acumulado.columns:
        fig.add_trace(go.Scatter(
            x=df_acumulado.index,
            y=df_acumulado[cliente],
            name=cliente,
            mode='lines+markers',
            hovertemplate=f'<b>{cliente}</b><br>Mês: %{{x|%b/%Y}}<br>Acumulado: R$ %{{y:,.2f}}<extra></extra>'
        ))
    fig.update_layout(
        title=f"<b>Evolução Acumulada (Top 10 Clientes de 01/{ano_selecionado} a {competencia})</b>",
        xaxis_title="Mês",
        yaxis_title="Faturamento Acumulado (R$)",
        template="plotly_white",
        legend_title="Clientes",
        margin=dict(t=50, b=20, l=20, r=20)
    )
    return html.Div(dcc.Graph(figure=fig), style={'border': '1px solid #ddd', 'borderRadius': '8px', 'padding': '10px', 'marginTop': '20px'})

# --- NOVOS CALLBACKS PARA A PÁGINA DE CONTAS A RECEBER ---
@app.callback(
    Output('recebimentos-container', 'children'),
    Input('filtro-data-recebimento', 'start_date'),
    Input('filtro-data-recebimento', 'end_date')
)
def atualizar_recebimentos(start_date, end_date):
    if not start_date or not end_date:
        raise PreventUpdate
    df_full = preparar_dataframe_completo()
    if 'Data_Pagamento' not in df_full.columns or 'Vlr_Recebido' not in df_full.columns:
        return html.Div("As colunas 'Data_Pagamento' ou 'Vlr_Recebido' não foram encontradas.", style={'color': 'red'})
    df_full['Vlr_Recebido'] = pd.to_numeric(df_full['Vlr_Recebido'], errors='coerce').fillna(0)
    start_date_dt = pd.to_datetime(start_date)
    end_date_dt = pd.to_datetime(end_date)
    df_recebido_periodo = df_full[
        (df_full['Data_Pagamento'] >= start_date_dt) & 
        (df_full['Data_Pagamento'] <= end_date_dt)
    ]
    total_recebido = df_recebido_periodo['Vlr_Recebido'].sum()
    recebimentos_diarios = df_recebido_periodo.groupby(df_recebido_periodo['Data_Pagamento'].dt.date)['Vlr_Recebido'].sum()
    fig = go.Figure(go.Bar(
        x=recebimentos_diarios.index,
        y=recebimentos_diarios.values,
        text=recebimentos_diarios.values,
        texttemplate='R$ %{y:,.2f}',
        textposition='outside'
    ))
    fig.update_layout(
        title=f"<b>Recebimentos Diários de {start_date_dt.strftime('%d/%m')} a {end_date_dt.strftime('%d/%m')}</b>",
        xaxis_title="Data do Pagamento",
        yaxis_title="Valor Recebido (R$)",
        template="plotly_white"
    )
    kpi_card = html.Div([
        html.H3("Total Recebido no Período"),
        html.P(f"R$ {total_recebido:,.2f}", style={'fontSize': 24, 'fontWeight': 'bold', 'color': '#28a745'})
    ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px'})
    return html.Div([
        kpi_card,
        dcc.Graph(figure=fig)
    ])

@app.callback(
    Output('projecao-recebiveis-container', 'children'),
    Input('filtro-data-recebimento', 'end_date')
)
def atualizar_projecao_recebiveis(end_date):
    if not end_date:
        raise PreventUpdate
    df_full = preparar_dataframe_completo()
    hoje = pd.to_datetime('today').normalize()
    df_futuro = df_full[
        (df_full['Vencimento'] > hoje) & 
        (df_full['Data_Pagamento'].isna())
    ].copy()
    df_full['Adiantou'] = (df_full['Vencimento'] - df_full['Data_Pagamento']).dt.days > 5
    clientes_adiantam = df_full[df_full['Adiantou']]['Clientes'].unique()
    df_futuro['Bom_Pagador'] = df_futuro['Clientes'].isin(clientes_adiantam)
    def calcular_score(df_cliente, data_referencia_hoje):
        historico = df_cliente[(df_cliente['Vencimento'] >= (data_referencia_hoje - relativedelta(months=6))) & (df_cliente['Vencimento'] < data_referencia_hoje)]
        if historico.empty: return 1000, "Novo"
        score = 1000
        for _, row in historico.iterrows():
            dias = row['DIAS_DE_ATRASO']
            if dias < -5: score += 10
            elif 1 <= dias <= 10: score -= 20
            elif 11 <= dias <= 30: score -= 50
            elif dias > 30: score -= 100
        if score >= 950: return score, "Excelente"
        if score >= 800: return score, "Bom"
        if score >= 600: return score, "Atenção"
        return score, "Crítico"
    scores = {nome: calcular_score(df_full[df_full['Clientes'] == nome], hoje) for nome in df_futuro['Clientes'].unique()}
    df_futuro['Score_Valor'] = df_futuro['Clientes'].map(lambda x: scores.get(x, (0, ''))[0])
    df_futuro['Score_Categoria'] = df_futuro['Clientes'].map(lambda x: scores.get(x, (0, ''))[1])
    proximos_30_dias = df_futuro[df_futuro['Vencimento'] <= hoje + timedelta(days=30)].sort_values(by='Vencimento')
    header = html.Tr([html.Th("Vencimento"), html.Th("Cliente"), html.Th("Valor a Receber"), html.Th("Score"), html.Th("Paga Adiantado?")])
    rows = []
    for _, row in proximos_30_dias.iterrows():
        cor_score = {"Excelente": "#28a745", "Bom": "#198754", "Atenção": "#ffc107", "Crítico": "#dc3545"}.get(row['Score_Categoria'], 'grey')
        rows.append(html.Tr([
            html.Td(row['Vencimento'].strftime('%d/%m/%Y')),
            html.Td(row['Clientes']),
            html.Td(f"R$ {row['Vlr_Titulo']:,.2f}"),
            html.Td(html.Span(f"{row['Score_Categoria']} ({row['Score_Valor']})", style={'color': cor_score, 'fontWeight': 'bold'})),
            html.Td("✅ Sim" if row['Bom_Pagador'] else "Não", style={'textAlign': 'center'})
        ]))
    tabela_vencimentos = html.Table([header, html.Tbody(rows)], className="table table-striped")
    df_historico = df_full[df_full['Data_Pagamento'].notna()]
    media_mensal_recebida = df_historico.groupby(df_historico['Data_Pagamento'].dt.to_period('M'))['Vlr_Recebido'].sum().mean()
    projecao_card = html.Div([
        html.H4("Projeção Histórica"),
        html.P("Média mensal recebida nos últimos meses:"),
        html.P(f"R$ {media_mensal_recebida:,.2f}", style={'fontSize': 22, 'fontWeight': 'bold'})
    ], style={'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px', 'textAlign': 'center'})
    return html.Div([
        html.H2("Projeção de Recebíveis Futuros", style={'textAlign': 'center', 'marginTop': '40px'}),
        html.Div([
            html.Div([
                html.H4("Próximos 30 Dias a Vencer"),
                tabela_vencimentos
            ], style={'flex': 3, 'paddingRight': '20px'}),
            html.Div(projecao_card, style={'flex': 1})
        ], style={'display': 'flex'})
    ])

# --- NOVOS CALLBACKS PARA A PÁGINA DE COBRANÇA ---
@app.callback(
    Output('cobranca-container', 'children'),
    Input('url', 'pathname')
)
def atualizar_kpis_cobranca(pathname):
    if pathname != '/cobranca':
        raise PreventUpdate
    df_full = preparar_dataframe_completo()
    required_cols = ['Vencimento', 'DIAS_DE_ATRASO', 'Vlr_Titulo', 'Vlr_Recebido', 'Data_Pagamento']
    for col in required_cols:
        if col not in df_full.columns:
            return html.Div(f"Erro: A coluna '{col}' é essencial e não foi encontrada.", style={'color': 'red', 'textAlign': 'center'})
    
    # Análise de 2025
    df_2025 = df_full[df_full['Vencimento'].dt.year == 2025].copy()
    portfolio_2025 = df_2025[df_2025['DIAS_DE_ATRASO'] > 0]
    total_devido_2025 = portfolio_2025['Vlr_Titulo'].sum()
    recuperado_2025_df = portfolio_2025[portfolio_2025['Data_Pagamento'].notna()]
    total_recuperado_2025 = recuperado_2025_df['Vlr_Recebido'].sum()
    taxa_recuperacao_2025 = (total_recuperado_2025 / total_devido_2025) * 100 if total_devido_2025 > 0 else 0
    juros_df = recuperado_2025_df[recuperado_2025_df['Vlr_Recebido'] > recuperado_2025_df['Vlr_Titulo']].copy()
    juros_df['Juros'] = juros_df['Vlr_Recebido'] - juros_df['Vlr_Titulo']
    juros_2025 = juros_df['Juros'].sum()

    # Análise de 2024
    df_2024 = df_full[df_full['Vencimento'].dt.year == 2024].copy()
    portfolio_2024 = df_2024[df_2024['DIAS_DE_ATRASO'] > 0]
    total_devido_2024 = portfolio_2024['Vlr_Titulo'].sum()
    total_recuperado_2024 = portfolio_2024[portfolio_2024['Data_Pagamento'].notna()]['Vlr_Recebido'].sum()
    taxa_recuperacao_2024 = (total_recuperado_2024 / total_devido_2024) * 100 if total_devido_2024 > 0 else 0

    def criar_kpi_card(titulo, valor, cor_valor='#333', sufixo='', prefixo=''):
        return html.Div([
            html.H4(titulo, style={'fontWeight': 'normal', 'color': '#6c757d'}),
            html.P(f"{prefixo}{valor:,.2f}{sufixo}", style={'fontSize': 28, 'fontWeight': 'bold', 'color': cor_valor})
        ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '10px', 'flex': '1'})

    kpis_2025 = html.Div([
        criar_kpi_card("Taxa de Recuperação 2025", taxa_recuperacao_2025, '#28a745', sufixo='%'),
        criar_kpi_card("Juros Recebidos 2025", juros_2025, '#007bff', prefixo='R$ ')
    ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '30px'})

    fig_comparativo = go.Figure(go.Bar(
        x=['2024', '2025'],
        y=[taxa_recuperacao_2024, taxa_recuperacao_2025],
        text=[f"{taxa_recuperacao_2024:.1f}%", f"{taxa_recuperacao_2025:.1f}%"],
        textposition='auto', marker_color=['#6c757d', '#007bff']
    ))
    fig_comparativo.update_layout(
        title="<b>Taxa de Recuperação Anual (Títulos Vencidos)</b>",
        yaxis_title="Taxa de Recuperação (%)", template="plotly_white"
    )

    return html.Div([
        html.H3("Desempenho da Cobrança em 2025", style={'textAlign': 'center'}),
        html.P("Análise de todos os títulos vencidos.", style={'textAlign': 'center', 'color': 'grey'}),
        kpis_2025,
        dcc.Graph(figure=fig_comparativo)
    ])

@app.callback(
    Output('cobranca-recebimentos-diarios-container', 'children'),
    Input('url', 'pathname')
)
def atualizar_recebimentos_cobranca(pathname):
    if pathname != '/cobranca': raise PreventUpdate
    df_full = preparar_dataframe_completo()
    recuperados_2025 = df_full[
        (df_full['Vencimento'].dt.year == 2025) &
        (df_full['DIAS_DE_ATRASO'] > 0) &
        (df_full['Data_Pagamento'].notna())
    ]
    if recuperados_2025.empty:
        return html.H5("Nenhum título vencido recuperado em 2025.", style={'textAlign': 'center'})
    
    recebimentos_diarios = recuperados_2025.groupby(recuperados_2025['Data_Pagamento'].dt.date)['Vlr_Recebido'].sum()
    fig = go.Figure(go.Bar(
        x=recebimentos_diarios.index, y=recebimentos_diarios.values,
        text=recebimentos_diarios.values, texttemplate='R$ %{y:,.2f}', textposition='outside'
    ))
    fig.update_layout(title="<b>Valores Recuperados por Dia em 2025</b>", xaxis_title="Data do Pagamento", yaxis_title="Valor Recuperado (R$)", template="plotly_white")
    return dcc.Graph(figure=fig)

@app.callback(
    Output('cobranca-rankings-container', 'children'),
    Input('url', 'pathname')
)
def atualizar_rankings_cobranca(pathname):
    if pathname != '/cobranca': raise PreventUpdate
    df_full = preparar_dataframe_completo()
    
    recuperados_2025 = df_full[
        (df_full['Vencimento'].dt.year == 2025) &
        (df_full['DIAS_DE_ATRASO'] > 0) &
        (df_full['Data_Pagamento'].notna())
    ].copy()

    if recuperados_2025.empty: return None

    top_10_antigos = recuperados_2025.sort_values(by='Vencimento', ascending=True).head(10)
    top_10_valores = recuperados_2025.sort_values(by='Vlr_Recebido', ascending=False).head(10)

    df_pagos_atrasados = df_full[(df_full['Data_Pagamento'].notna()) & (df_full['DIAS_DE_ATRASO'] > 0)]
    campeoes_atraso = df_pagos_atrasados.groupby('Clientes')['DIAS_DE_ATRASO'].mean().reset_index()
    campeoes_atraso = campeoes_atraso.sort_values(by='DIAS_DE_ATRASO', ascending=False).head(10)

    def criar_tabela_ranking(titulo, df, colunas_map):
        header = [html.Th(col) for col in colunas_map.keys()]
        rows = []
        for _, row in df.iterrows():
            cells = []
            for col_df, format_func in colunas_map.values():
                cells.append(html.Td(format_func(row[col_df])))
            rows.append(html.Tr(cells))
        return html.Div([
            html.H5(titulo, style={'textAlign': 'center'}),
            html.Table([html.Thead(html.Tr(header)), html.Tbody(rows)], className="table table-sm table-striped")
        ], style={'flex': 1, 'minWidth': '300px'})

    tabela_antigos = criar_tabela_ranking(
        "Top 10 Títulos Mais Antigos Recuperados", top_10_antigos, 
        {"Vencimento": ("Vencimento", lambda x: x.strftime('%d/%m/%Y')), "Cliente": ("Clientes", lambda x: x), "Valor Recuperado": ("Vlr_Recebido", lambda x: f"R$ {x:,.2f}")}
    )
    tabela_valores = criar_tabela_ranking(
        "Top 10 Maiores Valores Recuperados", top_10_valores,
        {"Cliente": ("Clientes", lambda x: x), "Valor Recuperado": ("Vlr_Recebido", lambda x: f"R$ {x:,.2f}"), "Pago em": ("Data_Pagamento", lambda x: x.strftime('%d/%m/%Y'))}
    )
    tabela_campeoes = criar_tabela_ranking(
        "Top 10 Clientes com Maior Média de Atraso", campeoes_atraso,
        {"Cliente": ("Clientes", lambda x: x), "Média de Atraso": ("DIAS_DE_ATRASO", lambda x: f"{x:.0f} dias")}
    )

    return html.Div([
        html.H3("Rankings de Recuperação (2025)", style={'textAlign': 'center', 'marginTop': '40px'}),
        html.Div([tabela_antigos, tabela_valores, tabela_campeoes], style={'display': 'flex', 'gap': '20px', 'flexWrap': 'wrap'})
    ])

if __name__ == '__main__':
    app.run(debug=True)
