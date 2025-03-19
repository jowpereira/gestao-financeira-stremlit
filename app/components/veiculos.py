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
        
        # Filtro de veículo
        if len(veiculos) > 1:
            selected_veiculo = st.multiselect(
                "Selecione o veículo:",
                options=["Todos"] + veiculos,
                default=["Todos"]
            )
            
            # Aplica filtro
            if "Todos" not in selected_veiculo:
                df_veiculos = df_veiculos[df_veiculos['Veículos'].isin(selected_veiculo)]
        
        # Verifica se há dados de abastecimento
        tem_abastecimento = all(col in df_veiculos.columns for col in ['KM', 'Litros'])
        
        # Cria métricas gerais
        # Total gasto com veículos
        total_gasto = df_veiculos['Valor'].sum()
        
        # Gasto médio por veículo
        gasto_medio = df_veiculos.groupby('Veículos')['Valor'].sum().mean()
        
        # Quilometragem total (se existir)
        km_total = 0
        if 'KM' in df_veiculos.columns:
            # Pega a maior quilometragem para cada veículo
            km_total = df_veiculos.groupby('Veículos')['KM'].max().sum()
        
        # Custo por quilômetro
        custo_por_km = 0
        if km_total > 0:
            custo_por_km = total_gasto / km_total
        
        # Layout em colunas para métricas
        st.subheader("Métricas Gerais")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            create_metric_card(
                "Total Gasto", 
                total_gasto,
                is_currency=True
            )
        
        with col2:
            create_metric_card(
                "Gasto Médio por Veículo", 
                gasto_medio,
                is_currency=True
            )
        
        with col3:
            if 'KM' in df_veiculos.columns:
                create_metric_card(
                    "Quilometragem Total", 
                    km_total,
                    suffix=" km",
                    is_currency=False
                )
            else:
                st.info("Dados de quilometragem não disponíveis")
        
        with col4:
            if custo_por_km > 0:
                create_metric_card(
                    "Custo por KM", 
                    custo_por_km,
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
                df_categorias = df_veiculos.groupby('Categoria')['Valor'].sum().reset_index()
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
        
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        st.info(f"Verifique se os arquivos CSV para o ano {selected_year} estão disponíveis e formatados corretamente.")


if __name__ == "__main__":
    # Teste do componente
    veiculos_view() 