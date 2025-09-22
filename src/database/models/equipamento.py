from typing import List

from sqlalchemy import Sequence, String, ForeignKey, Float, DateTime, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.tipos_base.model import Model

class Equipamento(Model):
    __tablename__ = 'EQUIPAMENTO'
    __menu_group__ = "Equipamento"
    __menu_order__ = 1
    __database_import_order__ = 3

    id: Mapped[int] = mapped_column(
        Sequence(f"{__tablename__}_SEQ_ID"), primary_key=True, autoincrement=True, nullable=False
    )

    nome: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, info={'label': 'Nome'},
    )

    modelo: Mapped[str] =mapped_column(
        String(255), nullable=True, info={'label': 'Modelo'},
    )

    localizacao: Mapped[str] = mapped_column(
        String(255), nullable=True, info={'label': 'Localização'},
    )

    descricao: Mapped[str] = mapped_column(
        Text(2000), nullable=True, info={'label': 'Descrição'},
    )

    observacoes: Mapped[str] = mapped_column(
        Text(2000), nullable=True, info={'label': 'Observações'},
    )

    data_instalacao: Mapped[DateTime] = mapped_column(
        DateTime, nullable=True, info={'label': 'Data de Instalação'},
        comment="Data de instalação do equipamento"
    )

    sensores: Mapped[List['Sensor']] = relationship(
        back_populates='equipamento',
        cascade='all, delete-orphan',
        info={'label': 'Sensores'}
    )

    manutencoes: Mapped[List['ManutencaoEquipamento']] = relationship(
        back_populates='equipamento',
        cascade='all, delete-orphan',
        info={'label': 'Manutenções'}
    )

    def __str__(self):
        return f"{self.id} - {self.nome}"
