import streamlit as st
from src.dashboard.machine import _machine_learning_results


def _principal():

    _machine_learning_results()
    

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