import logging
import os

from src.dashboard.api_sensor import iniciar_api_sensor
from src.dashboard.login import login_view, login_sqlite, login_oracle_from_env
import streamlit as st
from src.dashboard.navigator import navigation
from src.dashboard.setup import setup
from src.logger.config import configurar_logger


def main():
    """
    Função principal do aplicativo Streamlit.
    para rodar o aplicativo, execute o seguinte comando:
    streamlit run main_dash.py
    :return:
    """
    configurar_logger("dashboard.log")
    st.set_page_config(layout="wide") # deixa a página mais larga

    sql_lite:bool = str(os.environ.get("SQL_LITE", 'false')).lower() == "true"
    oracle_from_env = str(os.environ.get("ORACLE_DB_FROM_ENV", 'false')).lower() == "true"

    if not st.session_state.get('logged_in', False):
        logging.debug('acessando login')

        if sql_lite:
            login_sqlite()
        elif oracle_from_env:
            login_oracle_from_env()
        else:
            login_view()
    else:
        logging.debug('acessando dashboard')
        setup()
        iniciar_api_sensor()
        navigation()

if __name__ == "__main__":
    main()
