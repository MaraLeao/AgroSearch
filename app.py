import streamlit as st
import re
import math
import unicodedata
from collections import Counter
import pandas as pd

# BASE DE DOCUMENTOS 
DOCS = {
    1: "A soja requer irrigação constante durante o período de floração para garantir a produtividade.",
    2: "O controle biológico de lagartas na soja pode ser feito com a vespa Trichogramma.",
    3: "A adubação verde com leguminosas melhora o nitrogênio no solo para o milho.",
    4: "Lagartas desfolhadoras causam grande prejuízo na cultura da soja e do algodão.",
    5: "A irrigação por gotejamento economiza água e é ideal para o cultivo orgânico."
}

STOPWORDS = {'a', 'o', 'e', 'é', 'de', 'do', 'da', 'dos', 'das', 'para', 'com', 'na', 'no', 'nas', 'nos', 
             'por', 'que', 'se', 'pode', 'ser', 'feito', 'durante', 'os', 'as', 'um', 'uma'}

# PIPELINE DE PRÉ-PROCESSAMENTO
def remover_acentos(texto):
    texto = unicodedata.normalize('NFD', texto)
    texto = texto.encode('ascii', 'ignore').decode("utf-8")
    return str(texto)

def stemmer_ingenuo(palavra):
    sufixos = ['oes', 'cao', 'mente', 'ando', 'endo', 'indo', 'adas', 'ados', 'ada', 'ado', 'as', 'os', 'es', 's']
    for suf in sufixos:
        if palavra.endswith(suf) and len(palavra) > len(suf) + 2:
            return palavra[:-len(suf)]
    return palavra

def preprocessar(texto, usar_stopwords=True, usar_stemming=True):
    texto_limpo = remover_acentos(texto).lower()
    
    tokens = re.findall(r'\b[a-z0-9]+\b', texto_limpo)
    
    if usar_stopwords:
        tokens = [t for t in tokens if t not in STOPWORDS]
        
    if usar_stemming:
        tokens = [stemmer_ingenuo(t) for t in tokens]
        
    return tokens

# CONSTRUÇÃO DO ÍNDICE INVERTIDO E DADOS BASE
def construir_indice_e_stats(docs, usar_stopwords, usar_stemming):
    indice_invertido = {}
    docs_processados = {}
    
    for doc_id, texto in docs.items():
        tokens = preprocessar(texto, usar_stopwords, usar_stemming)
        docs_processados[doc_id] = tokens
        
        for token in set(tokens):
            if token not in indice_invertido:
                indice_invertido[token] = []
            indice_invertido[token].append(doc_id)
            
    return indice_invertido, docs_processados

# CÁLCULO TF-IDF E COSSENO
def calcular_tf(tokens):
    tf = {}
    total_termos = len(tokens)
    contagem = Counter(tokens)
    for termo, count in contagem.items():
        tf[termo] = count / total_termos if total_termos > 0 else 0
    return tf

def calcular_idf(indice_invertido, total_docs):
    idf = {}
    for termo, docs_com_termo in indice_invertido.items():
        idf[termo] = math.log10(total_docs / len(docs_com_termo))
    return idf

def calcular_vetor_tfidf(tokens_alvo, vocabulario, tf, idf):
    vetor = []
    for termo in vocabulario:
        if termo in tokens_alvo:
            vetor.append(tf[termo] * idf.get(termo, 0))
        else:
            vetor.append(0)
    return vetor

def similaridade_cosseno(vetor_a, vetor_b):
    dot_product = sum(a * b for a, b in zip(vetor_a, vetor_b))
    norm_a = math.sqrt(sum(a * a for a in vetor_a))
    norm_b = math.sqrt(sum(b * b for b in vetor_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)

# INTERFACE COM STREAMLIT
st.set_page_config(page_title="AgroSearch", layout="wide")

st.title("🌱 AgroSearch: Motor de Busca Inteligente")
st.markdown("Busca documental técnica utilizando pipeline NLP e TF-IDF construídos do zero.")
st.divider()

st.subheader("🔍 Realize sua Busca")

col_busca, col_botao = st.columns([15, 1])

with col_busca:
    query = st.text_input("Pesquisa", placeholder="Digite sua pesquisa técnica (ex: lagartas na soja)", label_visibility="collapsed")

with col_botao:
    btn_buscar = st.button("🔍", use_container_width=True)

col_stop, col_stem, _ = st.columns([2, 2, 6])
with col_stop:
    usar_stopwords = st.checkbox("Remover Stopwords", value=True)
with col_stem:
    usar_stemming = st.checkbox("Aplicar Stemming", value=True)

st.divider()

indice_invertido, docs_processados = construir_indice_e_stats(DOCS, usar_stopwords, usar_stemming)
total_docs = len(DOCS)
idf_geral = calcular_idf(indice_invertido, total_docs)

if query or btn_buscar:
    if not query:
        st.warning("Por favor, digite um termo para pesquisar.")
    else:
        st.subheader("📊 Resultados da Pesquisa")
        
        query_tokens = preprocessar(query, usar_stopwords, usar_stemming)
        st.info(f"**Query processada (Tokens):** {query_tokens}")
        
        if not query_tokens:
            st.warning("A consulta só continha stopwords. Tente outra palavra.")
        else:
            vocabulario = list(indice_invertido.keys())
            query_tf = calcular_tf(query_tokens)
            
            resultados = []
            
            for doc_id, tokens_doc in docs_processados.items():
                doc_tf = calcular_tf(tokens_doc)
                
                score_acumulado = 0
                for qt in query_tokens:
                    if qt in tokens_doc:
                        score_acumulado += (doc_tf[qt] * idf_geral.get(qt, 0))
                
                vetor_doc = calcular_vetor_tfidf(tokens_doc, vocabulario, doc_tf, idf_geral)
                vetor_query = calcular_vetor_tfidf(query_tokens, vocabulario, query_tf, idf_geral)
                cosseno = similaridade_cosseno(vetor_query, vetor_doc)
                
                if score_acumulado > 0 or cosseno > 0:
                    resultados.append({
                        "Doc ID": doc_id,
                        "Texto": DOCS[doc_id],
                        "TF-IDF Acumulado": round(score_acumulado, 4),
                        "Sim. Cosseno (Bônus)": round(cosseno, 4)
                    })
            
            if resultados:
                df_resultados = pd.DataFrame(resultados).sort_values(by="Sim. Cosseno (Bônus)", ascending=False).reset_index(drop=True)
                
                st.success(f"🏆 **Documento Vencedor:** Doc {df_resultados.iloc[0]['Doc ID']}!")
                st.markdown(f"*{df_resultados.iloc[0]['Texto']}*")
                
                def highlight_first(s):
                    return ['background-color: #2e7b32' if s.name == 0 else '' for i in s]
                
                st.dataframe(df_resultados.style.apply(highlight_first, axis=1), use_container_width=True)
            else:
                st.error("Nenhum documento relevante encontrado para a sua busca.")
                
    st.divider()

# EXIBIÇÃO DOS DADOS DE REFERÊNCIA
col1, col2 = st.columns(2)
with col1:
    st.subheader("📄 Base de Documentos")
    for d_id, txt in DOCS.items():
        st.markdown(f"**Doc {d_id}:** {txt}")

with col2:
    st.subheader("📚 Índice Invertido (Termo -> Docs)")
    dados_indice = [
        {"Termo": termo, "Documentos (IDs)": str(docs)} 
        for termo, docs in indice_invertido.items()
    ]
    df_indice = pd.DataFrame(dados_indice)
    st.dataframe(df_indice, use_container_width=True, hide_index=True)