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
    plot_bar_chart, plot_pie_chart, format_table_currency
)
from config import COLORS, EXPENSE_TYPES

def gastos_gerais_view():
    """
    Componente de visualização de Gastos Gerais
    """
    st.header("📊 Gastos Gerais")
    
    # Seletor de ano
    available_years = [2023, 2024, 2025]
    selected_year = st.selectbox("Selecione o ano", available_years, index=1)  # 2024 como padrão
    
    try:
        # Carrega e processa os dados
        df = load_data(selected_year)
        df_processed = preprocess_financial_data(df)
        
        # Calcula métricas
        metrics = calculate_financial_metrics(df_processed)
        
        # Layout em colunas
        st.subheader("Métricas Financeiras")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            create_metric_card(
                "Despesa Total", 
                metrics.get('total_despesas', 0),
                is_currency=True
            )
        
        with col2:
            create_metric_card(
                "Despesas Fixas", 
                metrics.get('total_fixo', 0),
                delta=metrics.get('percentual_fixo', 0),
                is_currency=True,
                is_percentage=False
            )
        
        with col3:
            create_metric_card(
                "Despesas Variáveis", 
                metrics.get('total_variável', 0),
                delta=metrics.get('percentual_variável', 0),
                is_currency=True,
                is_percentage=False
            )
        
        with col4:
            create_metric_card(
                "Despesas Não Operacionais", 
                metrics.get('total_não operacional', 0),
                delta=metrics.get('percentual_não operacional', 0),
                is_currency=True,
                is_percentage=False
            )
        
        st.markdown("---")
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de barras por tipo de despesa
            st.subheader("Despesas por Tipo")
            
            # Prepara dados para o gráfico
            expense_by_type = []
            
            for tipo in EXPENSE_TYPES:
                tipo_lower = tipo.lower()
                expense_by_type.append({
                    "Tipo": tipo,
                    "Valor": metrics.get(f'total_{tipo_lower}', 0)
                })
            
            df_expense_by_type = pd.DataFrame(expense_by_type)
            
            # Cria gráfico
            if not df_expense_by_type.empty:
                fig = plot_bar_chart(
                    df_expense_by_type,
                    x="Tipo",
                    y="Valor",
                    title="Despesas por Tipo",
                    color="Tipo",
                    color_discrete_map={
                        "Fixo": COLORS["fixed"],
                        "Variável": COLORS["variable"],
                        "Não Operacional": COLORS["non_operational"]
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Sem dados suficientes para gerar o gráfico.")
        
        with col2:
            # Gráfico de pizza por categoria
            st.subheader("Despesas por Categoria")
            
            if 'Categoria' in df_processed.columns and 'Valor' in df_processed.columns:
                # Agrupa por categoria
                df_by_category = df_processed.groupby('Categoria')['Valor'].sum().reset_index()
                
                # Ordena e pega as top 5, o resto agrupado como "Outros"
                df_by_category = df_by_category.sort_values('Valor', ascending=False)
                
                if len(df_by_category) > 5:
                    top_df = df_by_category.head(5)
                    others_value = df_by_category.iloc[5:]['Valor'].sum()
                    others_df = pd.DataFrame({'Categoria': ['Outros'], 'Valor': [others_value]})
                    df_by_category = pd.concat([top_df, others_df], ignore_index=True)
                
                # Cria gráfico
                fig = plot_pie_chart(
                    df_by_category,
                    values="Valor",
                    names="Categoria",
                    title="Distribuição por Categoria",
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Dados insuficientes para gerar o gráfico de categorias.")
        
        # Tabela detalhada
        st.subheader("Tabela Detalhada de Despesas")
        
        if 'Tipo' in df_processed.columns and 'Categoria' in df_processed.columns and 'Valor' in df_processed.columns:
            # Agrupa dados por tipo e categoria
            df_table = df_processed.groupby(['Tipo', 'Categoria'])['Valor'].sum().reset_index()
            
            # Ordena por tipo e valor
            df_table = df_table.sort_values(['Tipo', 'Valor'], ascending=[True, False])
            
            # Formata valores como moeda
            df_table_formatted = format_table_currency(df_table, ['Valor'])
            
            # Mostra tabela
            st.dataframe(
                df_table_formatted,
                column_config={
                    "Tipo": st.column_config.TextColumn("Tipo de Despesa"),
                    "Categoria": st.column_config.TextColumn("Categoria"),
                    "Valor": st.column_config.TextColumn("Valor (R$)")
                },
                use_container_width=True
            )
        else:
            st.warning("Dados insuficientes para gerar a tabela detalhada.")
        
        # Análise mensal se houver dados de mês
        if 'Mes' in df_processed.columns and 'Valor' in df_processed.columns:
            st.subheader("Análise Mensal")
            
            # Agrupa por mês
            monthly_data = df_processed.groupby('Mes')['Valor'].sum().reset_index()
            
            # Adiciona nome do mês
            months_names = {
                1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 
                5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
                9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
            }
            monthly_data['Mes_Nome'] = monthly_data['Mes'].map(months_names)
            
            # Gráfico
            fig = plot_bar_chart(
                monthly_data,
                x="Mes_Nome",
                y="Valor",
                title=f"Despesas Mensais - {selected_year}",
                color_discrete_sequence=[COLORS["primary"]]
            )
            st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        st.info(f"Verifique se os arquivos CSV para o ano {selected_year} estão disponíveis e formatados corretamente.")

if __name__ == "__main__":
    # Teste do componente
    gastos_gerais_view() 