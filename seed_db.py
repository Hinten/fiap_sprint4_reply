from datetime import datetime, timedelta

from src.database.tipos_base.database import Database
from src.database.generator.criar_sensores import criar_sensores_padrao
from src.database.generator.gerar_sensores_e_dados import criar_dados_sample
from src.database.models.sensor import LeituraSensor


def main():
    # 1) Inicializa SQLite local (cria ./database.db) e tabelas
    Database.init_sqlite()
    Database.create_all_tables()

    # 2) Cria sensores padrão (Lux, Temperatura, Vibração)
    sensores = criar_sensores_padrao()
    print(f"Sensores prontos: {len(sensores)}")

    # 3) Gera leituras de 7 dias com ~1000 pontos por sensor (ajuste se quiser)
    inicio = datetime.now() - timedelta(days=7)
    fim = datetime.now()
    total_leituras = 1000

    sensores_e_leituras = criar_dados_sample(
        data_inicial=inicio,
        data_final=fim,
        total_leituras=total_leituras,
    )

    # 4) Persiste leituras
    total = 0
    with Database.get_session() as s:
        for sensor, leituras in sensores_e_leituras:
            for leitura in leituras:
                # leitura é um LeituraSensor já com sensor_id e data/valor
                assert isinstance(leitura, LeituraSensor)
                s.add(leitura)
                total += 1
        s.commit()

    print(f"Base populada! Leituras inseridas: {total}")


if __name__ == "__main__":
    main()
