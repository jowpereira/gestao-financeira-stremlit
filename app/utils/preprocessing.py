import pandas as pd
import numpy as np
from datetime import datetime
import sys
from pathlib import Path

# Adiciona o diretório pai ao path para importar o módulo config
sys.path.append(str(Path(__file__).parent.parent))
from config import EXPENSE_TYPES

def preprocess_financial_data(df):
    """
    Pré-processa dados financeiros
    
    Args:
        df (pandas.DataFrame): DataFrame com dados financeiros
        
    Returns:
        pandas.DataFrame: DataFrame processado
    """
    df_processed = df.copy()

    if 'Conta' in df_processed.columns:
        df_processed['Conta'] = df_processed['Conta'].fillna('Não Informado')
        df_processed['Conta'] = df_processed['Conta'].str.strip().str.title()
        
    # Convertendo colunas de data
    if 'Data' in df_processed.columns:
        df_processed['Data'] = pd.to_datetime(df_processed['Data'], errors='coerce')
        df_processed['Mes'] = df_processed['Data'].dt.month
        df_processed['Mes_Nome'] = df_processed['Data'].dt.month_name()
        df_processed['Ano'] = df_processed['Data'].dt.year
        df_processed['Mês Ano'] = df_processed['Data'].dt.strftime('%B %Y')  # Add this line

    # Convertendo valores monetários
    monetary_columns = ['Valor']
    for col in monetary_columns:
        if df_processed[col].dtype == object:
            df_processed[col] = df_processed[col].astype(str)
            df_processed[col] = df_processed[col].str.replace('R\$', '', regex=True)
            df_processed[col] = df_processed[col].str.replace('.', '', regex=False)
            df_processed[col] = df_processed[col].str.replace(',', '.', regex=False)
        df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce').fillna(0)

    # Preenchendo colunas vazias com padrão
    df_processed['Tipo'] = df_processed['Tipo'].fillna('Não Classificado')
    df_processed['Categoria'] = df_processed['Categoria'].fillna('Não Classificada')

    # Padroniza os tipos com base em EXPENSE_TYPES
    for tipo in EXPENSE_TYPES:
        mask = df_processed['GASTOS'].str.contains(tipo, case=False, na=False)
        df_processed.loc[mask, 'GASTOS'] = tipo

    return df_processed

def calculate_financial_metrics(df, year=None):
    """
    Calcula métricas financeiras a partir dos dados
    
    Args:
        df (pandas.DataFrame): DataFrame com dados financeiros
        year (int, optional): Ano específico para filtrar os dados
        
    Returns:
        dict: Dicionário com métricas financeiras
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
        
    if year and year not in df['Ano'].unique():
        raise ValueError(f"Year {year} not found in the dataset")
        
    df_filtered = df[df['Ano'] == year] if year else df.copy()
    
    # Standardize GASTOS column values before filtering
    df_filtered['GASTOS'] = df_filtered['GASTOS'].astype(str).str.strip().str.title()
    df_filtered = df_filtered[df_filtered['GASTOS'].isin(EXPENSE_TYPES)]

    metrics = {}
    metrics['total_despesas'] = df_filtered['Valor'].sum()

    for tipo in EXPENSE_TYPES:
        valor = df_filtered[df_filtered['GASTOS'] == tipo]['Valor'].sum()
        metrics[f'total_{tipo.lower().replace(" ", "_")}'] = valor
        metrics[f'percentual_{tipo.lower().replace(" ", "_")}'] = (
            (valor / metrics['total_despesas']) * 100 if metrics['total_despesas'] > 0 else 0
        )

    if 'Mes' in df_filtered.columns:
        metrics['despesas_por_mes'] = df_filtered.groupby('Mes')['Valor'].sum().to_dict()

    if 'Categoria' in df_filtered.columns:
        metrics['despesas_por_categoria'] = df_filtered.groupby('Categoria')['Valor'].sum().to_dict()

    return metrics