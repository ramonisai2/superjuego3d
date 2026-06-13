"""Lectura comun de variables de entorno del juego."""

from __future__ import annotations

import os
from typing import Iterable


TRUE_VALUES = {"1", "true", "yes", "on"}
FALSE_VALUES = {"0", "false", "no", "off"}


def read_env_text(name: str, default: str = "", *, lower: bool = False) -> str:
    value = os.environ.get(name, "")
    text = str(value).strip()
    if not text:
        text = str(default)
    text = text.strip()
    return text.lower() if lower else text


def read_env_bool(
    name: str,
    default: bool = False,
    *,
    true_values: Iterable[str] = TRUE_VALUES,
    false_values: Iterable[str] = FALSE_VALUES,
) -> bool:
    raw = os.environ.get(name, "")
    text = str(raw).strip().lower()
    if not text:
        return bool(default)
    if text in set(true_values):
        return True
    if text in set(false_values):
        return False
    return bool(default)


def read_env_int(name: str, default: int, min_value: int | None = None, max_value: int | None = None) -> int:
    raw = os.environ.get(name, "")
    text = str(raw).strip()
    if not text:
        value = int(default)
    else:
        try:
            value = int(text)
        except ValueError:
            value = int(default)
    if min_value is not None:
        value = max(int(min_value), value)
    if max_value is not None:
        value = min(int(max_value), value)
    return value


def read_env_float(
    name: str,
    default: float,
    min_value: float | None = None,
    max_value: float | None = None,
) -> float:
    raw = os.environ.get(name, "")
    text = str(raw).strip()
    if not text:
        value = float(default)
    else:
        try:
            value = float(text)
        except ValueError:
            value = float(default)
    if min_value is not None:
        value = max(float(min_value), value)
    if max_value is not None:
        value = min(float(max_value), value)
    return value
