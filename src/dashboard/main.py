import logging
from src.dashboard.login import login_view, login_sqlite, login_oracle_from_env, logint_postgres_from_env
import streamlit as st
from src.dashboard.navigator import navigation
from src.dashboard.setup import setup
from src.logger.config import configurar_logger
from src.dashboard.styles_loader import apply_custom_theme
from src.utils.env_utils import parse_bool_env


def main():
    """
    Função principal do aplicativo Streamlit.
    para rodar o aplicativo, execute o seguinte comando:
    streamlit run main_dash.py
    :return:
    """
    configurar_logger("dashboard.log")
    st.set_page_config(layout="wide") # deixa a página mais larga

    # Apply custom CSS theme once at dashboard startup
    apply_custom_theme()

    sql_lite:bool = parse_bool_env("SQL_LITE")
    oracle = parse_bool_env("ORACLE_DB_FROM_ENV")
    postgres:bool = parse_bool_env("POSTGRE_DB_FROM_ENV")

    if not st.session_state.get('logged_in', False):
        logging.debug('acessando login')

        if oracle:
            login_oracle_from_env()
        elif postgres:
            logint_postgres_from_env()
        elif sql_lite:
            login_sqlite()
        else:
            login_view()
    else:
        logging.debug('acessando dashboard')
        setup()
        # iniciar_api_sensor()
        navigation()

if __name__ == "__main__":
    main()
