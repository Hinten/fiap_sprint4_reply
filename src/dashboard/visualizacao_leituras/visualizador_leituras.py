from src.dashboard.machine_learning.manual import carregar_modelo_e_realizar_previsao
from src.database.models.sensor import Sensor, LeituraSensor, TipoSensor, TipoSensorEnum
import streamlit as st
from itertools import islice
from src.dashboard.plots.generic.grafico_linha import get_grafico_linha
from datetime import datetime, timedelta

from src.database.tipos_base.database import Database

RELOAD_TIMER = 10  # segundos

@st.fragment
def prever_necessidade_de_manutencao(
        sensor_lux_id: int,
        sensor_temperatura_id: int,
        sensor_vibracao_id: int,
):

    with Database.get_session() as session:
        ultima_leitura_lux = session.query(LeituraSensor).filter(LeituraSensor.sensor_id == sensor_lux_id).order_by(LeituraSensor.data_leitura.desc()).first()
        ultima_leitura_temperatura = session.query(LeituraSensor).filter(LeituraSensor.sensor_id == sensor_temperatura_id).order_by(LeituraSensor.data_leitura.desc()).first()
        ultima_leitura_vibracao = session.query(LeituraSensor).filter(LeituraSensor.sensor_id == sensor_vibracao_id).order_by(LeituraSensor.data_leitura.desc()).first()

    if not ultima_leitura_lux or not ultima_leitura_temperatura or not ultima_leitura_vibracao:
        st.warning("Não há leituras suficientes para fazer a previsão de manutenção.")
        return

    # Exibir as últimas leituras
    st.subheader("Últimas Leituras dos Sensores Selecionados")
    st.write(f"**Sensor Lux:** {ultima_leitura_lux.valor:.2f} (em {ultima_leitura_lux.data_leitura.strftime('%d/%m/%Y %H:%M:%S')})")
    st.write(f"**Sensor Temperatura (°C):** {ultima_leitura_temperatura.valor:.2f} (em {ultima_leitura_temperatura.data_leitura.strftime('%d/%m/%Y %H:%M:%S')})")
    st.write(f"**Sensor Vibração:** {ultima_leitura_vibracao.valor:.2f} (em {ultima_leitura_vibracao.data_leitura.strftime('%d/%m/%Y %H:%M:%S')})")

    carregar_modelo_e_realizar_previsao(
        ultima_leitura_lux.valor,
        ultima_leitura_temperatura.valor,
        ultima_leitura_vibracao.valor
    )



@st.fragment
def prever_necessidade_manutencao():
    st.divider()
    st.title("🔧 Prever Necessidade de Manutenção")
    st.write(
        "Selecione os sensores correspondentes para prever a necessidade de manutenção com base nas últimas leituras."
    )

    with Database.get_session() as session:
        sensores = session.query(Sensor).all()
        tipos = session.query(TipoSensor).all()

        # Get TipoSensor instances for each type
        tipo_lux = next((t for t in tipos if t.tipo == TipoSensorEnum.LUX), None)
        tipo_temperatura = next((t for t in tipos if t.tipo == TipoSensorEnum.TEMPERATURA), None)
        tipo_vibracao = next((t for t in tipos if t.tipo == TipoSensorEnum.VIBRACAO), None)

        # Filter sensors by their tipo_sensor_id (assuming foreign key relationship)
        sensor_lux_option = [s for s in sensores if s.tipo_sensor_id == (tipo_lux.id if tipo_lux else None)]
        sensor_temperatura_option = [s for s in sensores if s.tipo_sensor_id == (tipo_temperatura.id if tipo_temperatura else None)]
        sensor_vibracao_option = [s for s in sensores if s.tipo_sensor_id == (tipo_vibracao.id if tipo_vibracao else None)]

    col1, col2, col3 = st.columns(3)
    with col1:
        sensor_lux = st.selectbox(
            "Sensor Lux",
            options=sensor_lux_option,
            format_func=lambda s: s.__str__(),
        )
    with col2:
        sensor_temperatura = st.selectbox(
            "Sensor Temperatura (°C)",
            options=sensor_temperatura_option,
            format_func=lambda s: s.__str__(),
        )
    with col3:
        sensor_vibracao = st.selectbox(
            "Sensor Vibração",
            options=sensor_vibracao_option,
            format_func=lambda s: s.__str__(),
        )

    prever_necessidade_de_manutencao(
        sensor_lux.id,
        sensor_temperatura.id,
        sensor_vibracao.id
    )



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

    prever_necessidade_manutencao()