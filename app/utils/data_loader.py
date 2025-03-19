import pandas as pd
import os
from pathlib import Path
import sys

# Adiciona o diretório pai ao path para importar o módulo config
sys.path.append(str(Path(__file__).parent.parent))
from config import DATA_2023, DATA_2024, DATA_2025, BASE_DIR

def load_data(year):
    """
    Carrega os dados financeiros do ano especificado
    
    Args:
        year (int): Ano dos dados a serem carregados (2023, 2024 ou 2025)
        
    Returns:
        pandas.DataFrame: DataFrame com os dados do ano especificado
    """
    # Determina o caminho do arquivo
    if year == 2023:
        filepath_str = DATA_2023
    elif year == 2024:
        filepath_str = DATA_2024
    elif year == 2025:
        filepath_str = DATA_2025
    else:
        raise ValueError(f"Ano {year} não disponível. Use 2023, 2024 ou 2025.")
    
    # Converte para Path
    filepath = Path(filepath_str)
    print(f"DEBUG: Tentando abrir arquivo para {year}. Caminho inicial: {filepath}")
    print(f"DEBUG: O arquivo existe? {filepath.exists()}")
    
    # Lista todos os arquivos em diversos caminhos possíveis
    print("DEBUG: Listando arquivos disponíveis:")
    try:
        print(f"Arquivos em data/: {list(Path('data').glob('*.csv'))}")
    except Exception as e:
        print(f"Erro ao listar arquivos em data/: {e}")
    
    try:
        print(f"Arquivos em {BASE_DIR / 'data'}: {list((BASE_DIR / 'data').glob('*.csv'))}")
    except Exception as e:
        print(f"Erro ao listar arquivos em {BASE_DIR / 'data'}: {e}")
    
    # Tenta abrir o arquivo usando path absoluto primeiro
    try:
        absolute_path = BASE_DIR / 'data' / f'lgd{year}.csv'
        print(f"DEBUG: Tentando path absoluto: {absolute_path} (Existe: {absolute_path.exists()})")
        if absolute_path.exists():
            print(f"Encontrado arquivo em: {absolute_path}")
            df = pd.read_csv(absolute_path, delimiter=',', encoding='utf-8')
            print(f"Arquivo carregado com sucesso: {len(df)} linhas")
            return df
    except Exception as e:
        print(f"DEBUG: Erro ao tentar path absoluto: {e}")
    
    # Tenta diversos caminhos relativos
    relative_paths = [
        Path('data') / f'lgd{year}.csv',
        Path('./data') / f'lgd{year}.csv',
        Path('../data') / f'lgd{year}.csv',
        Path(f'data/lgd{year}.csv'),
        Path(f'./data/lgd{year}.csv'),
        Path(f'../data/lgd{year}.csv'),
        Path(f'lgd{year}.csv'),
        Path(f'./lgd{year}.csv'),
    ]
    
    for path in relative_paths:
        try:
            print(f"DEBUG: Tentando path relativo: {path} (Existe: {path.exists()})")
            if path.exists():
                print(f"Encontrado arquivo em: {path}")
                df = pd.read_csv(path, delimiter=',', encoding='utf-8')
                print(f"Arquivo carregado com sucesso: {len(df)} linhas")
                return df
        except Exception as e:
            print(f"DEBUG: Erro ao tentar path relativo {path}: {e}")
    
    # Se chegou aqui, tenta diretamente o filepath original
    try:
        print(f"DEBUG: Tentando usar o caminho original: {filepath}")
        df = pd.read_csv(filepath, delimiter=',', encoding='utf-8')
        print(f"Arquivo carregado com sucesso: {len(df)} linhas")
        return df
    except Exception as e:
        print(f"DEBUG: Erro ao tentar o caminho original {filepath}: {e}")
    
    # Se chegou aqui, não conseguiu encontrar o arquivo
    err_msg = (f"Arquivo para o ano {year} não encontrado. "
              f"Caminhos testados: {filepath_str}, {absolute_path}, {relative_paths}")
    raise FileNotFoundError(err_msg)

def load_all_data():
    """
    Carrega os dados de todos os anos disponíveis em um único DataFrame
    
    Returns:
        pandas.DataFrame: DataFrame com dados de todos os anos
    """
    dfs = []
    
    try:
        df_2023 = load_data(2023)
        df_2023['Ano'] = 2023
        dfs.append(df_2023)
    except (FileNotFoundError, ValueError, IOError) as e:
        print(f"Aviso: {e}")
    
    try:
        df_2024 = load_data(2024)
        df_2024['Ano'] = 2024
        dfs.append(df_2024)
    except (FileNotFoundError, ValueError, IOError) as e:
        print(f"Aviso: {e}")
    
    try:
        df_2025 = load_data(2025)
        df_2025['Ano'] = 2025
        dfs.append(df_2025)
    except (FileNotFoundError, ValueError, IOError) as e:
        print(f"Aviso: {e}")
    
    if not dfs:
        raise ValueError("Nenhum dado disponível para carregar.")
    
    # Concatena os DataFrames
    return pd.concat(dfs, ignore_index=True)

def get_available_years():
    """
    Retorna uma lista dos anos disponíveis nos dados
    
    Returns:
        list: Lista de anos disponíveis
    """
    years = []
    
    # Verifica diretamente com Path.exists()
    data_dir = BASE_DIR / 'data'
    
    if (data_dir / 'lgd2023.csv').exists():
        years.append(2023)
    
    if (data_dir / 'lgd2024.csv').exists():
        years.append(2024)
    
    if (data_dir / 'lgd2025.csv').exists():
        years.append(2025)
    
    # Se não encontrou nada, tenta caminhos relativos
    if not years:
        # Lista de caminhos para verificar
        relative_paths = [
            Path('data'),
            Path('./data'),
            Path('../data')
        ]
        
        for path in relative_paths:
            if (path / 'lgd2023.csv').exists():
                years.append(2023)
            if (path / 'lgd2024.csv').exists():
                years.append(2024)
            if (path / 'lgd2025.csv').exists():
                years.append(2025)
            
            if years:  # Se encontrou algum arquivo, para de procurar
                break
    
    print(f"Anos disponíveis: {years}")
    return years

if __name__ == "__main__":
    # Teste de carregamento de dados
    print("Testando carregamento de dados...")
    
    years = get_available_years()
    print(f"Anos disponíveis: {years}")
    
    for year in years:
        try:
            df = load_data(year)
            print(f"Dados de {year} carregados com sucesso!")
            print(f"Formato: {df.shape}")
            print(f"Colunas: {df.columns.tolist()}")
            print(f"Primeiras linhas:\n{df.head(2)}\n")
        except Exception as e:
            print(f"Erro ao carregar dados de {year}: {e}") 