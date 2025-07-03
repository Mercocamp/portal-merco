# sheets_api.py (VERSÃO CORRIGIDA)

import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

def carregar_dados(planilha_nome: str, aba_nome: str) -> pd.DataFrame:
    """
    Carrega dados de uma planilha do Google Sheets.
    A principal alteração é o uso de 'value_render_option' para obter
    os valores numéricos puros, em vez de texto formatado.
    """
    escopo = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    credenciais = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", escopo)
    cliente = gspread.authorize(credenciais)

    planilha = cliente.open(planilha_nome)
    aba = planilha.worksheet(aba_nome)
    
    # --- ALTERAÇÃO PRINCIPAL AQUI ---
    # Pedimos ao Google os valores como números puros (ex: 6200) e não como texto formatado (ex: "R$ 6.200,00").
    # Isso resolve a raiz do problema de cálculo.
    dados = aba.get_all_records(value_render_option='UNFORMATTED_VALUE')

    df = pd.DataFrame(dados)

    # Garante que os nomes das colunas não tenham espaços extras
    df.columns = df.columns.str.strip()

    return df
