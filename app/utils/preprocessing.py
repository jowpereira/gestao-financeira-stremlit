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
    # Criando uma cópia para não modificar o original
    df_processed = df.copy()
    
    # Convertendo colunas de data
    if 'Data' in df_processed.columns:
        df_processed['Data'] = pd.to_datetime(df_processed['Data'], errors='coerce')
        
        # Extraindo mês e ano
        df_processed['Mes'] = df_processed['Data'].dt.month
        df_processed['Mes_Nome'] = df_processed['Data'].dt.month_name()
        df_processed['Ano'] = df_processed['Data'].dt.year
    
    # Convertendo valores monetários
    monetary_columns = [col for col in df_processed.columns if 'Valor' in col or 'Custo' in col]
    for col in monetary_columns:
        if df_processed[col].dtype == object:  # Se for string
            df_processed[col] = df_processed[col].str.replace('R$', '')
            df_processed[col] = df_processed[col].str.replace('.', '')
            df_processed[col] = df_processed[col].str.replace(',', '.')
        
        # Convertendo para float
        df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce')
    
    # Tratando valores nulos
    df_processed = df_processed.fillna({
        'Tipo': 'Não Classificado',
        'Categoria': 'Não Classificada'
    })
    
    # Valores monetários nulos como zero
    for col in monetary_columns:
        df_processed[col] = df_processed[col].fillna(0)
    
    # Validando tipos de despesa
    if 'Tipo' in df_processed.columns:
        # Corrigindo inconsistências
        for tipo in EXPENSE_TYPES:
            mask = df_processed['Tipo'].str.contains(tipo, case=False, na=False)
            df_processed.loc[mask, 'Tipo'] = tipo
    
    return df_processed

def categorize_expenses(df):
    """
    Categoriza despesas em Fixas, Variáveis e Não Operacionais
    
    Args:
        df (pandas.DataFrame): DataFrame com dados financeiros
        
    Returns:
        pandas.DataFrame: DataFrame com categorização aplicada
    """
    df_categorized = df.copy()
    
    # Mapeamento de categorias para tipos
    categoria_para_tipo = {
        'Aluguel': 'Fixo',
        'Energia': 'Fixo',
        'Água': 'Fixo',
        'Internet': 'Fixo',
        'Telefone': 'Fixo',
        'Salários': 'Fixo',
        'Seguros': 'Fixo',
        'Impostos': 'Fixo',
        'Material de Escritório': 'Variável',
        'Transporte': 'Variável',
        'Alimentação': 'Variável',
        'Marketing': 'Variável',
        'Manutenção': 'Variável',
        'Combustível': 'Variável',
        'Viagens': 'Não Operacional',
        'Investimentos': 'Não Operacional',
        'Financiamentos': 'Não Operacional',
        'Despesas Extraordinárias': 'Não Operacional'
    }
    
    # Aplicando o mapeamento
    if 'Categoria' in df_categorized.columns and 'Tipo' in df_categorized.columns:
        for categoria, tipo in categoria_para_tipo.items():
            mask = df_categorized['Categoria'].str.contains(categoria, case=False, na=False)
            df_categorized.loc[mask, 'Tipo'] = tipo
    
    return df_categorized

def calculate_financial_metrics(df, year=None):
    """
    Calcula métricas financeiras a partir dos dados
    
    Args:
        df (pandas.DataFrame): DataFrame com dados financeiros
        year (int, optional): Ano específico para filtrar os dados
        
    Returns:
        dict: Dicionário com métricas financeiras
    """
    # Filtrando por ano se especificado
    if year and 'Ano' in df.columns:
        df_filtered = df[df['Ano'] == year].copy()
    else:
        df_filtered = df.copy()
    
    # Calculando métricas financeiras
    metrics = {}
    
    # Total de despesas
    if 'Valor' in df_filtered.columns:
        metrics['total_despesas'] = df_filtered['Valor'].sum()
        
        # Despesas por tipo
        if 'Tipo' in df_filtered.columns:
            for tipo in EXPENSE_TYPES:
                tipo_despesas = df_filtered[df_filtered['Tipo'] == tipo]['Valor'].sum()
                metrics[f'total_{tipo.lower()}'] = tipo_despesas
                
                # Percentuais
                if metrics['total_despesas'] > 0:
                    metrics[f'percentual_{tipo.lower()}'] = (tipo_despesas / metrics['total_despesas']) * 100
                else:
                    metrics[f'percentual_{tipo.lower()}'] = 0
        
        # Despesas por mês
        if 'Mes' in df_filtered.columns:
            metrics['despesas_por_mes'] = df_filtered.groupby('Mes')['Valor'].sum().to_dict()
        
        # Despesas por categoria
        if 'Categoria' in df_filtered.columns:
            metrics['despesas_por_categoria'] = df_filtered.groupby('Categoria')['Valor'].sum().to_dict()
    
    # Total de receitas (se existir)
    if 'Receita' in df_filtered.columns:
        metrics['total_receitas'] = df_filtered['Receita'].sum()
        
        # Balanço (receitas - despesas)
        if 'Valor' in df_filtered.columns:
            metrics['balanco'] = metrics['total_receitas'] - metrics['total_despesas']
    
    # Métricas de veículos (se existirem)
    if 'Veiculo' in df_filtered.columns and 'KM' in df_filtered.columns and 'Litros' in df_filtered.columns:
        # Consumo médio por veículo
        veiculos = df_filtered['Veiculo'].unique()
        consumo_por_veiculo = {}
        
        for veiculo in veiculos:
            df_veiculo = df_filtered[df_filtered['Veiculo'] == veiculo]
            
            total_km = df_veiculo['KM'].sum()
            total_litros = df_veiculo['Litros'].sum()
            
            if total_litros > 0:
                consumo_medio = total_km / total_litros
            else:
                consumo_medio = 0
            
            consumo_por_veiculo[veiculo] = consumo_medio
        
        metrics['consumo_por_veiculo'] = consumo_por_veiculo
    
    return metrics 