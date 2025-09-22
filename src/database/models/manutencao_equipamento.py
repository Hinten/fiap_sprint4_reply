from sqlalchemy import Sequence, ForeignKey, Float, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models.equipamento import Equipamento
from src.database.tipos_base.model import Model
from src.database.tipos_base.model_mixins.display import SimpleTableFilter


class ManutencaoEquipamento(Model):
    __tablename__ = 'MANUTENCAO_EQUIPAMENTO'
    __menu_group__ = "Equipamento"
    __menu_order__ = 2
    __database_import_order__ = 3

    @classmethod
    def display_name(cls) -> str:
        return "Manutenção de Equipamento"

    @classmethod
    def display_name_plural(cls) -> str:
        return "Manutenções de Equipamentos"

    __table_view_filters__ = [
        SimpleTableFilter(field='equipamento_id', label='Equipamento', operator='==')
    ]

    id: Mapped[int] = mapped_column(
        Sequence(f"{__tablename__}_SEQ_ID"), primary_key=True, autoincrement=True, nullable=False
    )

    equipamento_id: Mapped[int] = mapped_column(
        ForeignKey('EQUIPAMENTO.id'), nullable=False, info={'label': 'Equipamento'},
    )

    equipamento: Mapped[Equipamento] = relationship('Equipamento', back_populates='manutencoes')

    data_previsao_manutencao: Mapped[DateTime] = mapped_column(
        DateTime, nullable=True, info={'label': 'Data Prevista da Manutenção'},
        comment="Data prevista para a próxima manutenção do equipamento"
    )

    motivo: Mapped[str] = mapped_column(
        Text(2000), nullable=True, info={'label': 'Motivo da Manutenção'},
        comment="Motivo pelo qual a manutenção será realizada no equipamento"
    )

    data_inicio_manutencao: Mapped[DateTime] = mapped_column(
        DateTime, nullable=True, info={'label': 'Data do inicio da Manutenção'},
        comment="Data em que a manutenção foi realizada no equipamento"
    )

    data_fim_manutencao: Mapped[DateTime] = mapped_column(
        DateTime, nullable=True, info={'label': 'Data do fim da Manutenção'},
        comment="Data em que a manutenção foi finalizada no equipamento"
    )

    descricao: Mapped[str] = mapped_column(
        Text(2000), nullable=True, info={'label': 'Descrição'},
        comment="Descrição detalhada da manutenção realizada"
    )

    observacoes: Mapped[str] = mapped_column(
        Text(2000), nullable=True, info={'label': 'Observações'},
        comment="Observações adicionais sobre a manutenção"
    )

    custo: Mapped[float] = mapped_column(
        Float, nullable=True, info={'label': 'Custo'},
    )

    def __str__(self):
        return f"{self.id} - {self.equipamento.nome} - {self.data_inicio_manutencao} a {self.data_fim_manutencao}"