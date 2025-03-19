import streamlit as st
import os
import sys
from pathlib import Path

# Adiciona caminhos aos diretórios de módulos
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / "utils"))
sys.path.append(str(Path(__file__).parent / "components"))

# Importando configurações e utilitários
from config import APP_TITLE
from utils.styling import set_page_config
from utils.data_loader import get_available_years

# Importando componentes
from components.gastos_gerais import gastos_gerais_view
from components.cartoes import cartoes_view
from components.veiculos import veiculos_view
from components.comparativo_anual import comparativo_anual_view
from components.balanco import balanco_view

# Configuração inicial da página
set_page_config()

def main():
    """
    Função principal da aplicação Streamlit
    """
    # Título da aplicação
    st.title(f"💰 {APP_TITLE}")
    
    # Verifica anos disponíveis
    available_years = get_available_years()
    
    if not available_years:
        st.error("⚠️ Nenhum arquivo de dados encontrado!")
        st.info(
            "Por favor, verifique se os arquivos CSV estão disponíveis no diretório 'data':"
            "\n- lgd2023.csv"
            "\n- lgd2024.csv"
            "\n- lgd2025.csv"
        )
        return
    
    # Menu lateral
    with st.sidebar:
        st.header("Navegação")
        
        # Seletor de página
        page = st.radio(
            "Selecione uma seção:",
            [
                "📊 Gastos Gerais",
                "💳 Cartões Corporativos",
                "🚗 Análise de Veículos",
                "📅 Comparativo Anual",
                "💰 Balanço Financeiro"
            ],
            index=0
        )
        
        st.markdown("---")
        
        # Informações da aplicação
        st.markdown("### Sobre")
        st.markdown("Sistema de Análise Financeira v1.0")
        st.markdown("Desenvolvido com Streamlit")
    
    # Renderiza a página selecionada
    if page == "📊 Gastos Gerais":
        gastos_gerais_view()
    elif page == "💳 Cartões Corporativos":
        cartoes_view()
    elif page == "🚗 Análise de Veículos":
        veiculos_view()
    elif page == "📅 Comparativo Anual":
        comparativo_anual_view()
    elif page == "💰 Balanço Financeiro":
        balanco_view()

if __name__ == "__main__":
    main() 