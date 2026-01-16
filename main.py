import streamlit as st
import requests
import os

# CONFIGURAÇÕES GERAIS
st.set_page_config(
    page_title="Otávio IA",
    page_icon="🤖",
    layout="centered"
)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
USERS = st.secrets["USERS"]

# CONTROLE DE LOGIN
if "logado" not in st.session_state:
    st.session_state["logado"] = False
    st.session_state["usuario"] = None

def tela_login():
    st.title("🔐 Login — Otávio IA")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if usuario in USERS and USERS[usuario] == senha:
            st.session_state["logado"] = True
            st.session_state["usuario"] = usuario
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos")

if not st.session_state["logado"]:
    tela_login()
    st.stop()

# SIDEBAR
st.sidebar.write(f"👤 Usuário: {st.session_state['usuario']}")

if st.sidebar.button("🚪 Sair"):
    st.session_state["logado"] = False
    st.session_state["usuario"] = None
    st.rerun()

# HISTÓRICO DE MENSAGENS
if "lista_mensagens" not in st.session_state:
    st.session_state["lista_mensagens"] = []


# FUNÇÃO DA IA (OPENROUTER)
def responder_ia(mensagens_usuario):
    url = "https://openrouter.ai/api/v1/chat/completions"

    mensagens = [
        {
            "role": "system",
            "content": (
                "Você é uma inteligência artificial chamada Otávio IA. "
                "Explique tudo de forma clara, didática e organizada. "
                "Use exemplos simples. "
                "Se a pergunta for de programação, explique passo a passo. "
                "Nunca responda curto demais. "
                "Se não souber algo, diga que não sabe."
            )
        }
    ]

    mensagens.extend(mensagens_usuario)

    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": mensagens,
        "temperature": 0.8
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    resposta = requests.post(url, headers=headers, json=payload)
    data = resposta.json()

    if "choices" not in data:
        return "⚠️ Erro ao obter resposta da IA."

    return data["choices"][0]["message"]["content"]

# INTERFACE PRINCIPAL
st.title("🤖 Otávio IA")
st.write("Sua IA pessoal de estudos e programação 🚀")

# Mostrar histórico
for msg in st.session_state["lista_mensagens"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Entrada do usuário
pergunta = st.chat_input("Digite sua pergunta...")

if pergunta:
    st.session_state["lista_mensagens"].append(
        {"role": "user", "content": pergunta}
    )

    with st.chat_message("user"):
        st.markdown(pergunta)

    with st.chat_message("assistant"):
        with st.spinner("Otávio IA está pensando..."):
            resposta = responder_ia(st.session_state["lista_mensagens"])
            st.markdown(resposta)

    st.session_state["lista_mensagens"].append(
        {"role": "assistant", "content": resposta}
    )
