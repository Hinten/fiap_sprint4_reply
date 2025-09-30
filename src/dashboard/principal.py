import streamlit as st

from src.dashboard.visualizacao_leituras.visualizador_leituras import visualizador_leituras_page


def _principal():
    visualizador_leituras_page()
    

principal_page = st.Page(
        _principal,
        title="Principal",
        url_path="/"
    )
