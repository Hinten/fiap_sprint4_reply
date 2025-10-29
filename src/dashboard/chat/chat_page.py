import streamlit as st

from src.dashboard.chat.conversa_chat import get_conversa


def _chat():
    """
    Renderiza a página de chat com o assistente de IA.
    """
    get_conversa()
    

chat_page = st.Page(
        _chat,
        title="Chat IA",
        icon="🤖",
        url_path="/chat"
    )
