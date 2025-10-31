import streamlit as st
from pycaret.classification import *
from src.machine_learning.dateset_manipulation import get_dataframe_leituras_sensores
from src.utils.model_store import save_model as save_model_to_registry, list_models, get_models_summary
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd


@st.cache_data(ttl=3600, show_spinner="Carregando dados...")
def load_sensor_data():
    """Carrega dados dos sensores com cache para evitar recarregamentos."""
    return get_dataframe_leituras_sensores()


def train_model_view():
    st.title('Treinando a IA com Pycaret')

    use_gpu = st.checkbox('Usar GPU?', value=True)

    # Carrega dados com cache
    df = load_sensor_data()

    if df.empty:
        st.warning("O DataFrame está vazio. Verifique se há dados disponíveis.")
        return

    target_column = 'Manutencao'

    train_dataset = df.drop(columns=['data_leitura'])
    train_dataset[target_column] = train_dataset[target_column].apply(lambda x: bool(x))
    st.write(train_dataset.head())

    st.write("""
    🔢 A tabela acima apresenta variáveis de sensores e a saída de manutenção:

        - Lux (x10³): intensidade luminosa.

        - Temperatura (°C): registro da temperatura.

        - Vibração: nível de vibração detectado.

        - Manutenção: campo binário (checkbox) que indica se houve necessidade de manutenção ou não.
             """)
    
    st.write(train_dataset.dtypes)

    st.write("""
            📑 Os tipos de dados estão adequados para o treinamento do modelo. As variáveis independentes são numéricas (float64) e a variável dependente é booleana (bool).
             """)
    

    pairplot_fig = sns.pairplot(
        train_dataset.drop(columns=[target_column]),
        # diag_kind="kde",
        # corner=True,
        # plot_kws={"alpha": 0.7, "s": 40, "edgecolor": "k"},
        # diag_kws={"shade": True},
        palette="viridis"
    )

    pairplot_fig.figure.suptitle("Pairplot dos Dados", y=1.02, fontsize=16)

    st.pyplot(pairplot_fig)
    
    st.write("""
     📊 Grafico de Pairplot dos dados, que é uma forma de visualizar a distribuição individual e as relações entre as variáveis medidas: Lux (x10³), Temperatura (°C) e Vibração.

         - Na diagonal, aparecem histogramas que revelam a distribuição de cada variável individualmente.

         - Fora da diagonal, temos gráficos de dispersão (scatter plots), que permitem observar possíveis correlações entre os pares de variáveis.

         - Tipo de visualização ajuda a identificar padrões, outliers e relações entre os atributos que podem ser relevantes para o modelo de aprendizado de máquina.
             """)

    s = setup(data=train_dataset, target=target_column, session_id=123, use_gpu=use_gpu, train_size=0.7, html=True)

    # Puxa o resumo do setup
    setup_summary = pull()

    st.dataframe(setup_summary)
    
    st.write("""
            ✅ A tabela acima resume as transformações aplicadas aos dados, como tratamento de valores ausentes, codificação de variáveis categóricas e normalização. Isso garante que os dados estejam prontos para o treinamento do modelo.
             """)

    metrica = st.selectbox('Selecione a métrica para comparar os modelos',
                           [
                               'Accuracy',
                               'AUC',
                               'Recall',
                               'Precision',
                               'F1',
                               'Kappa',
                               'MCC'
                            ]
               )

    turbo = st.checkbox("Modo turbo (mais rápido, menos preciso)", value=True)

    # Inicializa no session_state
    if 'top_models' not in st.session_state:
        st.session_state.top_models = None
    if 'compare_df' not in st.session_state:
        st.session_state.compare_df = None

    if st.button('Treinar e comparar modelos'):

        with st.spinner("Treinando modelos (este processo pode demorar um pouco)..."):
            # Compara e seleciona os top 5 modelos
            top_models = s.compare_models(n_select=5, sort=metrica, fold=5, turbo=turbo)
            compare_df = pull()
            
            # Armazena no session_state
            st.session_state.top_models = top_models
            st.session_state.compare_df = compare_df
            
            st.success("✅ Treinamento concluído! Veja abaixo a comparação dos top 5 modelos.")

    # Exibe resultados se existirem
    if st.session_state.top_models is not None:
        
        st.write("### 📊 Comparação de Todos os Modelos")
        st.dataframe(st.session_state.compare_df, use_container_width=True)
        
        # Garante que top_models seja uma lista
        top_models_list = st.session_state.top_models if isinstance(st.session_state.top_models, list) else [st.session_state.top_models]
        
        st.write("### 🏆 Top 5 Modelos Selecionados")
        
        # Cria dataframe para visualização dos top 5
        top_5_info = []
        for idx, model in enumerate(top_models_list[:5], 1):
            model_name = model.__class__.__name__
            # Busca métricas do compare_df
            if 'Model' in st.session_state.compare_df.columns:
                model_row = st.session_state.compare_df[
                    st.session_state.compare_df['Model'].str.contains(model_name, case=False, na=False)
                ]
                if not model_row.empty:
                    metrics_dict = model_row.iloc[0].to_dict()
                    metrics_dict['Rank'] = idx
                    top_5_info.append(metrics_dict)
        
        if top_5_info:
            top_5_df = pd.DataFrame(top_5_info)
            st.dataframe(top_5_df, use_container_width=True)
            
            # Gráfico comparativo dos top 5
            if metrica in top_5_df.columns:
                st.write(f"### 📈 Comparação Visual por {metrica}")
                chart_df = top_5_df[['Model', metrica]].copy()
                chart_df = chart_df.set_index('Model')
                st.bar_chart(chart_df)
        
        st.write("### 💾 Salvar Modelos")
        st.write("Selecione abaixo quais modelos você deseja salvar:")
        
        # Interface para salvar cada modelo
        for idx, model in enumerate(top_models_list[:5], 1):
            model_class_name = model.__class__.__name__
            
            with st.expander(f"Modelo {idx}: {model_class_name}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Nome padrão com timestamp para evitar conflitos
                    from datetime import datetime
                    default_name = f"{model_class_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    model_name_input = st.text_input(
                        "Nome do modelo:",
                        value=default_name,
                        key=f"name_{idx}_{model_class_name}"
                    )
                    
                    # Campo para descrição/notas
                    model_notes = st.text_area(
                        "Notas/Descrição (opcional):",
                        key=f"notes_{idx}_{model_class_name}",
                        height=80
                    )
                
                with col2:
                    # Métricas do modelo
                    if top_5_info and idx <= len(top_5_info):
                        metric_value = top_5_info[idx-1].get(metrica, 'N/A')
                        st.metric(metrica, f"{metric_value:.4f}" if isinstance(metric_value, (int, float)) else metric_value)
                
                # Botão para salvar
                if st.button(f"💾 Salvar {model_class_name}", key=f"save_{idx}_{model_class_name}"):
                    try:
                        # Finaliza o modelo antes de salvar
                        finalized_model = finalize_model(model)
                        
                        # Prepara metadados
                        metadata = {
                            "model_type": model_class_name,
                            "metric_used": metrica,
                            "rank": idx,
                            "notes": model_notes if model_notes else ""
                        }
                        
                        # Adiciona métricas disponíveis
                        if top_5_info and idx <= len(top_5_info):
                            for key, value in top_5_info[idx-1].items():
                                if key not in ['Model', 'Rank'] and isinstance(value, (int, float)):
                                    metadata[key] = float(value)
                        
                        # Salva usando o model_store
                        save_model_to_registry(finalized_model, model_name_input, metadata)
                        
                        st.success(f"✅ Modelo '{model_name_input}' salvo com sucesso!")
                        
                        # Exibe informações salvas
                        st.info(f"📁 Salvo em: modelos_salvos/{model_name_input}.pkl")
                        
                    except ValueError as e:
                        st.error(f"❌ Erro: {str(e)}")
                    except Exception as e:
                        st.error(f"❌ Erro ao salvar modelo: {str(e)}")
        
        # Seção para visualizar modelo específico
        st.write("### 🔍 Análise Detalhada do Melhor Modelo")
        
        best_model = top_models_list[0]
        best_model_finalized = finalize_model(best_model)
        
        st.success(f"**Melhor modelo**: {best_model.__class__.__name__}")
        
        model_results = predict_model(best_model_finalized)
        st.write("Resultados do modelo no conjunto de dados de teste:")
        st.dataframe(model_results)

        fig = plt.figure()
        s.plot_model(best_model_finalized, plot='threshold', display_format='streamlit')

        fig = plt.figure()
        s.plot_model(best_model_finalized, plot='confusion_matrix', display_format='streamlit')
        
        # Salva automaticamente o melhor modelo (compatibilidade com código antigo)
        save_model(best_model_finalized, 'best_classification_model')
        st.info("ℹ️ O melhor modelo também foi salvo automaticamente como 'best_classification_model.pkl' (método legado do PyCaret)")


train_model_page = st.Page(
    train_model_view,
    title="Train Model",
    icon="🧠",
)