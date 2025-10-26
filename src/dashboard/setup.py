import logging
from src.database.tipos_base.database import Database
import streamlit as st
from src.dashboard.styles_loader import apply_custom_theme

def setup():
    # Apply custom CSS theme
    apply_custom_theme()

    Database.init_from_session(st.session_state.get('engine'), st.session_state.get('session'))

    if not st.session_state.get('init_tables', False):
        logging.info("Criando tabelas...")
        st.toast("Criando tabelas...")
        Database.create_all_tables()
        st.session_state['init_tables'] = True
        logging.info("Tabelas criadas com sucesso.")
        st.toast("Tabelas criadas com sucesso.")
