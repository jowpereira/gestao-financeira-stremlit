# 💰 Sistema de Gestão Financeira

Esta aplicação interativa realiza análise financeira detalhada baseada em arquivos CSV. O sistema foi desenvolvido para ajudar empresas a controlar gastos, identificar oportunidades para redução de custos, otimizar operações financeiras, monitorar cartões corporativos, analisar gastos com veículos e comparar receitas e despesas.

## 📚 Funcionalidades

### 📊 Painéis Analíticos:
- **Gastos Gerais**: Visualização completa de todas as despesas
- **Cartões Corporativos**: Análise detalhada por funcionário
- **Análise de Veículos**: Eficiência de combustível e custos de manutenção
- **Comparativo Anual**: Evolução dos gastos ao longo dos anos
- **Balanço Financeiro**: Comparativo entre receitas e despesas

## 🚀 Como Executar

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Configuração do Ambiente

1. Clone o repositório:
```
git clone [url-do-repositorio]
cd gestao-financeira-streamlit
```

2. Crie um ambiente virtual:
```
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Instale as dependências:
```
pip install -r requirements.txt
```

4. Verifique se os arquivos de dados estão na pasta correta:
```
data/
  ├── lgd2023.csv
  ├── lgd2024.csv
  └── lgd2025.csv
```

### Executando a Aplicação

```
streamlit run app/main.py
```

A aplicação estará disponível em `http://localhost:8501`

## 📁 Estrutura do Projeto

```
gestao-financeira-streamlit/
│
├── app/
│   ├── main.py                  # Arquivo principal da aplicação
│   ├── components/              # Componentes da interface
│   │   ├── gastos_gerais.py     # Análise de gastos gerais
│   │   ├── cartoes.py           # Análise de cartões corporativos
│   │   ├── veiculos.py          # Análise de veículos
│   │   ├── comparativo_anual.py # Comparativo de anos
│   │   └── balanco.py           # Balanço financeiro
│   ├── utils/
│   │   ├── data_loader.py       # Carregamento de dados CSV
│   │   ├── preprocessing.py     # Processamento dos dados
│   │   └── styling.py           # Estilos para a aplicação
│   └── config.py                # Configurações da aplicação
│
├── data/
│   ├── lgd2023.csv              # Dados financeiros 2023
│   ├── lgd2024.csv              # Dados financeiros 2024
│   └── lgd2025.csv              # Dados financeiros 2025
│
├── .env                         # Variáveis de ambiente
├── requirements.txt             # Dependências do projeto
└── README.md                    # Documentação
```

## 📄 Formato dos Arquivos CSV

Os arquivos CSV devem seguir a seguinte estrutura:

```
Data,Tipo,Categoria,Valor,Descrição,...
2023-01-15,Fixo,Aluguel,1500.00,Pagamento mensal,...
...
```

As colunas obrigatórias são:
- `Data`: Data da despesa (formato YYYY-MM-DD)
- `Tipo`: Tipo de despesa (Fixo, Variável, Não Operacional)
- `Categoria`: Categoria da despesa
- `Valor`: Valor da despesa

## 📝 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para mais detalhes.

## ✨ Próximos Passos

- Implementação dos módulos de Cartões Corporativos
- Implementação do módulo de Análise de Veículos
- Implementação do Comparativo Anual
- Implementação do Balanço Financeiro
- Adição de funcionalidades de exportação de relatórios
- Melhorias na interface do usuário 