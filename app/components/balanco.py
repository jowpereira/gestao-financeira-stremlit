import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Adiciona diretórios ao path para importar módulos
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "utils"))

from utils.data_loader import load_data, get_available_years
from utils.preprocessing import preprocess_financial_data, calculate_financial_metrics
from utils.styling import (
    format_currency, format_percentage, create_metric_card,
    plot_bar_chart, plot_pie_chart, format_table_currency
)
from config import COLORS

def balanco_view():
    """
    Componente de visualização de Balanço Financeiro para a diretoria.
    A implementação normaliza os nomes das colunas, aplica a regra de
    classificação dos valores na coluna GASTOS (receita x gastos) e exibe
    diversas métricas e gráficos.
    """
    # Seletor de ano com ordenação
    available_years = get_available_years()
    try:
        available_years_sorted = sorted(available_years, key=lambda y: int(y))
    except Exception:
        available_years_sorted = sorted(available_years)
    selected_year = st.selectbox("Selecione o ano", available_years_sorted, index=min(1, len(available_years_sorted)-1))
    
    try:
        # --- Dados do Ano Selecionado ---
        df = load_data(selected_year)
        df_processed = preprocess_financial_data(df)
        # Normaliza os nomes das colunas para maiúsculas
        df_processed.columns = df_processed.columns.str.upper()
        
        # Converte a coluna GASTOS para numérico, se existir
        if 'GASTOS' in df_processed.columns:
            df_processed['GASTOS'] = pd.to_numeric(df_processed['GASTOS'], errors='coerce').fillna(0)
        
        # Aplica a regra: se TIPO estiver em tipos_receita, considera GASTOS como RECEITA; caso contrário, como VALOR (gasto)
        tipos_receita = ['Entrada Não Operacional', 'Receita', 'Medição']
        if 'GASTOS' in df_processed.columns and 'TIPO' in df_processed.columns:
            df_processed['RECEITA'] = np.where(df_processed['TIPO'].isin(tipos_receita), df_processed['GASTOS'], 0)
            df_processed['VALOR'] = np.where(~df_processed['TIPO'].isin(tipos_receita), df_processed['GASTOS'], 0)
        else:
            if 'RECEITA' not in df_processed.columns:
                df_processed['RECEITA'] = 0
        
        # Garante que as colunas RECEITA e VALOR sejam numéricas
        df_processed['RECEITA'] = pd.to_numeric(df_processed['RECEITA'], errors='coerce').fillna(0)
        df_processed['VALOR'] = pd.to_numeric(df_processed['VALOR'], errors='coerce').fillna(0)
        
        # --- Cálculo das Métricas Principais ---
        total_receitas = df_processed['RECEITA'].sum()
        total_despesas = df_processed['VALOR'].sum()
        balanco = total_receitas - total_despesas
        margem = (balanco / total_receitas * 100) if total_receitas > 0 else 0

        # --- Cards de Resumo Financeiro ---
        st.subheader("Resumo Financeiro")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            create_metric_card("Receitas Totais", total_receitas, is_currency=True)
        with col2:
            create_metric_card("Despesas Totais", total_despesas, is_currency=True)
        with col3:
            create_metric_card("Balanço", balanco, is_currency=True)
        with col4:
            create_metric_card("Margem de Lucro", margem, is_percentage=True)
        
        # --- Crescimento Comparativo ---
        growth_receitas, growth_despesas, growth_balanco = None, None, None
        if len(available_years_sorted) > 1:
            current_index = available_years_sorted.index(selected_year)
            if current_index > 0:
                previous_year = available_years_sorted[current_index - 1]
                df_prev = load_data(previous_year)
                df_prev_processed = preprocess_financial_data(df_prev)
                df_prev_processed.columns = df_prev_processed.columns.str.upper()
                if 'GASTOS' in df_prev_processed.columns:
                    df_prev_processed['GASTOS'] = pd.to_numeric(df_prev_processed['GASTOS'], errors='coerce').fillna(0)
                if 'GASTOS' in df_prev_processed.columns and 'TIPO' in df_prev_processed.columns:
                    df_prev_processed['RECEITA'] = np.where(df_prev_processed['TIPO'].isin(tipos_receita), df_prev_processed['GASTOS'], 0)
                    df_prev_processed['VALOR'] = np.where(~df_prev_processed['TIPO'].isin(tipos_receita), df_prev_processed['GASTOS'], 0)
                else:
                    if 'RECEITA' not in df_prev_processed.columns:
                        df_prev_processed['RECEITA'] = 0
                df_prev_processed['RECEITA'] = pd.to_numeric(df_prev_processed['RECEITA'], errors='coerce').fillna(0)
                df_prev_processed['VALOR'] = pd.to_numeric(df_prev_processed['VALOR'], errors='coerce').fillna(0)
                total_receitas_prev = df_prev_processed['RECEITA'].sum()
                total_despesas_prev = df_prev_processed['VALOR'].sum()
                balanco_prev = total_receitas_prev - total_despesas_prev
                
                if total_receitas_prev > 0:
                    growth_receitas = ((total_receitas - total_receitas_prev) / total_receitas_prev) * 100
                if total_despesas_prev > 0:
                    growth_despesas = ((total_despesas - total_despesas_prev) / total_despesas_prev) * 100
                if balanco_prev != 0:
                    growth_balanco = ((balanco - balanco_prev) / abs(balanco_prev)) * 100
        
        if any(val is not None for val in [growth_receitas, growth_despesas, growth_balanco]):
            st.subheader("Crescimento Comparativo (em relação ao ano anterior)")
            col_growth1, col_growth2, col_growth3 = st.columns(3)
            with col_growth1:
                create_metric_card("Crescimento de Receita", growth_receitas, is_percentage=True)
            with col_growth2:
                create_metric_card("Crescimento de Despesa", growth_despesas, is_percentage=True)
            with col_growth3:
                create_metric_card("Crescimento do Balanço", growth_balanco, is_percentage=True)
        
        st.markdown("---")
        
        # --- Gráfico de Receitas vs Despesas ---
        st.subheader("Receitas vs Despesas")
        df_balanco_chart = pd.DataFrame([
            {"Tipo": "Receitas", "Valor": total_receitas},
            {"Tipo": "Despesas", "Valor": total_despesas}
        ])
        fig = plot_bar_chart(
            df_balanco_chart,
            x="Tipo",
            y="Valor",
            title=f"Receitas vs Despesas - {selected_year}",
            color="Tipo",
            color_discrete_map={"Receitas": COLORS["secondary"], "Despesas": COLORS["primary"]}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # --- Análise Mensal ---
        if 'MES' in df_processed.columns:
            st.subheader("Análise Mensal")
            # Garante que a coluna MES seja tratada como string
            df_processed['MES'] = df_processed['MES'].astype(str)
            meses_abrev = {
                'jan': 'Jan', 'fev': 'Fev', 'mar': 'Mar', 'abr': 'Abr',
                'mai': 'Mai', 'jun': 'Jun', 'jul': 'Jul', 'ago': 'Ago',
                'set': 'Set', 'out': 'Out', 'nov': 'Nov', 'dez': 'Dez'
            }
            df_processed['MES_ABREV'] = df_processed['MES'].str[:3].str.lower().map(meses_abrev)
            
            # Agrega receitas e despesas por mês
            receitas_mensais = df_processed.groupby('MES_ABREV')['RECEITA'].sum().reset_index()
            receitas_mensais['TIPO_DADO'] = 'Receitas'
            receitas_mensais = receitas_mensais.rename(columns={'RECEITA': 'VALOR'})
            despesas_mensais = df_processed.groupby('MES_ABREV')['VALOR'].sum().reset_index()
            despesas_mensais['TIPO_DADO'] = 'Despesas'
            df_mensal = pd.concat([receitas_mensais, despesas_mensais], ignore_index=True)
            
            month_order = {'Jan': 1, 'Fev': 2, 'Mar': 3, 'Abr': 4, 'Mai': 5, 'Jun': 6,
                           'Jul': 7, 'Ago': 8, 'Set': 9, 'Out': 10, 'Nov': 11, 'Dez': 12}
            df_mensal['MES_NUM'] = df_mensal['MES_ABREV'].map(month_order)
            df_mensal = df_mensal.sort_values('MES_NUM')
            
            fig = plot_bar_chart(
                df_mensal,
                x="MES_ABREV",
                y="VALOR",
                color="TIPO_DADO",
                title=f"Receitas vs Despesas por Mês - {selected_year}",
                barmode="group",
                color_discrete_map={"Receitas": COLORS["secondary"], "Despesas": COLORS["primary"]}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("Balanço Mensal")
            pivot_mensal = df_mensal.pivot_table(
                values='VALOR',
                index='MES_NUM',
                columns='TIPO_DADO'
            ).reset_index()
            pivot_mensal['BALANCO'] = pivot_mensal.get('Receitas', 0) - pivot_mensal.get('Despesas', 0)
            pivot_mensal['MARGEM (%)'] = pivot_mensal.apply(
                lambda row: (row['BALANCO'] / row['Receitas'] * 100) if row.get('Receitas', 0) > 0 else 0,
                axis=1
            )
            pivot_mensal['MES'] = pivot_mensal['MES_NUM'].map({v: k for k, v in month_order.items()})
            pivot_mensal = pivot_mensal.sort_values('MES_NUM')
            pivot_mensal = pivot_mensal[['MES', 'Receitas', 'Despesas', 'BALANCO', 'MARGEM (%)']]
            
            pivot_formatado = pivot_mensal.copy()
            pivot_formatado['Receitas'] = pivot_formatado['Receitas'].apply(lambda x: format_currency(x))
            pivot_formatado['Despesas'] = pivot_formatado['Despesas'].apply(lambda x: format_currency(x))
            pivot_formatado['BALANCO'] = pivot_formatado['BALANCO'].apply(lambda x: format_currency(x))
            pivot_formatado['MARGEM (%)'] = pivot_formatado['MARGEM (%)'].apply(lambda x: format_percentage(x))
            st.dataframe(pivot_formatado, use_container_width=True)
            
            import plotly.graph_objects as go
            df_balanco_mensal = pivot_mensal.copy()
            df_balanco_mensal['COR'] = df_balanco_mensal['BALANCO'].apply(
                lambda x: COLORS["secondary"] if x >= 0 else COLORS["danger"]
            )
            fig = go.Figure()
            fig.add_trace(
                go.Bar(
                    x=df_balanco_mensal['MES'],
                    y=df_balanco_mensal['BALANCO'],
                    name='Balanço',
                    marker_color=df_balanco_mensal['COR']
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=df_balanco_mensal['MES'],
                    y=df_balanco_mensal['MARGEM (%)'],
                    name='Margem (%)',
                    yaxis='y2',
                    line=dict(color=COLORS["info"], width=3),
                    mode='lines+markers'
                )
            )
            fig.update_layout(
                title=f"Balanço e Margem Mensal - {selected_year}",
                xaxis=dict(title="Mês"),
                yaxis=dict(title="Balanço", tickprefix="R$ "),
                yaxis2=dict(title="Margem (%)", ticksuffix="%", overlaying="y", side="right"),
                legend=dict(x=0.01, y=0.99),
                margin=dict(l=50, r=50, t=80, b=50),
                height=500,
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # --- Fontes de Receita ---
        if 'TIPO' in df_processed.columns:
            st.subheader("Fontes de Receita")
            df_receitas = df_processed.groupby('TIPO')['RECEITA'].sum().reset_index()
            df_receitas = df_receitas.sort_values('RECEITA', ascending=False)
            
            col1, col2 = st.columns(2)
            with col1:
                fig = plot_pie_chart(
                    df_receitas,
                    values="RECEITA",
                    names="TIPO",
                    title="Distribuição das Fontes de Receita"
                )
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                df_receitas_formatado = df_receitas.copy()
                df_receitas_formatado['PERCENTUAL'] = (df_receitas_formatado['RECEITA'] / total_receitas * 100) if total_receitas > 0 else 0
                df_receitas_formatado['RECEITA'] = df_receitas_formatado['RECEITA'].apply(lambda x: format_currency(x))
                df_receitas_formatado['PERCENTUAL'] = df_receitas_formatado['PERCENTUAL'].apply(lambda x: format_percentage(x))
                df_receitas_formatado = df_receitas_formatado.rename(columns={
                    'TIPO': 'FONTE DE RECEITA',
                    'PERCENTUAL': 'Participação (%)'
                })
                st.dataframe(df_receitas_formatado, use_container_width=True)
        
        # --- Indicadores Financeiros Adicionais ---
        st.subheader("Indicadores Financeiros")
        metrics = calculate_financial_metrics(df_processed)
        percentual_fixas = metrics.get('percentual_fixo', 0)
        indice_liquidez = total_receitas / total_despesas if total_despesas > 0 else 0
        despesas_fixas = metrics.get('total_fixo', 0)
        despesas_variaveis = metrics.get('total_variável', 0)
        margem_contribuicao = 1 - (despesas_variaveis / total_receitas) if total_receitas > 0 else 0
        ponto_equilibrio = despesas_fixas / margem_contribuicao if margem_contribuicao > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            create_metric_card("Despesas Fixas", percentual_fixas, suffix=" %", is_percentage=True)
        with col2:
            create_metric_card("Índice de Liquidez", indice_liquidez, prefix="", suffix=" x")
        with col3:
            create_metric_card("Margem de Contribuição", margem_contribuicao * 100, is_percentage=True)
        with col4:
            create_metric_card("Ponto de Equilíbrio", ponto_equilibrio, is_currency=True)
    
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        st.info(f"Verifique se os arquivos CSV para o ano {selected_year} estão disponíveis e formatados corretamente.")

if __name__ == "__main__":
    balanco_view()
