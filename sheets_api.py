# sheets_api.py (VERSÃO OTIMIZADA COM CACHE)

import os
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from functools import lru_cache # Importa o lru_cache

RENDER_SECRETS_PATH = "/etc/secrets/credentials.json"
LOCAL_SECRETS_PATH = "credentials.json"

# Adiciona o decorador para cachear o resultado da função
@lru_cache(maxsize=1)
def carregar_dados(planilha_nome: str, aba_nome: str) -> pd.DataFrame:
    """
    Carrega dados de uma planilha do Google Sheets, com cache e tratamento de erros.
    A função só será executada de verdade uma vez. Nas chamadas seguintes,
    retornará o resultado armazenado em memória.
    """
    escopo = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    creds_path = RENDER_SECRETS_PATH if os.path.exists(RENDER_SECRETS_PATH) else LOCAL_SECRETS_PATH

    print(f"INFO: Tentando carregar dados do Google Sheets (Planilha: {planilha_nome})...")
    try:
        credenciais = ServiceAccountCredentials.from_json_keyfile_name(creds_path, escopo)
        cliente = gspread.authorize(credenciais)
        planilha = cliente.open(planilha_nome)
        aba = planilha.worksheet(aba_nome)
        
        dados = aba.get_all_records(value_render_option='UNFORMATTED_VALUE')
        df = pd.DataFrame(dados)

        print(f"SUCESSO: Planilha carregada com {len(df)} linhas.")
        
        if not df.empty:
            df.columns = df.columns.str.strip()

        return df
    except Exception as e:
        error_message = f"ERRO FATAL ao carregar dados do Sheets: {e}"
        print(error_message)
        # Retorna um DataFrame com uma coluna de erro para que o app não quebre
        return pd.DataFrame({'Erro': [error_message]})
