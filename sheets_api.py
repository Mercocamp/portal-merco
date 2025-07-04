# sheets_api.py (VERSÃO PARA PRODUÇÃO COM LIMITE DE TESTE)

import os
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

RENDER_SECRETS_PATH = "/etc/secrets/credentials.json"
LOCAL_SECRETS_PATH = "credentials.json"

def carregar_dados(planilha_nome: str, aba_nome: str) -> pd.DataFrame:
    """
    Carrega dados de uma planilha do Google Sheets, adaptando-se
    ao ambiente de produção (Render) ou desenvolvimento local.
    """
    escopo = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    if os.path.exists(RENDER_SECRETS_PATH):
        creds_path = RENDER_SECRETS_PATH
    else:
        creds_path = LOCAL_SECRETS_PATH

    try:
        credenciais = ServiceAccountCredentials.from_json_keyfile_name(creds_path, escopo)
        cliente = gspread.authorize(credenciais)

        planilha = cliente.open(planilha_nome)
        aba = planilha.worksheet(aba_nome)
        
        dados = aba.get_all_records(value_render_option='UNFORMATTED_VALUE')
        df = pd.DataFrame(dados)

        print(f"✅ Planilha '{planilha_nome} | {aba_nome}' carregada com {len(df)} linhas.")
        
        # --- LIMITE TEMPORÁRIO PARA TESTE NO RENDER ---
        # Se o dataframe for muito grande, pegamos apenas as 500 linhas mais recentes para teste
        if len(df) > 500:
            df = df.tail(500).copy()
            print(f"✅ APLICANDO LIMITE DE TESTE. {len(df)} LINHAS SERÃO USADAS.")
        # -------------------------------------------------

        if not df.empty:
            df.columns = df.columns.str.strip()

        return df
    except Exception as e:
        error_message = f"❌ Erro ao carregar dados do Sheets: {e}."
        print(error_message)
        return pd.DataFrame({'Erro': [error_message]})
