import logging
from src.database.tipos_base.database import Database
import streamlit as st


def setup():
    # Database já foi inicializado no login, apenas verifica se as tabelas foram criadas
    if not st.session_state.get('init_tables', False):
        logging.info("Criando tabelas...")
        st.toast("Criando tabelas...")
        Database.create_all_tables()
        st.session_state['init_tables'] = True
        logging.info("Tabelas criadas com sucesso.")
        st.toast("Tabelas criadas com sucesso.")
    elif st.session_state.get('logged_in', False):
        Database.init_from_dashboard(st.session_state.engine, st.session_state.session)
    else:
        raise RuntimeError("Banco de dados não inicializado. Faça o login primeiro.")
