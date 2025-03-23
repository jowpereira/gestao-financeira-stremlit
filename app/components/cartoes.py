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

# Add these month mappings at the top of the file after imports
MONTH_MAP = {
    'January': 'Janeiro',
    'February': 'Fevereiro',
    'March': 'Março',
    'April': 'Abril',
    'May': 'Maio',
    'June': 'Junho',
    'July': 'Julho',
    'August': 'Agosto',
    'September': 'Setembro',
    'October': 'Outubro',
    'November': 'Novembro',
    'December': 'Dezembro'
}

def validate_cartoes_data(df):
    """Validates corporate card data requirements"""
    required_columns = ['Usuário', 'Conta', 'Valor', 'Data']
    missing = [col for col in required_columns if col not in df.columns]
    
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(missing)}")
    
    if df.empty:
        raise ValueError("Dataset está vazio")
        
    return True

def cartoes_view():
    """
    Componente de visualização de Cartões Corporativos
    """
    st.header("💳 Cartões Corporativos")
    
    # Seletor de ano
    available_years = [2023, 2024, 2025]
    selected_year = st.selectbox("Selecione o ano", available_years, index=1)  # 2024 como padrão
    
    try:
        # Carrega e processa os dados
        df = load_data(selected_year)
        df_processed = preprocess_financial_data(df)
        
        # Add validation
        if not validate_cartoes_data(df_processed):
            return
        
        # Verifica se há dados de cartões (coluna Conta)
        if 'Usuário' not in df_processed.columns or 'Conta' not in df_processed.columns:
            st.warning("Este conjunto de dados não contém informações de cartões corporativos.")
            return
        
        # Função para verificar se o valor é numérico
        def is_numeric(val):
            try:
                # Tenta converter para float e verifica se é um número
                float(val)
                return True
            except (ValueError, TypeError):
                return False
        
        # Filtra apenas despesas com cartões (valores numéricos na coluna 'Conta')
        df_cartoes = df_processed[df_processed['Conta'].apply(is_numeric)]
        
        if df_cartoes.empty:
            st.warning("Não há registros de cartões corporativos para este ano.")
            return
        
        # Obtém lista de funcionários
        usuarios = df_cartoes['Usuário'].unique().tolist()
        
        # Layout em colunas para filtros
        col1, col2 = st.columns(2)
        
        with col1:
            # Filtro de funcionário
            if len(usuarios) > 1:
                selected_usuario = st.multiselect(
                    "Filtrar por funcionário:",
                    options=["Todos"] + usuarios,
                    default=["Todos"]
                )
            else:
                selected_usuario = usuarios
        
        with col2:
            # Verifica qual coluna usar para meses (Mes ou Mês Ano)
            mes_column = 'Mês Ano' if 'Mês Ano' in df_cartoes.columns else 'Mes'
            
            if mes_column in df_cartoes.columns:
                # Extrai o mês de 'Mês Ano' se necessário
                if mes_column == 'Mês Ano':
                    # Supondo que 'Mês Ano' seja algo como "Janeiro 2024"
                    df_cartoes['Mes'] = df_cartoes[mes_column].apply(
                        lambda x: MONTHS.index(MONTH_MAP.get(x.split()[0], x.split()[0])) + 1 
                        if isinstance(x, str) and ' ' in x else 0
                    )
                
                months_in_data = sorted(df_cartoes['Mes'].unique().tolist())
                month_names = [MONTHS[m-1] for m in months_in_data if 1 <= m <= 12]
                
                selected_month = st.multiselect(
                    "Filtrar por mês:",
                    options=["Todos"] + month_names,
                    default=["Todos"]
                )
            else:
                st.warning("Dados de mês não disponíveis para filtragem.")
                selected_month = ["Todos"]
        
        # Aplicar filtros
        if "Todos" not in selected_usuario:
            df_cartoes = df_cartoes[df_cartoes['Usuário'].isin(selected_usuario)]
        
        if "Todos" not in selected_month and 'Mes' in df_cartoes.columns:
            # Converte nomes dos meses para números
            month_numbers = [
                MONTHS.index(MONTH_MAP.get(m, m)) + 1 
                for m in selected_month if m != "Todos"
            ]
            df_cartoes = df_cartoes[df_cartoes['Mes'].isin(month_numbers)]
        
        # Métricas
        st.subheader("Métricas de Cartões Corporativos")
        
        # Calcula métricas de cartões
        total_gasto = df_cartoes['Valor'].sum()
        media_por_cartao = df_cartoes.groupby('Usuário')['Valor'].sum().mean()
        total_transacoes = len(df_cartoes)
        valor_medio_transacao = total_gasto / total_transacoes if total_transacoes > 0 else 0
        
        # Exibe métricas em cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            create_metric_card(
                "Total Gasto", 
                total_gasto,
                is_currency=True
            )
        
        with col2:
            create_metric_card(
                "Média por Funcionário", 
                media_por_cartao,
                is_currency=True
            )
        
        with col3:
            create_metric_card(
                "Total de Transações", 
                total_transacoes,
                is_currency=False
            )
        
        with col4:
            create_metric_card(
                "Valor Médio por Transação", 
                valor_medio_transacao,
                is_currency=True
            )
        
        st.markdown("---")
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de gastos por funcionário
            st.subheader("Gastos por Funcionário")
            
            df_por_Usuário = df_cartoes.groupby('Usuário')['Valor'].sum().reset_index()
            df_por_Usuário = df_por_Usuário.sort_values('Valor', ascending=False)
            
            fig = plot_bar_chart(
                df_por_Usuário,
                x="Usuário",
                y="Valor",
                title="Gastos Totais por Funcionário",
                color_discrete_sequence=[COLORS["primary"]]
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Gráfico de categorias por cartão
            st.subheader("Distribuição por Categoria")
            
            if 'Categoria' in df_cartoes.columns:
                df_categorias = df_cartoes.groupby('Categoria')['Valor'].sum().reset_index()
                df_categorias = df_categorias.sort_values('Valor', ascending=False)
                
                # Limitando para top 5 + Outros
                if len(df_categorias) > 5:
                    top5 = df_categorias.head(5)
                    outros_valor = df_categorias.iloc[5:]['Valor'].sum()
                    outros = pd.DataFrame({'Categoria': ['Outros'], 'Valor': [outros_valor]})
                    df_categorias = pd.concat([top5, outros], ignore_index=True)
                
                fig = plot_pie_chart(
                    df_categorias,
                    values="Valor",
                    names="Categoria",
                    title="Gastos por Categoria"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Dados de categoria não disponíveis.")
        
        # Gráfico de evolução mensal
        st.subheader("Evolução de Gastos Mensais")
        
        if 'Mes' in df_cartoes.columns:
            # Add transaction count to monthly analysis
            df_mensal = df_cartoes.groupby('Mes').agg({
                'Valor': 'sum',
                'Usuário': 'count'  # Counts transactions
            }).reset_index()
            
            df_mensal = df_mensal.rename(columns={'Usuário': 'Transações'})
            df_mensal['Mes_Nome'] = df_mensal['Mes'].apply(
                lambda x: MONTHS[x-1] if 1 <= x <= 12 else f'Mês {x}'
            )
            
            # Create two charts in columns
            col1, col2 = st.columns(2)
            
            with col1:
                # Existing spending chart
                fig_valor = plot_line_chart(
                    df_mensal,
                    x="Mes_Nome",
                    y="Valor",
                    title=f"Gastos Mensais - {selected_year}",
                    markers=True,
                    color_discrete_sequence=[COLORS["primary"]]
                )
                st.plotly_chart(fig_valor, use_container_width=True)
                
            with col2:
                # New transactions count chart
                fig_trans = plot_line_chart(
                    df_mensal,
                    x="Mes_Nome",
                    y="Transações",
                    title=f"Quantidade de Transações - {selected_year}",
                    markers=True,
                    color_discrete_sequence=[COLORS.get("secondary", "#ff7f0e")]  # Uses fallback color if not found
                )
                st.plotly_chart(fig_trans, use_container_width=True)
        
        # Tabela detalhada de transações
        st.subheader("Transações Detalhadas")
        
        # Colunas a serem exibidas na tabela
        display_columns = ['Data', 'Usuário', 'Categoria', 'Valor', 'Descrição']
        columns_to_show = [col for col in display_columns if col in df_cartoes.columns]
        
        # Ordenação da tabela
        df_table = df_cartoes[columns_to_show].sort_values('Data', ascending=False)
        
        # Formata valores monetários
        if 'Valor' in columns_to_show:
            df_table = format_table_currency(df_table, ['Valor'])
        
        # Exibe tabela com paginação
        st.dataframe(
            df_table,
            use_container_width=True
        )
        
        # Add export button
        if not df_table.empty:
            csv = df_table.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Exportar Transações",
                csv,
                f"transacoes_cartao_{selected_year}.csv",
                "text/csv",
                key='download-csv'
            )
        
        # Gráfico de análise comparativa
        if len(usuarios) > 1 and 'Categoria' in df_cartoes.columns:
            st.subheader("Análise Comparativa por Funcionário")
            
            # Top 3 categorias
            top_categorias = df_cartoes.groupby('Categoria')['Valor'].sum().nlargest(3).index.tolist()
            
            # Filtra apenas as top categorias
            df_top_categorias = df_cartoes[df_cartoes['Categoria'].isin(top_categorias)]
            
            # Agrupa por funcionário e categoria
            df_Usuário_categoria = df_top_categorias.groupby(['Usuário', 'Categoria'])['Valor'].sum().reset_index()
            
            # Cria gráfico
            fig = plot_bar_chart(
                df_Usuário_categoria,
                x="Usuário",
                y="Valor",
                color="Categoria",
                title="Comparativo de Principais Categorias por Funcionário",
                barmode="group"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Relatório de auditoria
        st.subheader("Relatório de Auditoria")
        
        # Identifica transações atípicas (acima de 2 desvios padrão)
        media = df_cartoes['Valor'].mean()
        desvio = df_cartoes['Valor'].std()
        limite = media + 2 * desvio
        
        df_atipicas = df_cartoes[df_cartoes['Valor'] > limite]
        
        if not df_atipicas.empty:
            st.warning(f"Foram identificadas {len(df_atipicas)} transações com valores atípicos (acima de {format_currency(limite)}).")
            
            # Formata valores monetários
            df_atipicas_formatada = format_table_currency(
                df_atipicas[columns_to_show].sort_values('Valor', ascending=False),
                ['Valor']
            )
            
            # Exibe transações atípicas
            st.dataframe(
                df_atipicas_formatada,
                use_container_width=True
            )
        else:
            st.success("Não foram identificadas transações com valores atípicos.")
        
        st.write("Colunas disponíveis:", df_processed.columns.tolist())
    
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        st.info(f"Verifique se os arquivos CSV para o ano {selected_year} estão disponíveis e formatados corretamente.")

if __name__ == "__main__":
    # Teste do componente
    cartoes_view()