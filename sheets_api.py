# sheets_api.py (VERSÃO FINAL OTIMIZADA)

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
        print("Usando credenciais do Render.")
    else:
        creds_path = LOCAL_SECRETS_PATH
        print("Usando credenciais locais.")

    try:
        credenciais = ServiceAccountCredentials.from_json_keyfile_name(creds_path, escopo)
        cliente = gspread.authorize(credenciais)

        planilha = cliente.open(planilha_nome)
        aba = planilha.worksheet(aba_nome)
        
        print(f"Buscando todos os registros de '{planilha_nome} | {aba_nome}'...")
        dados = aba.get_all_records(value_render_option='UNFORMATTED_VALUE')
        df = pd.DataFrame(dados)

        print(f"✅ Planilha carregada com sucesso. Total de {len(df)} linhas.")
        
        # ALTERAÇÃO: Bloco que limitava os dados a 500 linhas foi REMOVIDO.
        # Agora a função sempre retornará o DataFrame completo.

        if not df.empty:
            # Garante que os nomes das colunas não tenham espaços extras
            df.columns = df.columns.str.strip()

        return df
        
    except Exception as e:
        error_message = f"❌ Erro ao carregar dados do Sheets: {e}."
        print(error_message)
        # Retorna um DataFrame vazio com uma coluna de erro para facilitar a depuração
        return pd.DataFrame({'Erro': [error_message]})
