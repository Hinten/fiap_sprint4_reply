"""Utility helpers for environment variable parsing."""
from typing import Any
import os


def parse_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    try:
        return str(value).strip().lower() in ("true", "1", "yes", "on")
    except Exception:
        return default


def parse_bool_env(env_var: str, default: bool = False) -> bool:
    """
    Converte variável de ambiente para booleano.

    Aceita: 'true', '1', 'yes', 'on' (case-insensitive) como True
    Qualquer outro valor é False
    """
    value = os.environ.get(env_var)
    return parse_bool(value, default)
