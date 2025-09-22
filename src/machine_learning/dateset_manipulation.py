import pandas as pd
import numpy as np
from sqlalchemy.orm import joinedload
from src.database.models.sensor import LeituraSensor, Sensor
from src.database.tipos_base.database import Database

def _convert_sensor_id_to_tipo_sensor(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converte os sensor_id para o tipo do sensor.
    :param df: DataFrame com as leituras.
    :return: DataFrame com os tipos dos sensores.
    """

    sensores_ids = list(map(int, df['sensor_id'].unique()))
    with Database.get_session() as session:
        sensores = session.query(Sensor) \
            .options(joinedload(Sensor.tipo_sensor)) \
            .filter(Sensor.id.in_(sensores_ids)).all()

    sensor_id_to_tipo = {sensor.id: sensor.tipo_sensor.tipo.__str__() for sensor in sensores}

    df['tipo_sensor'] = df['sensor_id'].map(sensor_id_to_tipo)

    return df

def _convert_leituras_to_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converte as leituras para um DataFrame com uma coluna para cada sensor_id,
    preenchendo NA com o valor da data_leitura mais próxima.
    """
    df_pivot = df.pivot_table(index='data_leitura', columns='tipo_sensor', values='valor', aggfunc='mean')
    df_pivot = df_pivot.interpolate(method='nearest', limit_direction='both')
    df_pivot = df_pivot.ffill().bfill()
    df_pivot = df_pivot.reset_index()

    return df_pivot

def _limpar_redundantes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove colunas redundantes do DataFrame.
    :param df: DataFrame com as leituras.
    :return: DataFrame sem colunas redundantes.
    """

    if df.duplicated().sum() == 0:
        return df

    print(f"Removendo {df.duplicated().sum()} linhas duplicadas...")
    return df.drop_duplicates()

def _criar_coluna_target(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria uma coluna target com o nome Manutencao tipo binário (0 ou 1) de forma aleatória.
    :param df: DataFrame com as leituras.
    :return: DataFrame com a coluna target.
    """

    np.random.seed(42)
    np.random.seed(42)
    df['Manutencao'] = np.random.randint(0, 2, size=len(df))
    return df

def get_dataframe_leituras_sensores() -> pd.DataFrame:
    """
    Retorna um DataFrame com todas as leituras dos sensores.
    :return: DataFrame com as leituras dos sensores.
    """
    leituras = LeituraSensor.as_dataframe_all()
    df = _convert_sensor_id_to_tipo_sensor(leituras)
    df = _convert_leituras_to_dataframe(df)
    df = _limpar_redundantes(df)
    df = _criar_coluna_target(df)

    return df


if __name__ == '__main__':

    pd.set_option('display.max_columns', 50)

    Database.init_sqlite(r'C:\Users\Lucas\PycharmProjects\fiap_sprint3_reply_leo\database.db')
    Database.create_all_tables()

    leituras = get_dataframe_leituras_sensores()

    print(leituras.shape)
    print(leituras.columns)

    print(leituras.head())
    #
    # print(leituras.describe())
    # print(leituras.info())
    # print(leituras.isna().sum())
    # print(leituras.dtypes)
