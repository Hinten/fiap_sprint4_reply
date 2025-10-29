import streamlit as st
from src.large_language_model.client import GenerativeModelClient, AvailableGenerativeModels
from google.genai import types, chats
import logging

def get_or_init_chat_client() -> GenerativeModelClient:
    """
    Função para obter ou inicializar o cliente do modelo de linguagem generativa.
    :return: GenerativeModelClient - A instância do cliente do modelo de linguagem generativa.
    """
    if "generative_model_client" not in st.session_state:
        logging.debug("Initializing generative model client...")
        st.session_state.generative_model_client = GenerativeModelClient()

    return st.session_state.generative_model_client

def get_or_init_chat(new_chat: bool = False, generative_model: AvailableGenerativeModels or None = None) -> chats.Chat:
    """
    Função para obter ou inicializar o chat.
    :param new_chat: Se True, cria um novo chat mesmo que já exista um.
    :param generative_model: Modelo a ser utilizado. Se não fornecido, usa o modelo padrão.
    :return: Chat - A instância do chat com o modelo de linguagem generativa.
    """
    if "generative_model_client" not in st.session_state:
        logging.debug("Initializing generative model...")
        st.session_state.generative_model_client = GenerativeModelClient()

    if "generative_chat" not in st.session_state or new_chat:
        logging.info("Creating new chat...")
        st.session_state.generative_chat = st.session_state.generative_model_client.get_chat(generative_model=generative_model)

    return st.session_state.generative_chat
