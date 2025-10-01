from src.database.models.sensor import Sensor, LeituraSensor
import streamlit as st
from itertools import islice
from src.dashboard.plots.generic.grafico_linha import get_grafico_linha
from datetime import datetime


@st.fragment(
    run_every=10
)
def grafico_leituras_sensor(sensor_id: int):

    sensor = Sensor.get_from_id(sensor_id)
    leituras_do_sensor = LeituraSensor.get_leituras_for_sensor(sensor_id)

    #gráfico de linha com as leituras_do_sensor
    get_grafico_linha(
        leituras_do_sensor,
        sensor.__str__(),
        sensor.limiar_manutencao_maior,
        sensor.limiar_manutencao_maior,
        show_df=False
    )

    horario = "%d/%m/%Y - %H:%M:%S"

    st.write(f"Atualizado em {datetime.now().strftime(horario)}")



def visualizador_leituras_page():

    st.title('Visualizador de Leituras de Sensors em Tempo Real')
    
    st.write("""
            📡 Esta página exibe gráficos de linha para as leituras de todos os sensores cadastrados no sistema. Os gráficos são atualizados automaticamente a cada 10 segundos, permitindo o monitoramento em tempo real dos dados coletados pelos sensores.
            
📊 Exibição contínua das leituras dos sensores principais:


    🌞 Sensor Lux → Intensidade luminosa.

    🌡️  Sensor Temperatura (°C) → Condições térmicas do ambiente ou equipamento.

    📳 Sensor Vibração → Identificação de oscilações e possíveis falhas mecânicas.
             """)

    todos_sensores_id = [sensor.id for sensor in Sensor.all()]
    if len(todos_sensores_id) == 0:
        st.warning("Nenhum sensor cadastrado.")
        return

    for i in range(0, len(todos_sensores_id), 3):
        grupo = list(islice(todos_sensores_id, i, i + 3))

        colunas = st.columns(3)
        for idx, sensor_id in enumerate(grupo):
            with colunas[idx]:
                grafico_leituras_sensor(sensor_id)
    
    st.write("""
    📈 Benefícios

        🔎 Detecção de falhas antecipada → Identifica padrões incomuns antes que se tornem problemas graves.

        ⚡ Monitoramento em tempo real → Acompanhamento contínuo e confiável.

        🔗 Escalável → Novos sensores podem ser adicionados facilmente.

        📂 Registro histórico → Possibilidade de salvar e analisar dados passados.

        🛠️ Manutenção preditiva → Planejamento eficiente com base em dados reais.
             """)  