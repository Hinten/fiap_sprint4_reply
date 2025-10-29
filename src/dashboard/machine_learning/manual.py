import streamlit as st
import joblib
import os
import numpy as np
from datetime import datetime

from src.notificacoes.email import enviar_email
from src.utils.model_store import list_models, load_model, get_models_summary


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
        """Carrega modelo do registry ou da pasta legada."""
        
        # Primeiro tenta carregar do registry
        registry = list_models()
        
        if registry:
            st.write("### 📚 Modelos Disponíveis no Registry")
            
            # Cria lista de modelos para seleção
            models_summary = get_models_summary()
            
            if models_summary:
                # Exibe tabela com informações dos modelos
                import pandas as pd
                summary_df = pd.DataFrame(models_summary)
                
                # Seleciona colunas relevantes para display
                display_cols = ['name', 'saved_at']
                if 'model_type' in summary_df.columns:
                    display_cols.append('model_type')
                if 'Accuracy' in summary_df.columns:
                    display_cols.append('Accuracy')
                if 'AUC' in summary_df.columns:
                    display_cols.append('AUC')
                    
                display_df = summary_df[[col for col in display_cols if col in summary_df.columns]]
                st.dataframe(display_df, use_container_width=True)
                
                # Selectbox para escolher modelo
                model_names = [m['name'] for m in models_summary]
                selected_model_name = st.selectbox(
                    "Selecione o modelo:",
                    options=model_names,
                    key="model_selector"
                )
                
                # Exibe detalhes do modelo selecionado
                if selected_model_name:
                    selected_info = next(m for m in models_summary if m['name'] == selected_model_name)
                    
                    with st.expander("ℹ️ Detalhes do Modelo"):
                        st.json(selected_info)
                    
                    try:
                        modelo = load_model(selected_model_name)
                        st.success(f"✅ Modelo '{selected_model_name}' carregado com sucesso!")
                        return modelo
                    except Exception as e:
                        st.error(f"❌ Erro ao carregar modelo: {str(e)}")
                        return None
            else:
                st.warning("Nenhum modelo encontrado no registry.")
                return None
        
        else:
            # Fallback para o método legado
            st.info("📂 Usando método legado de carregamento (pasta modelos_salvos)")
            
            pasta_resultados = os.path.join(
                os.path.dirname(__file__), 
                "..", 
                "..", 
                "machine_learning", 
                "modelos_salvos"
            )

            # Lista apenas arquivos .pkl e .joblib
            modelos_disponiveis = [
                f for f in os.listdir(pasta_resultados) 
                if f.endswith(('.pkl', '.joblib'))
            ]
            
            if not modelos_disponiveis:
                st.warning("Nenhum modelo encontrado. Treine um modelo primeiro.")
                return None

            modelo_str = st.selectbox(
                "Selecione o modelo de classificação:", 
                modelos_disponiveis
            )

            try:
                modelo = joblib.load(os.path.join(pasta_resultados, modelo_str))
                st.success(f"✅ Modelo '{modelo_str}' carregado!")
                return modelo
            except FileNotFoundError:
                st.error(
                    f"Arquivo do modelo {modelo_str} não encontrado. "
                    "Verifique se o arquivo está na pasta correta."
                )
                return None
            except Exception as e:
                st.error(f"❌ Erro ao carregar modelo: {str(e)}")
                return None

    modelo = carregar_modelo()

    # --- 3. LÓGICA DE PREVISÃO ---
    # O código abaixo só roda se o modelo foi carregado com sucesso
    if modelo:
        st.write("---")
        # Botão para executar a previsão, agora na página principal
        if st.button("🔮 Fazer Previsão", type="primary"):
            try:
                # Junta todos os inputs de texto em uma lista
                features = [lux, temp, vibracao]

                # Converte a lista para o formato que o modelo espera (array 2D)
                dados_para_prever = np.array(features).reshape(1, -1)

                # Faz a previsão usando o modelo carregado
                resultado_numerico = modelo.predict(dados_para_prever)[0]

                # Mostra probabilidades se o modelo suportar
                if hasattr(modelo, 'predict_proba'):
                    probabilidades = modelo.predict_proba(dados_para_prever)[0]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Probabilidade - Sem Manutenção", f"{probabilidades[0]:.2%}")
                    with col2:
                        st.metric("Probabilidade - Com Manutenção", f"{probabilidades[1]:.2%}")

                # retorna se é necessário fazer manutenção ou não
                if int(resultado_numerico) == 1:
                    st.error("⚠️ **Manutenção Necessária**")
                    enviar_alerta_manutencao(
                        lux,
                        temp,
                        vibracao
                    )

                else:
                    st.success("✅ **Sem Necessidade de Manutenção**")
                    
            except Exception as e:
                st.error(f"❌ Erro ao fazer previsão: {str(e)}")
                st.info("Verifique se os valores de entrada estão corretos.")
    else:
        st.warning("⚠️ Nenhum modelo carregado. Por favor, selecione um modelo válido acima.")


def previsao_manual():
    # --- 2. INTERFACE VISUAL DA PÁGINA ---
    st.title("🤖 Classificador de Equipamentos")

    st.header("Insira as características de equipamentos:")
    
    st.write("""
    Este classificador utiliza machine learning para prever se um equipamento 
    necessita de manutenção com base em três parâmetros principais:
    """)

    col1, col2, col3 = st.columns(3)
    
    with col1:
        Lux_str = st.number_input(
            "💡 Lux (x10³)", 
            value=15.0, 
            step=1.0,
            help="Intensidade luminosa medida pelo sensor"
        )
    
    with col2:
        Temperatura_str = st.number_input(
            "🌡️ Temperatura (°C)", 
            value=14.0, 
            step=1.0,
            help="Temperatura ambiente registrada"
        )
    
    with col3:
        vibracao_str = st.number_input(
            "📳 Vibração", 
            value=0.0, 
            step=0.1,
            help="Nível de vibração detectado"
        )

    carregar_modelo_e_realizar_previsao(
        Lux_str,
        Temperatura_str,
        vibracao_str
    )





previsao_manual_page = st.Page(previsao_manual, title="Classificador Manual", icon="🤖")
