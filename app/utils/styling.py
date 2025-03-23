import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import sys
from pathlib import Path

# Adiciona o diretório pai ao path para importar o módulo config
sys.path.append(str(Path(__file__).parent.parent))
from config import COLORS, DEFAULT_CURRENCY

def set_page_config():
    """
    Configura a página do Streamlit
    """
    st.set_page_config(
        page_title="Sistema de Gestão Financeira",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    # CSS personalizado
    st.markdown("""
    <style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 {
        color: #1E3A8A;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #F3F4F6;
        border-radius: 5px 5px 0px 0px;
        padding: 10px 16px;
        height: auto;
    }
    .stTabs [aria-selected="true"] {
        background-color: #E0E7FF;
        border-bottom: 2px solid #3B82F6;
    }
    .metric-card {
        background-color: #FFFFFF;
        border-radius: 5px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24);
    }
    .metric-title {
        font-size: 1rem;
        color: #6B7280;
        margin-bottom: 0.5rem;
    }
    .metric-value {
        font-size: 1.875rem;
        font-weight: bold;
        color: #111827;
    }
    .metric-delta {
        margin-top: 0.25rem;
        font-size: 0.875rem;
    }
    .positive {
        color: #10B981;
    }
    .negative {
        color: #EF4444;
    }
    </style>
    """, unsafe_allow_html=True)

def format_currency(value, precision=2):
    """
    Formata um valor como moeda (R$)
    
    Args:
        value (float): Valor a ser formatado
        precision (int): Número de casas decimais
        
    Returns:
        str: Valor formatado como moeda
    """
    try:
        value_float = float(value)
        return f"{DEFAULT_CURRENCY} {value_float:,.{precision}f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except (ValueError, TypeError):
        return f"{DEFAULT_CURRENCY} 0,00"

def format_percentage(value, precision=2):
    """
    Formata um valor como percentual
    
    Args:
        value (float): Valor a ser formatado
        precision (int): Número de casas decimais
        
    Returns:
        str: Valor formatado como percentual
    """
    try:
        value_float = float(value)
        return f"{value_float:.{precision}f}%".replace('.', ',')
    except (ValueError, TypeError):
        return "0,00%"

def format_table_currency(df, columns):
    """
    Formata colunas de um DataFrame como moeda
    
    Args:
        df (pandas.DataFrame): DataFrame a ser formatado
        columns (list): Lista de colunas a serem formatadas
        
    Returns:
        pandas.DataFrame: DataFrame formatado
    """
    df_styled = df.copy()
    
    for col in columns:
        if col in df_styled.columns:
            df_styled[col] = df_styled[col].apply(lambda x: format_currency(x))
    
    return df_styled

def create_metric_card(label, value, delta=None, is_currency=False, is_percentage=False, delta_sign=True, suffix=""):
    """
    Creates a metric card with formatted values
    
    Args:
        label (str): Title of the metric card
        value (float): Main value to display
        delta (float, optional): Delta/change value to display below main value
        is_currency (bool): Whether to format as currency
        is_percentage (bool): Whether to format delta as percentage
        delta_sign (bool): Whether to show +/- signs for delta
        suffix (str): Optional suffix to append to the value (e.g. "km", "%")
    """
    if is_currency:
        formatted_value = format_currency(value)
    else:
        formatted_value = f"{value:,.2f}{suffix}"
        
    if delta is not None:
        if is_percentage:
            delta_value = abs(delta) if not delta_sign else delta
            delta_text = f"{delta_value:.1f}%"
        else:
            delta_value = abs(delta) if not delta_sign else delta
            delta_text = format_currency(delta_value) if is_currency else f"{delta_value:.2f}{suffix}"
    else:
        delta_text = None
        
    st.metric(label, formatted_value, delta_text)

def plot_bar_chart(df, x, y, title="", color=None, color_discrete_map=None, text_auto=True, **kwargs):
    """
    Cria um gráfico de barras usando Plotly
    
    Args:
        df (pandas.DataFrame): DataFrame com os dados
        x (str): Coluna para o eixo X
        y (str): Coluna para o eixo Y
        title (str, optional): Título do gráfico
        color (str, optional): Coluna para colorir as barras
        color_discrete_map (dict, optional): Mapeamento de cores
        text_auto (bool, optional): Se deve mostrar os valores nas barras
        
    Returns:
        plotly.graph_objects.Figure: Figura do Plotly
    """
    fig = px.bar(
        df, 
        x=x, 
        y=y, 
        title=title,
        color=color,
        color_discrete_map=color_discrete_map or COLORS,
        text_auto=text_auto,
        **kwargs
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        title_font_size=18,
        title_font_family="Arial",
        legend_title_font_size=12,
        font=dict(family="Arial", size=12),
        margin=dict(l=50, r=50, t=80, b=50),
    )
    
    return fig

def plot_pie_chart(df, values, names, title="", color_discrete_map=None, **kwargs):
    """
    Cria um gráfico de pizza usando Plotly
    
    Args:
        df (pandas.DataFrame): DataFrame com os dados
        values (str): Coluna para os valores
        names (str): Coluna para os nomes das fatias
        title (str, optional): Título do gráfico
        color_discrete_map (dict, optional): Mapeamento de cores
        
    Returns:
        plotly.graph_objects.Figure: Figura do Plotly
    """
    fig = px.pie(
        df, 
        values=values, 
        names=names, 
        title=title,
        color=names,
        color_discrete_map=color_discrete_map or COLORS,
        **kwargs
    )
    
    fig.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        insidetextfont=dict(size=12)
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        title_font_size=18,
        title_font_family="Arial",
        legend_title_font_size=12,
        font=dict(family="Arial", size=12),
        margin=dict(l=50, r=50, t=80, b=50),
    )
    
    return fig

def plot_line_chart(df, x, y, title="", color=None, color_discrete_map=None, markers=True, **kwargs):
    """
    Cria um gráfico de linha usando Plotly
    
    Args:
        df (pandas.DataFrame): DataFrame com os dados
        x (str): Coluna para o eixo X
        y (str): Coluna para o eixo Y
        title (str, optional): Título do gráfico
        color (str, optional): Coluna para colorir as linhas
        color_discrete_map (dict, optional): Mapeamento de cores
        markers (bool, optional): Se deve mostrar marcadores
        
    Returns:
        plotly.graph_objects.Figure: Figura do Plotly
    """
    fig = px.line(
        df, 
        x=x, 
        y=y, 
        title=title,
        color=color,
        color_discrete_map=color_discrete_map or COLORS,
        markers=markers,
        **kwargs
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        title_font_size=18,
        title_font_family="Arial",
        legend_title_font_size=12,
        font=dict(family="Arial", size=12),
        margin=dict(l=50, r=50, t=80, b=50),
    )
    
    return fig