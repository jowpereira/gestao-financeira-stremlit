
import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "utils"))

from utils.data_loader import load_data, get_available_years
from utils.preprocessing import preprocess_financial_data, calculate_financial_metrics
from utils.styling import (
    format_currency, format_percentage, create_metric_card,
    plot_bar_chart, plot_pie_chart, format_table_currency
)
from config import COLORS

EXPENSE_TYPES = [
    "Fixo",
    "Investimento",
    "Saída Não Operacional",
    "Variável",
    "TH Parfum"
]

def balanco_view():
    st.header("📊 Balanço Financeiro")

    anos = sorted(get_available_years(), key=lambda x: int(x))
    ano = st.selectbox("🗓️ Selecione o ano", anos, index=min(1, len(anos)-1))

    try:
        df = preprocess_financial_data(load_data(ano))

        if 'Conta' not in df.columns or 'Valor' not in df.columns:
            st.error("Colunas obrigatórias ausentes: Conta, Valor")
            return

        df['Conta'] = df['Conta'].astype(str).str.strip().str.title()
        df['GASTOS'] = df['GASTOS'].astype(str).str.strip().str.title()

        df['Receita'] = np.where(df['Conta'].str.contains("Medição", case=False, na=False), df['Valor'], 0)
        df['Valor'] = np.where(~df['Conta'].str.contains("Medição", case=False, na=False), df['Valor'], 0)

        df['Receita'] = pd.to_numeric(df['Receita'], errors='coerce').fillna(0)
        df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce').fillna(0)

        total_receitas = df['Receita'].sum()
        df_despesas = df[df['GASTOS'].isin(EXPENSE_TYPES)]
        total_despesas = df_despesas['Valor'].sum()
        balanco = total_receitas - total_despesas
        margem_lucro = (balanco / total_receitas * 100) if total_receitas > 0 else 0

        despesas_fixas = df_despesas[df_despesas['GASTOS'] == "Fixo"]['Valor'].sum()
        despesas_variaveis = df_despesas[df_despesas['GASTOS'] == "Variável"]['Valor'].sum()

        margem_contrib = (total_receitas - despesas_variaveis) / total_receitas if total_receitas > 0 else 0
        ponto_eq = despesas_fixas / margem_contrib if margem_contrib > 0 else 0

        st.markdown("## 📌 Resumo Financeiro")
        st.divider()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            create_metric_card("✅ Receitas Totais", total_receitas, is_currency=True)
        with col2:
            create_metric_card("❌ Despesas Totais", total_despesas, is_currency=True)
        with col3:
            create_metric_card("💰 Balanço", balanco, is_currency=True)
        with col4:
            create_metric_card("📈 Margem de Lucro", margem_lucro, is_percentage=True)

        st.markdown("## 📊 Gráficos de Receita vs Despesa")
        df_bar = pd.DataFrame({"Tipo": ["Receitas", "Despesas"], "Valor": [total_receitas, total_despesas]})
        fig = plot_bar_chart(
            df_bar, x="Tipo", y="Valor", title=f"Comparativo Financeiro - {ano}",
            color="Tipo", color_discrete_map={"Receitas": COLORS["secondary"], "Despesas": COLORS["primary"]}
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("## 🧾 Distribuição das Despesas")
        df_pizza = df_despesas.groupby('GASTOS')['Valor'].sum().reset_index()
        fig = plot_pie_chart(df_pizza, values="Valor", names="GASTOS", title="Tipos de Despesas")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("## 🧮 Indicadores Operacionais")
        st.info("💡 *Indicadores que ajudam a entender a estrutura de custos e a saúde financeira da empresa.*")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            create_metric_card("🏛️ Despesas Fixas", (despesas_fixas / total_despesas) * 100 if total_despesas else 0, is_percentage=True)
        with col2:
            create_metric_card("💧 Índice de Liquidez", total_receitas / total_despesas if total_despesas else 0)
        with col3:
            create_metric_card("⚙️ Margem de Contribuição", margem_contrib * 100, is_percentage=True)
        with col4:
            create_metric_card("📉 Ponto de Equilíbrio", ponto_eq, is_currency=True)

        st.markdown("## 🧠 Indicadores Estratégicos")
        st.info("📊 *Métricas para decisões de investimento e avaliação de performance financeira.*")

        investimento_total = df_despesas[df_despesas['GASTOS'] == "Investimento"]['Valor'].sum()
        roi = (balanco / investimento_total) * 100 if investimento_total > 0 else 0
        lucro_mensal = df.groupby('Mes')['Receita'].sum().mean()
        payback = investimento_total / lucro_mensal if lucro_mensal > 0 else 0
        ebitda = total_receitas - (despesas_fixas + despesas_variaveis)

        col1, col2, col3 = st.columns(3)
        with col1:
            create_metric_card("🚀 ROI", roi, is_percentage=True)
        with col2:
            create_metric_card("⏱️ Payback (meses)", payback)
        with col3:
            create_metric_card("💼 EBITDA", ebitda, is_currency=True)

    except Exception as e:
        st.error(f"Erro: {e}")
        st.info("Verifique se os dados estão disponíveis e bem formatados.")

if __name__ == "__main__":
    balanco_view()
