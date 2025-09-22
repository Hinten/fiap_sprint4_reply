from enum import StrEnum
from typing import List, Self, Union, Any
from datetime import datetime, date, time, timedelta

from sqlalchemy import Sequence, String, ForeignKey, Float, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

import numpy as np

from src.database.tipos_base.database import Database
from src.database.tipos_base.model import Model
from src.database.tipos_base.model_mixins.display import SimpleTableFilter
from src.plots.plot_config import GenericPlot, PlotField, TipoGrafico, OrderBy


class SiglaEstadoEnum(StrEnum):
    AC = "AC"
    AL = "AL"
    AP = "AP"
    AM = "AM"
    BA = "BA"
    CE = "CE"
    DF = "DF"
    ES = "ES"
    GO = "GO"
    MA = "MA"
    MT = "MT"
    MS = "MS"
    MG = "MG"
    PA = "PA"
    PB = "PB"
    PR = "PR"
    PE = "PE"
    PI = "PI"
    RJ = "RJ"
    RN = "RN"
    RS = "RS"
    RO = "RO"
    RR = "RR"
    SC = "SC"
    SP = "SP"
    SE = "SE"
    TO = "TO"
    EX = "EX"  # Exterior

    def __str__(self):

        match self.value:
            case "AC":
                return "Acre"
            case "AL":
                return "Alagoas"
            case "AP":
                return "Amapá"
            case "AM":
                return "Amazonas"
            case "BA":
                return "Bahia"
            case "CE":
                return "Ceará"
            case "DF":
                return "Distrito Federal"
            case "ES":
                return "Espírito Santo"
            case "GO":
                return "Goiás"
            case "MA":
                return "Maranhão"
            case "MT":
                return "Mato Grosso"
            case "MS":
                return "Mato Grosso do Sul"
            case "MG":
                return "Minas Gerais"
            case "PA":
                return "Pará"
            case "PB":
                return "Paraíba"
            case "PR":
                return "Paraná"
            case "PE":
                return "Pernambuco"
            case "PI":
                return "Piauí"
            case "RJ":
                return "Rio de Janeiro"
            case "RN":
                return "Rio Grande do Norte"
            case "RS":
                return "Rio Grande do Sul"
            case "RO":
                return "Rondônia"
            case "RR":
                return "Roraima"
            case "SC":
                return "Santa Catarina"
            case "SP":
                return "São Paulo"
            case "SE":
                return "Sergipe"
            case "TO":
                return "Tocantins"
            case "EX":
                return "Exterior"
            case _:
                return self.value

class Empresa(Model):
    __tablename__ = 'EMPRESA'
    __menu_group__ = "Empresa"
    __menu_order__ = 1
    __database_import_order__ = 1

    id: Mapped[int] = mapped_column(
        Sequence(f"{__tablename__}_SEQ_ID"), primary_key=True, autoincrement=True, nullable=False
    )

    nome: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, info={'label': 'Nome'},
    )

    cnpj: Mapped[str] = mapped_column(
        String(14), nullable=True, unique=True, info={'label': 'CNPJ'},
    )

    logradouro: Mapped[str] = mapped_column(
        String(255), nullable=True, info={'label': 'Logradouro'},
        comment="Ex.: Rua, avenida, travessa, etc."
    )

    numero: Mapped[str] = mapped_column(
        String(255), nullable=True, info={'label': 'Número'},
    )

    bairro: Mapped[str] = mapped_column(
        String(255), nullable=True, info={'label': 'Bairro'},
    )

    cidade: Mapped[str] = mapped_column(
        String(255), nullable=True, info={'label': 'Cidade'},
    )

    estado: Mapped[SiglaEstadoEnum] = mapped_column(
        Enum(SiglaEstadoEnum, length=2), nullable=True, info={'label': 'Estado'},
    )

    cep: Mapped[str] = mapped_column(
        String(8), nullable=True, info={'label': 'CEP'},
    )

    def __str__(self):
        return f"{self.id} - {self.nome}"
