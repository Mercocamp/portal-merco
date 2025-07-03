# operacao.py

from dash import dcc, html

# Estrutura dos Centros de Distribuição
cds_structure = {
    "CD Matriz": ["CD MATRIZ", "CD MATRIZ A", "CD MATRIZ B"],
    "CD Cariacica": ["CD CARIACICA 2", "CD CARIACICA 3"],
    "CD Viana": [],
    "CD Civit": []
}

# Função para criar os links de forma padronizada
def create_cd_link(cd_name):
    # Cria uma URL amigável (ex: 'CD MATRIZ A' vira 'cd-matriz-a')
    href_slug = cd_name.lower().replace(' ', '-')
    return dcc.Link(
        cd_name, 
        href=f'/operacao/{href_slug}', 
        className='cd-link-button' # Classe para estilização futura
    )

# Monta a lista de componentes do layout
layout_items = [
    html.H2("Visão Operacional por Centro de Distribuição", style={'textAlign': 'center', 'marginBottom': '30px', 'color': '#333'})
]

for cd_principal, galpoes in cds_structure.items():
    if not galpoes:
        # Se não há galpões (submenus), cria um link direto
        layout_items.append(create_cd_link(cd_principal))
    else:
        # Se há galpões, cria um menu expansível (accordion)
        layout_items.append(
            html.Details([
                html.Summary(cd_principal, className='cd-summary-header'),
                html.Div([
                    create_cd_link(galpao) for galpao in galpoes
                ], className='cd-submenu-container')
            ], className='cd-details-group')
        )

# Adiciona um botão para voltar ao menu principal
layout_items.append(
    dcc.Link("⬅️ Voltar ao Menu Principal", href="/menu", style={
        'display': 'inline-block', 
        'marginTop': '40px', 
        'textDecoration': 'none',
        'color': '#007bff',
        'fontWeight': 'bold'
    })
)

# Layout final da página
layout = html.Div(layout_items, style={
    'maxWidth': '800px',
    'margin': '50px auto',
    'padding': '40px',
    'textAlign': 'center',
    'backgroundColor': '#f8f9fa',
    'borderRadius': '15px',
    'boxShadow': '0 6px 15px rgba(0,0,0,0.08)'
})

# Adicione este CSS ao seu arquivo de estilos (ex: assets/menu_styles.css)
# para que os botões e menus fiquem com uma aparência melhor.
"""
/* CSS para operacao.py - Adicionar em assets/menu_styles.css */

.cd-link-button, .cd-summary-header {
    display: block;
    padding: 15px 20px;
    margin: 10px auto;
    background-color: #fff;
    border: 1px solid #ddd;
    border-radius: 8px;
    text-decoration: none;
    color: #333;
    font-weight: 600;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.2s ease-in-out;
    max-width: 400px;
}

.cd-link-button:hover, .cd-summary-header:hover {
    background-color: #007bff;
    color: white;
    border-color: #007bff;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.cd-details-group {
    margin-bottom: 10px;
}

.cd-details-group[open] .cd-summary-header {
    background-color: #0056b3;
    color: white;
}

.cd-submenu-container {
    padding: 10px;
    background-color: #f0f0f0;
    border-radius: 0 0 8px 8px;
    margin: -10px auto 10px;
    max-width: 400px;
}

.cd-submenu-container .cd-link-button {
    background-color: #e9ecef;
    font-weight: normal;
}
"""
