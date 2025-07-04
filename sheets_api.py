# sheets_api.py (VERSÃO CORRIGIDA)

import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import os  # <- movi para cima para manter organizado

def carregar_dados(planilha_nome: str, aba_nome: str) -> pd.DataFrame:
    """
    Carrega dados de uma planilha do Google Sheets.
    A principal alteração é o uso de 'value_render_option' para obter
    os valores numéricos puros, em vez de texto formatado.
    """
    escopo = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # Verifica se está no Render (com o arquivo secreto)
    if os.path.exists('/etc/secrets/credentials.json'):
        caminho_credenciais = '/etc/secrets/credentials.json'
    else:
        # Rodando localmente
        caminho_credenciais = 'credentials.json'

    credenciais = ServiceAccountCredentials.from_json_keyfile_name(caminho_credenciais, escopo)
    cliente = gspread.authorize(credenciais)

    planilha = cliente.open(planilha_nome)
    aba = planilha.worksheet(aba_nome)
    
    # --- ALTERAÇÃO PRINCIPAL AQUI ---
    # Pedimos ao Google os valores como números puros (ex: 6200) e não como texto formatado (ex: "R$ 6.200,00").
    dados = aba.get_all_records(value_render_option='UNFORMATTED_VALUE')

    df = pd.DataFrame(dados)

    # Garante que os nomes das colunas não tenham espaços extras
    df.columns = df.columns.str.strip()

    return df
