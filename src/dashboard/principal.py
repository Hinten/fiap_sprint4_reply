import streamlit as st
from src.dashboard.machine import _machine_learning_results
from src.dashboard.notificacoes.enviar import enviar_email_teste


def _principal():
    enviar_email_teste()
    # _machine_learning_results()
    

def get_principal_page() -> st.Page:
    """
    Função para retornar a página principal.
    :return: st.Page - A página principal do aplicativo.
    """
    return st.Page(
        _principal,
        title="Principal",
        url_path="/"
    )
