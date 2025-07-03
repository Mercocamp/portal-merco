from sheets_api import carregar_dados

# Nome da planilha e aba (exatamente como você passou)
nome_planilha = "BaseReceber2025"
nome_aba = "BaseReceber"

# Tenta carregar os dados
try:
    df = carregar_dados(nome_planilha, nome_aba)
    print("✅ Planilha carregada com sucesso!")
    print(df.head())  # Mostra as 5 primeiras linhas
    print("Colunas disponíveis:", df.columns.tolist())
except Exception as e:
    print("❌ Erro ao carregar planilha:")
    print(e)
