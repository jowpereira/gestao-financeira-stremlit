import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Adiciona diretórios ao path para importar módulos
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "utils"))

from utils.data_loader import load_data, load_all_data, get_available_years
from utils.preprocessing import preprocess_financial_data, calculate_financial_metrics
from utils.styling import (
    format_currency, format_percentage, create_metric_card,
    plot_bar_chart, plot_pie_chart, plot_line_chart, format_table_currency
)
from config import COLORS, EXPENSE_TYPES

def comparativo_anual_view():
    """
    Componente de visualização de Comparativo Anual
    """
    st.header("📅 Comparativo Anual")
    
    # Obtém anos disponíveis
    available_years = get_available_years()
    
    if len(available_years) < 2:
        st.warning("É necessário ter dados de pelo menos dois anos para realizar comparativos.")
        return
    
    try:
        # Carrega todos os dados disponíveis
        df_all = load_all_data()
        df_processed = preprocess_financial_data(df_all)
        
        # Seletor de anos para comparação
        selected_years = st.multiselect(
            "Selecione os anos para comparação:",
            options=available_years,
            default=available_years[:2]  # Selecionando os dois primeiros anos por padrão
        )
        
        if len(selected_years) < 2:
            st.warning("Selecione pelo menos dois anos para comparação.")
            return
        
        # Filtra dados pelos anos selecionados
        df_selected = df_processed[df_processed['Ano'].isin(selected_years)]
        
        # Cálculo de métricas para cada ano
        metrics_by_year = {}
        for year in selected_years:
            df_year = df_processed[df_processed['Ano'] == year]
            metrics_by_year[year] = calculate_financial_metrics(df_year)
        
        # Comparativo de despesas totais por ano
        st.subheader("Despesas Totais por Ano")
        
        # Prepara dados para o gráfico
        total_despesas = []
        
        for year in selected_years:
            total_despesas.append({
                "Ano": str(year),
                "Valor": metrics_by_year[year].get('total_despesas', 0)
            })
        
        df_total_despesas = pd.DataFrame(total_despesas)
        
        # Cria gráfico
        fig = plot_bar_chart(
            df_total_despesas,
            x="Ano",
            y="Valor",
            title="Despesas Totais por Ano",
            color_discrete_sequence=[COLORS["primary"]]
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabela comparativa
        st.subheader("Tabela Comparativa")
        
        # Prepara dados para a tabela
        comparativo_data = []
        
        # Adiciona despesas totais
        row_total = {"Métrica": "Despesa Total"}
        for year in selected_years:
            row_total[str(year)] = metrics_by_year[year].get('total_despesas', 0)
        comparativo_data.append(row_total)
        
        # Adiciona despesas por tipo
        for tipo in EXPENSE_TYPES:
            tipo_lower = tipo.lower()
            row_tipo = {"Métrica": f"Despesas {tipo}"}
            for year in selected_years:
                row_tipo[str(year)] = metrics_by_year[year].get(f'total_{tipo_lower}', 0)
            comparativo_data.append(row_tipo)
        
        # Adiciona percentuais por tipo
        for tipo in EXPENSE_TYPES:
            tipo_lower = tipo.lower()
            row_percentual = {"Métrica": f"% {tipo}"}
            for year in selected_years:
                row_percentual[str(year)] = metrics_by_year[year].get(f'percentual_{tipo_lower}', 0)
            comparativo_data.append(row_percentual)
        
        # Cria dataframe da tabela
        df_comparativo = pd.DataFrame(comparativo_data)
        
        # Formata valores monetários
        year_columns = [str(year) for year in selected_years]
        
        # Cria uma cópia formatada
        df_formatado = df_comparativo.copy()
        
        # Formata valores
        for idx, row in df_formatado.iterrows():
            if "%" in row["Métrica"]:
                # Formata percentuais
                for year in year_columns:
                    df_formatado.at[idx, year] = format_percentage(row[year])
            else:
                # Formata valores monetários
                for year in year_columns:
                    df_formatado.at[idx, year] = format_currency(row[year])
        
        # Exibe tabela
        st.dataframe(
            df_formatado,
            use_container_width=True
        )
        
        # Comparativo por Categoria
        st.subheader("Comparativo por Categoria")
        
        # Obtém lista de categorias
        if 'Categoria' in df_selected.columns:
            categorias = df_selected['Categoria'].unique().tolist()
            
            # Seletor de categorias
            selected_categorias = st.multiselect(
                "Selecione as categorias para analisar:",
                options=categorias,
                default=categorias[:5] if len(categorias) > 5 else categorias  # Seleciona até 5 categorias por padrão
            )
            
            if selected_categorias:
                # Filtra dados pelas categorias selecionadas
                df_categorias = df_selected[df_selected['Categoria'].isin(selected_categorias)]
                
                # Agrupa por ano e categoria
                df_ano_categoria = df_categorias.groupby(['Ano', 'Categoria'])['Valor'].sum().reset_index()
                
                # Converte ano para string para o gráfico
                df_ano_categoria['Ano'] = df_ano_categoria['Ano'].astype(str)
                
                # Cria gráfico
                fig = plot_bar_chart(
                    df_ano_categoria,
                    x="Categoria",
                    y="Valor",
                    color="Ano",
                    title="Despesas por Categoria e Ano",
                    barmode="group"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Análise de variação percentual
                st.subheader("Variação Percentual entre Anos")
                
                # Calcula variação percentual para cada categoria
                df_pivot = df_ano_categoria.pivot(index='Categoria', columns='Ano', values='Valor').reset_index()
                
                # Cria colunas de variação
                for i in range(1, len(selected_years)):
                    ano_anterior = str(selected_years[i-1])
                    ano_atual = str(selected_years[i])
                    
                    # Nome da coluna de variação
                    var_col = f"Var {ano_anterior}-{ano_atual}"
                    
                    # Calcula variação percentual
                    df_pivot[var_col] = ((df_pivot[ano_atual] - df_pivot[ano_anterior]) / df_pivot[ano_anterior]) * 100
                
                # Formata valores
                df_pivot_formatado = df_pivot.copy()
                
                # Formata colunas de valor
                for year in [str(year) for year in selected_years]:
                    df_pivot_formatado[year] = df_pivot_formatado[year].apply(lambda x: format_currency(x))
                
                # Formata colunas de variação
                for i in range(1, len(selected_years)):
                    ano_anterior = str(selected_years[i-1])
                    ano_atual = str(selected_years[i])
                    var_col = f"Var {ano_anterior}-{ano_atual}"
                    
                    # Aplica formatação e indicadores
                    df_pivot_formatado[var_col] = df_pivot[var_col].apply(
                        lambda x: f"↑ {format_percentage(x)}" if x > 0 else 
                                 (f"↓ {format_percentage(abs(x))}" if x < 0 else "→ 0,00%")
                    )
                
                # Exibe tabela
                st.dataframe(
                    df_pivot_formatado,
                    use_container_width=True
                )
                
                # Gráfico de evolução por categoria
                st.subheader("Evolução por Categoria")
                
                # Prepara dados para o gráfico
                df_pivot_melt = pd.melt(
                    df_pivot,
                    id_vars=['Categoria'],
                    value_vars=[str(year) for year in selected_years],
                    var_name='Ano',
                    value_name='Valor'
                )
                
                # Cria gráfico de linha
                fig = plot_line_chart(
                    df_pivot_melt,
                    x="Ano",
                    y="Valor",
                    color="Categoria",
                    title="Evolução de Despesas por Categoria",
                    markers=True
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Dados de categoria não disponíveis para comparativo.")
        
        # Comparativo de despesas mensais
        if 'Mes' in df_selected.columns:
            st.subheader("Comparativo Mensal")
            
            # Agrupa por ano e mês
            df_mensal = df_selected.groupby(['Ano', 'Mes'])['Valor'].sum().reset_index()
            
            # Adiciona nome do mês
            meses = {
                1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 
                5: 'Mai', 6: 'Jun', 7: 'Jul', 8: 'Ago',
                9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
            }
            df_mensal['Mes_Nome'] = df_mensal['Mes'].map(meses)
            
            # Converte ano para string
            df_mensal['Ano'] = df_mensal['Ano'].astype(str)
            
            # Ordena por mês
            df_mensal = df_mensal.sort_values(['Ano', 'Mes'])
            
            # Cria gráfico
            fig = plot_line_chart(
                df_mensal,
                x="Mes_Nome",
                y="Valor",
                color="Ano",
                title="Comparativo de Despesas Mensais",
                markers=True
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Cria heatmap para análise de sazonalidade
            st.subheader("Análise de Sazonalidade")
            
            # Prepara dados para heatmap
            df_heatmap = df_mensal.pivot(index='Mes_Nome', columns='Ano', values='Valor')
            
            # Reordena os meses
            mes_ordem = [meses[i] for i in range(1, 13)]
            df_heatmap = df_heatmap.reindex(mes_ordem)
            
            # Cria heatmap usando Plotly
            import plotly.figure_factory as ff
            
            # Formata valores para o heatmap
            z = df_heatmap.values
            x = df_heatmap.columns.tolist()
            y = df_heatmap.index.tolist()
            
            # Formata valores para exibição no hover
            text = [[format_currency(val) for val in row] for row in z]
            
            # Cria figura
            fig = ff.create_annotated_heatmap(
                z=z,
                x=x,
                y=y,
                annotation_text=text,
                colorscale='Blues',
                showscale=True
            )
            
            # Atualiza layout
            fig.update_layout(
                title="Heatmap de Despesas Mensais por Ano",
                xaxis=dict(title="Ano"),
                yaxis=dict(title="Mês", categoryorder='array', categoryarray=mes_ordem),
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        st.info("Verifique se os arquivos CSV estão disponíveis e formatados corretamente.")

if __name__ == "__main__":
    # Teste do componente
    comparativo_anual_view() 