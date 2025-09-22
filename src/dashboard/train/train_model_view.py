import streamlit as st

from pycaret.classification import *

from src.machine_learning.dateset_manipulation import get_dataframe_leituras_sensores

import seaborn as sns
import matplotlib.pyplot as plt

@st.cache_resource
def treinar_e_comparar_modelos(s, metrica, turbo):
    best_models = s.compare_models(n_select=5, sort=metrica, fold=5, turbo=turbo)
    compare_df = pull()
    st.write("Resumo da comparação dos modelos:")
    st.dataframe(compare_df)
    return best_models

def train_model_view():
    st.title('Treinando a IA com Pycaret')

    use_gpu = st.checkbox('Usar GPU?', value=True)

    df = get_dataframe_leituras_sensores()

    if df.empty:
        st.warning("O DataFrame está vazio. Verifique se há dados disponíveis.")
        return

    target_column = 'Manutencao'

    df[target_column] = df[target_column].astype(bool)
    st.write(df.head())
    st.write(df.dtypes)

    train_dataset = df.drop(columns=['data_leitura'])

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

    s = setup(data=train_dataset, target=target_column, session_id=123, use_gpu=use_gpu, train_size=0.7, html=True)

    # Puxa o resumo do setup
    setup_summary = pull()

    st.dataframe(setup_summary)

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

    best_models = None

    if st.button('Treinar e comparar modelos'):
        with st.spinner("Treinando modelos (este processo pode demorar um pouco)..."):
            best_models = s.compare_models(n_select=5, sort=metrica, fold=5, turbo=turbo)
            compare_df = pull()
            st.write("Resumo da comparação dos modelos:")
            st.dataframe(compare_df)

    if best_models:
        st.write("Top 5 modelos:")

        modelo_selected = st.selectbox(
            'Selecione o modelo para visualizar as métricas',
            best_models,
            format_func=lambda model: model.__str__(),
        )

        # s.evaluate_model(modelo_selected)

        if modelo_selected:

            col1, col2, col3 = st.columns(3)

            with col1:
                fig = plt.figure()
                s.plot_model(modelo_selected, plot='auc', display_format='streamlit')
                # st.pyplot(fig)

            with col2:
                fig = plt.figure()
                s.plot_model(modelo_selected, plot='confusion_matrix', display_format='streamlit')
            with col3:
                fig = plt.figure()
                s.plot_model(modelo_selected, plot = 'feature', display_format='streamlit')


train_model_page = st.Page(
    train_model_view,
    title="Train Model",
    icon="🧠",
)