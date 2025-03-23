import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Adiciona diretórios ao path para importar módulos
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "utils"))

from utils.data_loader import load_data
from utils.preprocessing import preprocess_financial_data, calculate_financial_metrics
from utils.styling import (
    format_currency, format_percentage, create_metric_card,
    plot_bar_chart, plot_pie_chart, plot_line_chart, format_table_currency
)
from config import COLORS, MONTHS

def calculate_vehicle_metrics(df):
    """Calculate vehicle metrics with validation"""
    metrics = {}
    
    # Total expenses
    metrics['total_gasto'] = df['Valor'].sum()
    
    # Average expense per vehicle
    metrics['gasto_medio'] = df.groupby('Veículos')['Valor'].sum().mean()
    
    # Total mileage (max - min per vehicle)
    if 'KM' in df.columns:
        km_por_veiculo = df.groupby('Veículos')['KM'].agg(['min', 'max'])
        km_por_veiculo['km_rodados'] = km_por_veiculo['max'] - km_por_veiculo['min']
        metrics['km_total'] = km_por_veiculo['km_rodados'].sum()
        
        # Cost per km
        metrics['custo_por_km'] = (
            metrics['total_gasto'] / metrics['km_total'] 
            if metrics['km_total'] > 0 else 0
        )
    
    return metrics

def plot_monthly_analysis(df):
    """Plot monthly trends"""
    if 'Data' not in df.columns:
        return
        
    df['Mês'] = pd.to_datetime(df['Data']).dt.to_period('M')
    df_mensal = df.groupby('Mês').agg({
        'Valor': 'sum',
        'KM': lambda x: x.max() - x.min() if 'KM' in df.columns else 0,
        'Litros': 'sum'
    }).reset_index()
    
    df_mensal['Mês'] = df_mensal['Mês'].astype(str)
    df_mensal['Custo_por_KM'] = np.where(
        df_mensal['KM'] > 0,
        df_mensal['Valor'] / df_mensal['KM'],
        0
    )
    
    # Plot monthly trends
    st.subheader("Análise Mensal")
    fig = plot_line_chart(
        df_mensal,
        x="Mês",
        y="Valor",
        title="Gastos Mensais",
        color_discrete_sequence=[COLORS["primary"]]
    )
    st.plotly_chart(fig, use_container_width=True)

def veiculos_view():
    """
    Componente de visualização de Análise de Veículos
    """
    st.header("🚗 Análise de Veículos")
    
    # Seletor de ano
    available_years = [2023, 2024, 2025]
    selected_year = st.selectbox("Selecione o ano", available_years, index=1)  # 2024 como padrão
    
    try:
        # Carrega e processa os dados
        df = load_data(selected_year)
        
        # Ajuste para garantir que as colunas sejam corretamente processadas
        df_processed = preprocess_financial_data(df)
        
        # Verifica se há dados de veículos
        if 'Veículos' not in df_processed.columns:
            st.warning("Este conjunto de dados não contém informações de veículos.")
            return
        
        # Filtra apenas despesas com veículos
        df_veiculos = df_processed[df_processed['Veículos'].notna()]
        
        if df_veiculos.empty:
            st.warning("Não há registros de veículos para este ano.")
            return
        
        # Obtém lista de veículos
        veiculos = df_veiculos['Veículos'].unique().tolist()
        
        # Improved vehicle filter
        if len(veiculos) > 1:
            col1, col2 = st.columns([3, 1])
            with col1:
                selected_veiculo = st.multiselect(
                    "Selecione o veículo:",
                    options=veiculos,  # Removed "Todos" from options
                    default=[],
                    key="vehicle_filter"
                )
            with col2:
                if st.button("Selecionar Todos"):
                    st.session_state.vehicle_filter = veiculos
                    
            # Apply filter
            df_veiculos = (
                df_veiculos if not selected_veiculo 
                else df_veiculos[df_veiculos['Veículos'].isin(selected_veiculo)]
            )
        
        # Verifica se há dados de abastecimento
        tem_abastecimento = all(col in df_veiculos.columns for col in ['KM', 'Litros'])
        
        # Cria métricas gerais
        metrics = calculate_vehicle_metrics(df_veiculos)
        
        # Layout em colunas para métricas
        st.subheader("Métricas Gerais")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            create_metric_card(
                "Total Gasto", 
                metrics['total_gasto'],
                is_currency=True
            )
        
        with col2:
            create_metric_card(
                "Gasto Médio por Veículo", 
                metrics['gasto_medio'],
                is_currency=True
            )
        
        with col3:
            if 'KM' in df_veiculos.columns:
                create_metric_card(
                    "Quilometragem Total", 
                    metrics['km_total'],
                    is_currency=False,
                    suffix=" km"  # Space before km for better formatting
                )
            else:
                st.info("Dados de quilometragem não disponíveis")
        
        with col4:
            if metrics['custo_por_km'] > 0:
                create_metric_card(
                    "Custo por KM", 
                    metrics['custo_por_km'],
                    is_currency=True
                )
            else:
                st.info("Impossível calcular custo por KM")
        
        st.markdown("---")
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de gastos por veículo
            st.subheader("Gastos por Veículo")
            
            df_por_veiculo = df_veiculos.groupby('Veículos')['Valor'].sum().reset_index()
            df_por_veiculo = df_por_veiculo.sort_values('Valor', ascending=False)
            
            fig = plot_bar_chart(
                df_por_veiculo,
                x="Veículos",
                y="Valor",
                title="Gastos Totais por Veículo",
                color_discrete_sequence=[COLORS["primary"]]
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Gráfico de categorias de gastos
            st.subheader("Gastos por Categoria")
            
            if 'Categoria' in df_veiculos.columns:
                # Filter out "Medição" entries and standardize category names
                df_categorias = df_veiculos[df_veiculos['Conta'] != 'Medição'].copy()
                df_categorias['Categoria'] = df_categorias['Categoria'].str.strip().str.title()
                
                if df_categorias.empty:
                    st.warning("Sem dados de categoria após filtrar medições.")
                else:
                    # Group and sort by value
                    df_categorias = df_categorias.groupby('Categoria')['Valor'].sum().reset_index()
                    df_categorias = df_categorias.sort_values('Valor', ascending=False)
                    
                    fig = plot_pie_chart(
                        df_categorias,
                        values="Valor",
                        names="Categoria",
                        title="Distribuição de Gastos por Categoria"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Dados de categoria não disponíveis.")
        
        # Análise de Eficiência (se houver dados)
        if tem_abastecimento:
            st.subheader("Análise de Eficiência de Combustível")
            
            # Cálculo de eficiência
            df_abastecimentos = df_veiculos[df_veiculos['Litros'] > 0].copy()
            
            # Agrupa por veículo
            df_eficiencia = df_abastecimentos.groupby('Veículos').agg({
                'KM': 'max',
                'Litros': 'sum',
                'Valor': 'sum'
            }).reset_index()
            
            # Calcula eficiência (km/l)
            df_eficiencia['Eficiencia'] = df_eficiencia['KM'] / df_eficiencia['Litros']
            
            # Calcula custo por km
            df_eficiencia['Custo_por_KM'] = df_eficiencia['Valor'] / df_eficiencia['KM']
            
            # Layout em colunas
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de eficiência
                fig = plot_bar_chart(
                    df_eficiencia,
                    x="Veículos",
                    y="Eficiencia",
                    title="Eficiência de Combustível (km/l)",
                    color_discrete_sequence=[COLORS["info"]]
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Gráfico de custo por km
                fig = plot_bar_chart(
                    df_eficiencia,
                    x="Veículos",
                    y="Custo_por_KM",
                    title="Custo por Quilômetro (R$/km)",
                    color_discrete_sequence=[COLORS["warning"]]
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Tabela de eficiência
            st.subheader("Tabela de Eficiência")
            
            # Prepara tabela formatada
            df_eficiencia_formatada = df_eficiencia.copy()
            df_eficiencia_formatada['Eficiencia'] = df_eficiencia_formatada['Eficiencia'].apply(lambda x: f"{x:.2f} km/l")
            df_eficiencia_formatada['Custo_por_KM'] = df_eficiencia_formatada['Custo_por_KM'].apply(lambda x: format_currency(x))
            df_eficiencia_formatada['Valor'] = df_eficiencia_formatada['Valor'].apply(lambda x: format_currency(x))
            
            st.dataframe(
                df_eficiencia_formatada,
                column_config={
                    "Veículos": st.column_config.TextColumn("Veículo"),
                    "KM": st.column_config.NumberColumn("Quilometragem", format="%d km"),
                    "Litros": st.column_config.NumberColumn("Combustível", format="%.2f L"),
                    "Valor": st.column_config.TextColumn("Custo Total"),
                    "Eficiencia": st.column_config.TextColumn("Eficiência"),
                    "Custo_por_KM": st.column_config.TextColumn("Custo por KM")
                },
                use_container_width=True
            )
        
        # Análise Mensal
        plot_monthly_analysis(df_veiculos)
        
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        st.info(f"Verifique se os arquivos CSV para o ano {selected_year} estão disponíveis e formatados corretamente.")


if __name__ == "__main__":
    # Teste do componente
    veiculos_view()