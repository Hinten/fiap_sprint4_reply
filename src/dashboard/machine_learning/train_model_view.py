import streamlit as st
from pycaret.classification import *
from src.machine_learning.dateset_manipulation import get_dataframe_leituras_sensores
import seaborn as sns
import matplotlib.pyplot as plt


def train_model_view():
    st.title('Treinando a IA com Pycaret')

    use_gpu = st.checkbox('Usar GPU?', value=True)

    df = get_dataframe_leituras_sensores()

    if df.empty:
        st.warning("O DataFrame está vazio. Verifique se há dados disponíveis.")
        return

    target_column = 'Manutencao'

    train_dataset = df.drop(columns=['data_leitura'])
    train_dataset[target_column] = train_dataset[target_column].apply(lambda x: bool(x))
    st.write(train_dataset.head())
    st.write(train_dataset.dtypes)


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

    _best_models = None

    if st.button('Treinar e comparar modelos'):

        with st.spinner("Treinando modelos (este processo pode demorar um pouco)..."):
            _best_models = s.compare_models(n_select=1, sort=metrica, fold=5, turbo=turbo)
            compare_df = pull()
            st.write("Resumo da comparação dos modelos:")
            st.dataframe(compare_df)

    if _best_models:

        best_model = finalize_model(_best_models)
        st.success(f"✅ Melhor modelo selecionado:\n\n**{_best_models.__str__()}**")

        model_results = predict_model(best_model)
        st.write("Resultados do modelo no conjunto de dados de teste:")
        st.dataframe(model_results)

        fig = plt.figure()
        s.plot_model(best_model, plot='threshold', display_format='streamlit')

        fig = plt.figure()
        s.plot_model(best_model, plot='confusion_matrix', display_format='streamlit')

        save_model(best_model, 'best_classification_model')
        st.success("Modelo salvo como 'best_classification_model.pkl'")


train_model_page = st.Page(
    train_model_view,
    title="Train Model",
    icon="🧠",
)