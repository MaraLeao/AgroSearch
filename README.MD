# AgroSearch

Um sistema de busca inteligente para documentos sobre agricultura e técnicas de cultivo.

## Descrição

O AgroSearch é uma aplicação web que permite buscar rapidamente informações sobre práticas agrícolas, como:
- Técnicas de irrigação
- Controle de pragas
- Adubação e melhoramento do solo
- Cultivo de diferentes commodities (soja, milho, algodão)

## Funcionalidades

- **Busca por palavras-chave**: Digite termos sobre agricultura e encontre documentos relevantes
- **Pré-processamento de texto**: Remove acentos, stopwords e aplica stemming para resultados mais precisos
- **Índice invertido**: Estrutura de dados otimizada para buscas rápidas e eficientes
- **Interface amigável**: Construída com Streamlit para fácil utilização

## Tecnologias

- **Python 3.x**
- **Streamlit**: Framework para criar aplicações web
- **Processamento de Linguagem Natural**: Tokenização, stemming e remoção de acentos

## Requisitos

```bash
pip install streamlit pandas
```

## Como executar

```bash
streamlit run app.py
```

A aplicação será aberta em seu navegador padrão (geralmente em `http://localhost:8501`)

## Estrutura

- `app.py`: Código principal da aplicação Streamlit
- `README.MD`: Este arquivo

## Exemplo de Uso

1. Inicie a aplicação
2. Digite uma palavra-chave na barra de busca (ex: "soja", "irrigação", "praga")
3. Visualize os documentos relevantes encontrados na base de dados