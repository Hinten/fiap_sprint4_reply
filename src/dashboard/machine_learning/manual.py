import streamlit as st
import joblib
import os
import numpy as np
from datetime import datetime

from src.notificacoes.email import enviar_email


# --- 1. CARREGAR O SEU MODELO ---
# Esta função carrega seu modelo salvo e o guarda em cache para não recarregar a cada interação.

@st.fragment
def enviar_alerta_manutencao(lux, temperatura, vibracao):
    if st.button("Enviar Alerta de Manutenção"):
        hoje = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        enviar_email(
            f"Manutenção Necessária - {hoje}",
            "Prezado(a),\n\nO classificador de equipamentos identificou que uma manutenção é necessária com base nas características fornecidas:\n\n"
            f"- Lux: {lux:.2f}\n"
            f"- Temperatura: {temperatura:.2f}\n"
            f"- Vibração: {vibracao:.2f}\n\n"
            "Por favor, agende a manutenção o mais breve possível.\n\nAtenciosamente,\nSistema de Monitoramento"
        )
        st.success("Alerta de manutenção enviado com sucesso!")

@st.fragment
def carregar_modelo_e_realizar_previsao(lux:float, temp:float, vibracao:float):
    def carregar_modelo():
        pasta_resultados = os.path.join(os.path.dirname(__file__), "..", "..", "machine_learning", "modelos_salvos")

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

    # --- 3. LÓGICA DE PREVISÃO ---
    # O código abaixo só roda se o modelo foi carregado com sucesso
    if modelo:
        # Botão para executar a previsão, agora na página principal
        if st.button("Fazer Previsão"):
            # Junta todos os inputs de texto em uma lista
            features = [lux, temp, vibracao]

            # Converte a lista para o formato que o modelo espera (array 2D)
            dados_para_prever = np.array(features).reshape(1, -1)

            # Faz a previsão usando o modelo carregado
            resultado_numerico = modelo.predict(dados_para_prever)[0]

            # retorna se é necessário fazer manutenção ou não

            if int(resultado_numerico) == 1:
                st.success("Manutenção Necessária")
                enviar_alerta_manutencao(
                    lux,
                    temp,
                    vibracao
                )

            else:
                st.success("Sem Manutenção Necessária")


def previsao_manual():


    # --- 2. INTERFACE VISUAL DA PÁGINA ---
    st.title("Classificador de Equipamentos")

    st.header("Insira as características de equipamentos:")

    Lux_str = st.number_input("Lux", value=15.0, step=1.0)
    Temperatura_str = st.number_input("Temperatura", value=14.0, step=1.0)
    vibracao_str = st.number_input("Vibração", value=0.0, step=1.0)

    carregar_modelo_e_realizar_previsao(
        Lux_str,
        Temperatura_str,
        vibracao_str
    )





previsao_manual_page = st.Page(previsao_manual, title="Classificador Manual", icon="🤖")
