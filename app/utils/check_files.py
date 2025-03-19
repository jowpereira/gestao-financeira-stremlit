import pandas as pd
import os
from pathlib import Path
import sys

# Adiciona o diretório pai ao path para importar o módulo config
current_dir = Path(__file__).parent
app_dir = current_dir.parent
root_dir = app_dir.parent
sys.path.append(str(app_dir))

try:
    from config import DATA_2023, DATA_2024, DATA_2025, BASE_DIR
    config_loaded = True
except ImportError:
    print("Não foi possível importar variáveis do config.py")
    config_loaded = False
    BASE_DIR = root_dir

def check_file_exists(filename, year):
    """Testa vários caminhos para verificar onde o arquivo pode ser encontrado"""
    print(f"\nVerificando arquivo: {filename}")
    
    # Imprime diretório atual
    print(f"Diretório atual: {os.getcwd()}")
    
    # Lista arquivos no diretório data/
    try:
        data_files = os.listdir("data")
        print(f"Arquivos em 'data/': {data_files}")
    except Exception as e:
        print(f"Erro ao listar diretório data/: {e}")
    
    # Testa caminhos com diferentes formatos de slash
    paths_to_check = [
        f"data\\{filename}",
        f"data/{filename}",
        os.path.join(os.getcwd(), "data", filename),
        f"data\\{filename}"
    ]
    
    for path in paths_to_check:
        exists = os.path.exists(path)
        print(f"Caminho: {path} | Existe: {exists}")
    
    # Verifica se pode abrir e ler o arquivo
    try:
        df = pd.read_csv(f"data/{filename}")
        print(f"Arquivo lido com sucesso! Formato: {df.shape}")
        return True
    except Exception as e:
        print(f"Erro ao tentar abrir o arquivo: {e}")
        return False

def test_with_pathlib():
    """Testa funcionalidades do módulo pathlib"""
    print("\nTeste com pathlib.Path:")
    
    years = [2023, 2024, 2025]
    
    for year in years:
        filename = f"lgd{year}.csv"
        
        # Caminho relativo
        path = Path("data") / filename
        print(f"Path: {path} | Existe: {path.exists()}")
        
        # Caminho absoluto
        abs_path = Path(os.getcwd()) / "data" / filename
        print(f"Path absoluto: {abs_path} | Existe: {abs_path.exists()}")
        
        # Tenta abrir o arquivo
        try:
            if path.exists():
                df = pd.read_csv(path)
                print(f"Arquivo {filename} lido com sucesso! {len(df)} linhas")
        except Exception as e:
            print(f"Erro ao abrir {path}: {e}")

def create_dummy_data():
    """Cria arquivos de dados de exemplo caso não existam"""
    print("\nVerificando se é necessário criar dados de exemplo:")
    
    # Verifica se o diretório data existe
    data_dir = Path("data")
    if not data_dir.exists():
        print("Criando diretório data/")
        data_dir.mkdir(exist_ok=True)
    
    years = [2023, 2024, 2025]
    
    for year in years:
        filepath = data_dir / f"lgd{year}.csv"
        
        if not filepath.exists():
            print(f"Criando arquivo de dados de exemplo para {year}...")
            
            # Cria dados básicos para teste
            data = {
                'Mês': ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'],
                'Valor': [1000, 1200, 950, 1100, 1300, 1400, 1250, 1350, 1500, 1450, 1600, 1700],
                'Categoria': ['Fixo'] * 12
            }
            
            # Cria o DataFrame e salva como CSV
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False)
            print(f"Arquivo {filepath} criado com sucesso.")
        else:
            print(f"Arquivo {filepath} já existe.")

if __name__ == "__main__":
    print("Verificando arquivos de dados...")
    
    # Verifica se os arquivos existem
    check_file_exists("lgd2023.csv", 2023)
    check_file_exists("lgd2024.csv", 2024)
    check_file_exists("lgd2025.csv", 2025)
    
    # Testa com pathlib
    test_with_pathlib()
    
    # Cria dados de exemplo se necessário
    create_dummy_data()
    
    print("\nTeste completo!") 