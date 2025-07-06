# sheets_api.py (SIMPLIFICADO E ROBUSTO)

import os
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from functools import lru_cache
from datetime import datetime

# --- FUNÇÃO DE CARREGAMENTO COM CACHE ---
# O cache aqui é útil para evitar múltiplas chamadas ao Sheets na mesma hora
# se o usuário navegar rapidamente entre páginas que precisam dos mesmos dados.
@lru_cache(maxsize=1)
def carregar_e_processar_dados(cache_key: str = None):
    """
    Carrega e processa todos os dados da planilha do Google Sheets.
    O cache_key (baseado na hora) garante que não buscamos os dados
    a cada clique, mas sim uma vez por hora ou quando o cache é limpo.
    """
    escopo = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    RENDER_SECRETS_PATH = "/etc/secrets/credentials.json"
    LOCAL_SECRETS_PATH = "credentials.json"
    creds_path = RENDER_SECRETS_PATH if os.path.exists(RENDER_SECRETS_PATH) else LOCAL_SECRETS_PATH

    try:
        print(f"Buscando dados do Google Sheets... Chave de cache: {cache_key}")
        credenciais = ServiceAccountCredentials.from_json_keyfile_name(creds_path, escopo)
        cliente = gspread.authorize(credenciais)
        planilha = cliente.open("BaseReceber2025")
        aba = planilha.worksheet("BaseReceber")
        
        dados = aba.get_all_records(value_render_option='UNFORMATTED_VALUE')
        df = pd.DataFrame(dados)
        print(f"✅ {len(df)} linhas carregadas com sucesso do Google Sheets.")

        # --- PROCESSAMENTO DE DADOS ---
        if 'Cliente' in df.columns and 'Clientes' not in df.columns: df.rename(columns={'Cliente': 'Clientes'}, inplace=True)
        
        text_cols = ['Clientes', 'Competencia', 'Tipo_Resumido', 'Lotacao']
        for col in text_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
                if col == 'Tipo_Resumido': df[col] = df[col].str.lower()
        
        numeric_cols = ['Vlr_Titulo', 'Vlr_Recebido']
        for col in numeric_cols:
            if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        date_cols = ['Vencimento', 'Data_Pagamento', 'Emissao']
        for col in date_cols:
            if col in df.columns:
                s_numeric = pd.to_numeric(df[col], errors='coerce')
                s_datetime = pd.to_datetime(df[col], errors='coerce', dayfirst=True)
                df[col] = s_datetime.fillna(pd.to_datetime('1899-12-30') + pd.to_timedelta(s_numeric, 'D'))
        
        if 'Vencimento' in df.columns and 'Data_Pagamento' in df.columns:
            df['DIAS_DE_ATRASO'] = 0
            pagas = df['Data_Pagamento'].notna() & df['Vencimento'].notna()
            df.loc[pagas, 'DIAS_DE_ATRASO'] = (df.loc[pagas, 'Data_Pagamento'] - df.loc[pagas, 'Vencimento']).dt.days
            hoje = pd.to_datetime("today").normalize()
            em_aberto_vencidas = df['Data_Pagamento'].isna() & (df['Vencimento'] < hoje)
            df.loc[em_aberto_vencidas, 'DIAS_DE_ATRASO'] = (hoje - df.loc[em_aberto_vencidas, 'Vencimento']).dt.days
            
        return df

    except Exception as e:
        print(f"❌ Erro ao carregar ou processar dados: {e}")
        return pd.DataFrame({'Erro': [str(e)]})

def get_data():
    """
    Função auxiliar que gera uma chave de cache baseada na hora atual
    e chama a função principal de carregamento.
    """
    cache_key = datetime.now().strftime('%Y-%m-%d-%H')
    return carregar_e_processar_dados(cache_key)

def clear_data_cache():
    """Função para limpar o cache de dados."""
    carregar_e_processar_dados.cache_clear()
