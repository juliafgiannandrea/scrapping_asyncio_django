import streamlit as st
import pandas as pd
import requests
import threading

API_URL = "http://localhost:8000/api/webscrapping"

st.set_page_config(page_title="Scraper DF Imóveis", layout="wide")
st.title("Scraping de Imóveis com Django + Streamlit")

if "df" not in st.session_state:
    st.session_state.df = None

# Função para disparar scraping em background
def executar_scraping_e_carregar_df(filtros):
    try:
        response = requests.post(f"{API_URL}/executar-e-retornar", json=filtros)
        if response.status_code == 200:
            dados = response.json()
            if dados:
                st.session_state.df = pd.DataFrame(dados)
                st.success(f"{len(dados)} imóveis encontrados.")
            else:
                st.warning("Nenhum imóvel encontrado.")
        else:
            st.error(f"Erro no scraping: {response.status_code}")
    except Exception as e:
        st.error(f"Erro ao executar scraping: {e}")





# # Função para buscar os dados prontos do banco
# def consultar_resultados():
#     try:
#         response = requests.get(f"{API_URL}/imoveis")
#         if response.status_code == 200:
#             dados = response.json()
#             if dados:
#                 st.session_state.df = pd.DataFrame(dados)
#                 st.success(f"{len(dados)} imóveis carregados do banco.")
#             else:
#                 st.warning("Nenhum dado encontrado no banco ainda.")
#         else:
#             st.error("Erro ao consultar o banco.")
#     except Exception as e:
#         st.error(f"Erro ao buscar resultados: {e}")


# Função para salvar os dados exibidos
def salvar_no_banco(dados):
    try:
        response = requests.post(f"{API_URL}/salvar-dados", json=dados)
        if response.status_code == 200:
            mensagem = response.json().get("mensagem", "")
            if "já cadastrados" in mensagem:
                st.info("Imóveis já cadastrados.")
            else:
                st.success(mensagem)
        else:
            st.error("Erro ao salvar os dados.")
    except Exception as e:
        st.error(f"Erro ao salvar no banco: {e}")


def carregar_todos_os_imoveis():
    try:
        response = requests.get(f"{API_URL}/imoveis")
        if response.status_code == 200:
            dados = response.json()
            if dados:
                st.session_state.df = pd.DataFrame(dados)
                st.success(f"{len(dados)} imóveis carregados do banco.")
            else:
                st.warning("Nenhum imóvel encontrado no banco.")
        else:
            st.error(f"Erro ao buscar imóveis: {response.status_code}")
    except Exception as e:
        st.error(f"Erro ao buscar imóveis: {e}")

# Formulário de filtros
with st.form("filtros_form"):
    st.subheader("Filtros de Busca")

    tipo_operacao = st.selectbox("Tipo de operação", ["", "ALUGUEL", "IMOVEL NOVO", "TEMPORADA", "VENDA"])
    tipo_imovel = st.selectbox("Tipo de imóvel", [
        "", "Apartamento", "Casa", "Kitnet/Studio", "Cobertura", "Loja",
        "Prédio", "Terreno", "Hotel/Flat"
    ])
    localizacao = st.text_input("Localização")
    cidade = st.text_input("Cidade")
    bairro = st.text_input("Bairro")
    quartos = st.selectbox("Número de quartos", ["", "1", "2", "3", "4", "5 ou mais"])
    preco_medio = st.text_input("Preço médio")
    palavra_chave = st.text_input("Palavra-chave")

    submit = st.form_submit_button("Executar scraping")

if submit:
    filtros = {
        "tipo_operacao": tipo_operacao,
        "tipo_imovel": tipo_imovel,
        "localizacao": localizacao,
        "cidade": cidade,
        "bairro": bairro,
        "quartos": quartos,
        "preco_medio": preco_medio,
        "palavra_chave": palavra_chave
    }

    with st.spinner("⏳ Executando scraping... isso pode levar alguns segundos."):
        executar_scraping_e_carregar_df(filtros)


# if st.button("📦 Visualizar todos os imóveis do banco"):
#     carregar_todos_os_imoveis()

# # Exibição dos resultados
# if st.session_state.df is not None:
#     st.subheader("Resultado da Busca")
#     st.dataframe(st.session_state.df, use_container_width=True)

#     if st.button("Salvar no banco"):
#         salvar_no_banco(st.session_state.df.to_dict(orient="records"))



# Se uma tarefa assíncrona estiver em andamento, verifica o status
if "task_id" in st.session_state:
    try:
        response = requests.get(f"{API_URL}/resultado-tarefa/" + st.session_state.task_id)
        if response.status_code == 200:
            resultado = response.json()
            if resultado["status"] == "done":
                st.session_state.df = pd.DataFrame(resultado["dados"])
                st.success(f"{len(resultado['dados'])} imóveis encontrados.")
                del st.session_state.task_id
            else:
                st.info("⏳ Scraping ainda em andamento... clique em 'Atualizar resultados' abaixo.")
                if st.button("🔄 Atualizar resultados"):
                    st.experimental_rerun()
    except Exception as e:
        st.error(f"Erro ao buscar resultado da tarefa: {e}")

# Botão para visualizar todos os imóveis cadastrados no banco
if st.button("📦 Visualizar todos os imóveis do banco"):
    carregar_todos_os_imoveis()

# Exibição dos resultados da busca
if st.session_state.df is not None:
    st.subheader("Resultado da Busca")
    st.dataframe(st.session_state.df, use_container_width=True)

    if st.button("Salvar no banco"):
        salvar_no_banco(st.session_state.df.to_dict(orient="records"))
