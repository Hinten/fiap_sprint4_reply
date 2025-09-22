import streamlit as st
import joblib
import os
import numpy as np


# --- 1. CARREGAR O SEU MODELO ---
# Esta função carrega seu modelo salvo e o guarda em cache para não recarregar a cada interação.


def previsao_manual():
    def carregar_modelo():
        pasta_resultados = os.path.join(os.path.dirname(__file__), "..", "machine_learning", "modelos_salvos")

        # Lista apenas arquivos .pkl
        modelos_pkl = [f for f in os.listdir(pasta_resultados) if f.endswith('.joblib')]

        modelo_str = st.selectbox("Selecione o modelo de classificação:", modelos_pkl)

        try:
            modelo = joblib.load(os.path.join(pasta_resultados, modelo_str))
            return modelo
        except FileNotFoundError:
            st.error(f"Arquivo do modelo {modelo_str} não encontrado. Verifique se o arquivo está na pasta correta.")
            return None

    # ...existing code...

    # Carrega o modelo ao iniciar a página
    modelo = carregar_modelo()

    # --- 2. INTERFACE VISUAL DA PÁGINA ---
    st.title("Classificador de Equipamentos")

    st.header("Insira as características de equipamentos:")

    Lux_str = st.number_input("Lux", value=15.0, step=1.0)
    Temperatura_str = st.number_input("Temperatura", value=14.0, step=1.0)
    vibracao_str = st.number_input("Vibração", value=0.0, step=1.0)

    # --- 3. LÓGICA DE PREVISÃO ---
    # O código abaixo só roda se o modelo foi carregado com sucesso
    if modelo:
        # Botão para executar a previsão, agora na página principal
        if st.button("Fazer Previsão"):
            # Junta todos os inputs de texto em uma lista
            features = [Lux_str, Temperatura_str, vibracao_str]

            # Converte a lista para o formato que o modelo espera (array 2D)
            dados_para_prever = np.array(features).reshape(1, -1)

            # Faz a previsão usando o modelo carregado
            resultado_numerico = modelo.predict(dados_para_prever)[0]


            # retorna se é necessário fazer manutenção ou não

            if int(resultado_numerico) == 1:
                resultado_texto = "Manutenção Necessária"
            else:
                resultado_texto = "Sem Manutenção Necessária"

            st.success(f"**{resultado_texto}**")



previsao_manual_page = st.Page(previsao_manual, title="Classificador Manual", icon="🤖")
