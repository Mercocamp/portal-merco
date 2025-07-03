# login.py (NOVO LAYOUT FLUTUANTE)

from dash import html, dcc

layout = html.Div([
    # 1. Logo aumentada e com mais espaçamento
    html.Img(src="/assets/logo.png", style={
        'height': '176px', # Aumentado em mais 10%
        'marginBottom': '50px' # Espaçamento aumentado
    }),

    # 2. Container para os inputs e botão
    html.Div([
        # 3. Inputs um embaixo do outro e sem borda
        dcc.Input(id='usuario', placeholder='Usuário', type='text',
                  style={
                      'padding': '18px', 
                      'margin': '8px', 
                      'width': '320px', 
                      'borderRadius': '15px', 
                      'border': 'none', # Borda removida
                      'boxShadow': '0px 4px 15px rgba(0,0,0,0.08)', # Sombra sutil
                      'textAlign': 'center',
                      'fontSize': '16px'
                  }),
        
        dcc.Input(id='senha', placeholder='Senha', type='password', n_submit=0,
                  style={
                      'padding': '18px', 
                      'margin': '8px', 
                      'width': '320px', 
                      'borderRadius': '15px', 
                      'border': 'none', # Borda removida
                      'boxShadow': '0px 4px 15px rgba(0,0,0,0.08)', # Sombra sutil
                      'textAlign': 'center',
                      'fontSize': '16px'
                  }),

        html.Button("Entrar", id="botao-login", n_clicks=0,
                      style={
                          'marginTop': '25px', 
                          'padding': '15px 40px', 
                          'fontWeight': 'bold', 
                          'borderRadius': '15px', 
                          'cursor': 'pointer',
                          'border': 'none',
                          'backgroundColor': '#007bff',
                          'color': 'white'
                      }),

        html.Div(id="mensagem-erro", style={'color': 'red', 'marginTop': '20px'}),
        
    ], style={
        'display': 'flex',
        'flexDirection': 'column', # Garante que os itens fiquem um embaixo do outro
        'alignItems': 'center'  # Centraliza os itens horizontalmente
    })
], style={
    'height': '100vh',
    'display': 'flex',
    'flexDirection': 'column',
    'justifyContent': 'center',
    'alignItems': 'center',
    'backgroundColor': '#e9ecef'
})
