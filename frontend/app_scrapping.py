import streamlit as st
import pandas as pd
import requests
import threading

API_URL = "http://localhost:8000/api/webscrapping"

st.set_page_config(page_title="Scraper DF Imóveis", layout="wide")
st.title("Scraping de Imóveis com Django + Streamlit")

if "df" not in st.session_state:
    st.session_state.df = None

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


# Função para disparar scraping em background
def executar_scraping_e_carregar_df(filtros):
    try:
        response = requests.post(f"{API_URL}/executar-scraping", json=filtros)
        if response.status_code == 200:
            dados = response.json()
            if dados:
                st.session_state.df = pd.DataFrame(dados)
                st.session_state.scraping_status = f"{len(dados)} imóveis carregados com sucesso."
            else:
                st.session_state.scraping_status = "Nenhum dado retornado."
        else:
            st.session_state.scraping_status = f"Erro no scraping: {response.status_code}"
    except Exception as e:
        st.session_state.scraping_status = f"Erro ao executar scraping: {e}"


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
    

    st.session_state.scraping_status = "Scraping em andamento..."
    threading.Thread(
        target=executar_scraping_e_carregar_df,
        args=(filtros,),
        daemon=True
    ).start()
    st.success("Scraping iniciado. Clique em 'Consultar resultados' depois de alguns segundos.")
        


#botões:
if st.button("📦 Visualizar todos os imóveis do banco"):
    carregar_todos_os_imoveis()

if st.button("Consultar resultados"):
    if "scraping_status" in st.session_state:
        st.info(st.session_state.scraping_status)

    try:
        response = requests.get(f"{API_URL}/resultados-atuais")
        if response.status_code == 200:
            dados = response.json()
            if dados:
                st.session_state.df = pd.DataFrame(dados)
                st.dataframe(st.session_state.df)
            else:
                st.warning("Ainda não há resultados disponíveis.")
        else:
            st.error("Erro ao buscar resultados.")
    except Exception as e:
        st.error(f"Erro ao consultar resultados: {e}")


if st.session_state.df is not None and not st.session_state.df.empty:
    st.subheader("Resultado da Busca")
    st.dataframe(st.session_state.df, use_container_width=True)

    if st.button("Salvar no banco"):
        try:
            response = requests.post(f"{API_URL}/salvar-dados", json=st.session_state.df.to_dict(orient="records"))
            if response.status_code == 200:
                st.success(response.json().get("mensagem", "Dados salvos com sucesso."))
            else:
                st.error("Erro ao salvar os dados no banco.")
        except Exception as e:
            st.error(f"Erro ao salvar: {e}")

    