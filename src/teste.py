from src.database.generator.criar_dados_leitura import criar_dados_leitura
from src.database.generator.gerar_sensores_e_dados import criar_dados_sample
from src.database.login.iniciar_database import iniciar_database
from src.database.models.sensor import LeituraSensor
from src.database.reset_contador_ids import reset_contador_ids, get_sequences_from_db
from src.database.tipos_base.database import Database
from src.database.utils.database_creation_explain import generate_ddl, generate_mer
from src.logger.config import configurar_logger
from datetime import datetime, timedelta


def teste():
    """Função teste do programa."""
    configurar_logger()
    Database.init_oracledb("RM561409", '250489')
    # Database.create_all_tables(drop_if_exists=False)

    generate_ddl()
    generate_mer()


if __name__ == "__main__":
    teste()