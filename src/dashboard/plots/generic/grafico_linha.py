import streamlit as st
from src.database.models.sensor import LeituraSensor
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def get_grafico_linha(
        leituras: list[LeituraSensor],
        title: str,
        limiar_manutencao_maior: float = None,
        limiar_manutencao_menor: float = None,
        show_df: bool = True,
):
    """
    Função para gerar um gráfico de linha com os dados do sensor.
    :param leituras: instâncias de LeituraSensor
    :param title: título do gráfico
    :param limiar_manutencao_maior: valor do limiar superior (opcional)
    :param limiar_manutencao_menor: valor do limiar inferior (opcional)
    :param show_df: se True, exibe a tabela com os dados abaixo do gráfico
    :return:
    """

    # Cria um DataFrame a partir das leituras
    df = pd.DataFrame([{
        'data_leitura': leitura.data_leitura,
        'valor': leitura.valor
    } for leitura in leituras])

    # Gráfico de linha
    fig, ax = plt.subplots()
    ax.plot(df['data_leitura'], df['valor'])
    ax.grid(True)
    ax.set_xlabel('Data')
    ax.set_ylabel('Valor')
    ax.set_title(title)
    date_format = mdates.DateFormatter('%H:%M %d/%m/%Y')
    ax.xaxis.set_major_formatter(date_format)
    plt.xticks(rotation=45)

    # Adiciona linha vermelha para o limiar superior, se definido
    if limiar_manutencao_maior is not None:
        ax.axhline(y=limiar_manutencao_maior, color='red', linestyle='--', label='Limiar Superior')

    # Adiciona linha vermelha para o limiar inferior, se definido
    if limiar_manutencao_menor is not None:
        ax.axhline(y=limiar_manutencao_menor, color='yellow', linestyle='--', label='Limiar Inferior')

    # Exibe a legenda se algum limiar foi adicionado
    if limiar_manutencao_maior is not None or limiar_manutencao_menor is not None:
        ax.legend()

    # Exibe o gráfico no Streamlit
    st.pyplot(fig)

    # Tabela com os dados
    if show_df:
        st.write(df)
