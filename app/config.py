import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Diretório do projeto (usa o diretório do módulo atual)
BASE_DIR = Path(__file__).parent.parent.absolute()

# Configurações da aplicação
APP_TITLE = os.getenv("APP_TITLE", "Sistema de Gestão Financeira")
APP_THEME = os.getenv("APP_THEME", "light")

# Caminhos de arquivos - com fallback para paths diretos caso o .env falhe
DATA_PATH = os.getenv("DATA_PATH", str(BASE_DIR / "data"))
DATA_2023 = os.getenv("DATA_2023", str(BASE_DIR / "data" / "lgd2023.csv"))
DATA_2024 = os.getenv("DATA_2024", str(BASE_DIR / "data" / "lgd2024.csv"))
DATA_2025 = os.getenv("DATA_2025", str(BASE_DIR / "data" / "lgd2025.csv"))

# Configurações de visualização
DEFAULT_CURRENCY = os.getenv("DEFAULT_CURRENCY", "R$")
DEFAULT_YEAR = int(os.getenv("DEFAULT_YEAR", "2024"))

# Cores para visualizações
COLORS = {
    "primary": "#7FB3D5",     # azul suave
    "secondary": "#F5B041",   # laranja pastel
    "fixed": "#82E0AA",      # verde menta
    "variable": "#F1948A",   # rosa salmão
    "non_operational": "#C39BD3",  # lilás suave
    "warning": "#FAD7A0",    # pêssego
    "info": "#85C1E9"        # azul céu
}

# Tipos de despesas
EXPENSE_TYPES = [
    "Fixo",
    "Investimento",
    "Saída Não Operacional",
    "Variável",
    "TH Parfum"
]

# Meses para visualizações
MONTHS = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

# Informações de debug
print(f"Diretório base: {BASE_DIR}")
print(f"Diretório de dados: {DATA_PATH}")
print(f"Arquivos:")
print(f"2023: {DATA_2023} (existe: {Path(DATA_2023).exists()})")
print(f"2024: {DATA_2024} (existe: {Path(DATA_2024).exists()})")
print(f"2025: {DATA_2025} (existe: {Path(DATA_2025).exists()})")