from __future__ import annotations

import streamlit as st

from core import (
    DEFAULT_MODEL,
    buscar_conceitos,
    carregar_base,
    montar_contexto,
    montar_mensagens,
    ollama_disponivel,
    perguntar_ollama,
    resposta_fallback,
)

st.set_page_config(
    page_title="PyMentor",
    page_icon="🐍",
    layout="centered",
)


@st.cache_data
def base_de_conhecimento():
    return carregar_base()


base = base_de_conhecimento()

st.title("🐍 PyMentor")
st.caption("Um assistente simples para tirar dúvidas de Python sem pular a parte de aprender.")

with st.sidebar:
    st.subheader("Configuração")
    modelo = st.text_input("Modelo do Ollama", value=DEFAULT_MODEL)
    online = ollama_disponivel()
    if online:
        st.success("Ollama conectado")
    else:
        st.warning("Ollama não encontrado. Modo demonstração ativo.")

    st.divider()
    st.subheader("Base atual")
    st.write(f"{len(base['conceitos'])} conceitos")
    st.write(f"{len(base['exercicios'])} desafios")
    st.write(f"{len(base['erros'])} erros comuns")

    if st.button("Limpar conversa", use_container_width=True):
        st.session_state.mensagens = []
        st.rerun()

if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

if not st.session_state.mensagens:
    mensagem_inicial = (
        "Oi! Eu sou o PyMentor. Pode me perguntar sobre variáveis, `input()`, "
        "`if/elif/else`, listas, fatiamento, `%`, `//`, `for` e outros tópicos básicos."
    )
    st.session_state.mensagens.append({"role": "assistant", "content": mensagem_inicial})

for mensagem in st.session_state.mensagens:
    with st.chat_message(mensagem["role"]):
        st.markdown(mensagem["content"])

pergunta = st.chat_input("Digite sua dúvida de Python...")

if pergunta:
    st.session_state.mensagens.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)

    resultados = buscar_conceitos(pergunta, base["conceitos"])

    with st.chat_message("assistant"):
        if not resultados:
            resposta = resposta_fallback([], base["exercicios"])
            st.markdown(resposta)
        else:
            contexto = montar_contexto(resultados, base["exercicios"], base["erros"])

            if online:
                mensagens_ollama = montar_mensagens(
                    pergunta,
                    contexto,
                    historico=st.session_state.mensagens[:-1],
                )
                try:
                    with st.spinner("Pensando..."):
                        resposta = perguntar_ollama(mensagens_ollama, modelo=modelo)
                except Exception as erro:
                    resposta = resposta_fallback(resultados, base["exercicios"])
                    st.warning(f"Não consegui consultar o Ollama: {erro}")
            else:
                resposta = resposta_fallback(resultados, base["exercicios"])

            st.markdown(resposta)
            topicos = ", ".join(item["titulo"] for item in resultados)
            st.caption(f"Base consultada: {topicos}")

    st.session_state.mensagens.append({"role": "assistant", "content": resposta})
