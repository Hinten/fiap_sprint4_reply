from src.database.models.sensor import Sensor, LeituraSensor
import streamlit as st
from itertools import islice
from src.dashboard.plots.generic.grafico_linha import get_grafico_linha
from datetime import datetime, timedelta

RELOAD_TIMER = 60  # segundos

@st.fragment(
    run_every=RELOAD_TIMER
)
def grafico_leituras_sensor(sensor_id: int, periodo: int | None = None):

    sensor = Sensor.get_from_id(sensor_id)
    if periodo is None:
        leituras_do_sensor = LeituraSensor.get_leituras_for_sensor(sensor_id)
    else:
        data_inicial = datetime.now() - timedelta(minutes=periodo)
        leituras_do_sensor = LeituraSensor.get_leituras_for_sensor(sensor_id, data_inicial=data_inicial)

    if len(leituras_do_sensor) == 0:
        st.warning(f"Nenhuma leitura encontrada para o sensor {sensor.__str__()} no período selecionado.")
        return

    #gráfico de linha com as leituras_do_sensor
    get_grafico_linha(
        leituras=leituras_do_sensor,
        title=sensor.__str__(),
        limiar_manutencao_maior=sensor.limiar_manutencao_maior,
        limiar_manutencao_menor=sensor.limiar_manutencao_menor,
        show_df=False
    )

    horario = "%d/%m/%Y - %H:%M:%S"

    st.write(f"Atualizado em {datetime.now().strftime(horario)}")



def visualizador_leituras_page():

    st.title('Visualizador de Leituras de Sensors em Tempo Real')
    
    st.write(f"""
    📡 Esta página exibe gráficos de linha para as leituras de todos os sensores cadastrados no sistema. Os gráficos são atualizados automaticamente a cada {RELOAD_TIMER} segundos, permitindo o monitoramento em tempo real dos dados coletados pelos sensores.
            
    📊 Exibição contínua das leituras dos sensores principais:


    🌞 Sensor Lux → Intensidade luminosa.

    🌡️  Sensor Temperatura (°C) → Condições térmicas do ambiente ou equipamento.

    📳 Sensor Vibração → Identificação de oscilações e possíveis falhas mecânicas.
             """)

    periodo = st.selectbox(
        "Período da leitura",
        options=[10, 60, 120, None],
        format_func = lambda x: "Todo Período" if x is None else f"Últimos {x} minutos",
        index=1,
    )


    todos_sensores_id = [sensor.id for sensor in Sensor.all()]
    if len(todos_sensores_id) == 0:
        st.warning("Nenhum sensor cadastrado.")
        return

    for i in range(0, len(todos_sensores_id), 3):
        grupo = list(islice(todos_sensores_id, i, i + 3))

        colunas = st.columns(3)
        for idx, sensor_id in enumerate(grupo):
            with colunas[idx]:
                grafico_leituras_sensor(sensor_id, periodo)
    
    st.write("""
    📈 Benefícios

        🔎 Detecção de falhas antecipada → Identifica padrões incomuns antes que se tornem problemas graves.

        ⚡ Monitoramento em tempo real → Acompanhamento contínuo e confiável.

        🔗 Escalável → Novos sensores podem ser adicionados facilmente.

        📂 Registro histórico → Possibilidade de salvar e analisar dados passados.

        🛠️ Manutenção preditiva → Planejamento eficiente com base em dados reais.
             """)  