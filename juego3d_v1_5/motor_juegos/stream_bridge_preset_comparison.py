"""
Stage33 S - comparador de presets del puente seguro.

Lee logs separados de safe, balanced y aggressive para decidir que perfil conviene
seguir probando sin cambiar el valor por defecto del juego.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List
import re

from motor_juegos.playtest_log_analyzer import summarize_log


PRESET_LOGS = {
    "safe": "playtest_opengl_bridge_safe.log",
    "balanced": "playtest_opengl_bridge_balanced.log",
    "aggressive": "playtest_opengl_bridge_aggressive.log",
}


@dataclass
class PresetLogSummary:
    preset: str
    path: str
    exists: bool = False
    line_count: int = 0
    error_count: int = 0
    stream_bridge_count: int = 0
    max_queue: int = 0
    max_pending: int = 0
    last_req: int = 0
    last_lod: int = 0
    last_free_detail: int = 0
    last_free_lod: int = 0
    last_cancel: int = 0
    score: int = 999999
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PresetComparisonStatus:
    ok: bool = False
    logs_dir: str = ""
    presets_checked: int = 0
    logs_found: int = 0
    logs_ready_for_comparison: bool = False
    best_preset: str = ""
    action_code: str = ""
    action_label: str = ""
    recommendation: str = ""
    preset_summaries: List[Dict[str, Any]] | None = None
    blocked_reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _read_lines(path: Path) -> List[str]:
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return path.read_text(errors="replace").splitlines()


def _parse_stream_numbers(line: str) -> Dict[str, int]:
    values: Dict[str, int] = {}
    for key, value in re.findall(r"([A-Za-z]+)=(-?\d+)", line):
        values[key.lower()] = int(value)
    return values


def summarize_preset_log(preset: str, path: Path) -> PresetLogSummary:
    base = summarize_log(path)
    summary = PresetLogSummary(
        preset=preset,
        path=str(path),
        exists=base.exists,
        line_count=base.line_count,
        error_count=base.error_count,
        stream_bridge_count=base.stream_bridge_count,
    )
    if not path.exists():
        summary.notes = "Falta ejecutar este playtest."
        return summary

    last_values: Dict[str, int] = {}
    for line in _read_lines(path):
        if "[STREAM-BRIDGE]" not in line:
            continue
        values = _parse_stream_numbers(line)
        if "queue" in values:
            summary.max_queue = max(summary.max_queue, values["queue"])
        if "pending" in values:
            summary.max_pending = max(summary.max_pending, values["pending"])
        last_values.update(values)

    summary.last_req = last_values.get("req", 0)
    summary.last_lod = last_values.get("lod", 0)
    summary.last_free_detail = last_values.get("freed", 0)
    summary.last_free_lod = last_values.get("freel", 0)
    summary.last_cancel = last_values.get("cancel", 0)

    summary.score = (
        summary.error_count * 10000
        + summary.max_queue * 20
        + summary.max_pending * 15
        + max(0, 8 - summary.stream_bridge_count) * 25
    )
    if summary.stream_bridge_count <= 0:
        summary.score += 500
        summary.notes = "El log existe, pero no tiene telemetria [STREAM-BRIDGE]."
    elif summary.error_count:
        summary.notes = "Tiene errores; revisar antes de elegir este perfil."
    else:
        summary.notes = "Log legible para comparar."
    return summary


def _find_logs_dir(root: str | None) -> Path:
    base = Path(root).resolve() if root else Path(__file__).resolve().parents[2]
    logs_dir = base / "juego3d_v1_5" / "logs"
    if not logs_dir.exists() and (base / "logs").exists():
        logs_dir = base / "logs"
    return logs_dir


def compare_stream_bridge_presets(root: str | None = None) -> Dict[str, Any]:
    status = PresetComparisonStatus()
    try:
        logs_dir = _find_logs_dir(root)
        summaries = [
            summarize_preset_log(preset, logs_dir / filename)
            for preset, filename in PRESET_LOGS.items()
        ]
        found = [item for item in summaries if item.exists]
        usable = [item for item in found if item.error_count == 0 and item.stream_bridge_count > 0]
        missing = [item.preset for item in summaries if not item.exists]

        status.logs_dir = str(logs_dir)
        status.presets_checked = len(summaries)
        status.logs_found = len(found)
        status.logs_ready_for_comparison = len(found) == len(summaries)
        status.preset_summaries = [item.to_dict() for item in summaries]

        if not found:
            status.action_code = "RUN_SAFE_FIRST"
            status.action_label = "Ejecutar preset safe primero"
            status.recommendation = "Corre LANZAR_PLAYTEST_OPENGL_BRIDGE_SAFE_LOG.bat; luego balanced."
        elif missing:
            status.action_code = "RUN_MISSING"
            status.action_label = "Faltan perfiles por probar"
            status.recommendation = "Falta ejecutar: " + ", ".join(missing) + "."
        elif not usable:
            status.action_code = "REVIEW_ERRORS"
            status.action_label = "Revisar errores antes de elegir preset"
            status.recommendation = "Hay logs, pero ninguno esta limpio con telemetria del puente."
        else:
            best = sorted(usable, key=lambda item: (item.score, item.preset != "balanced", item.preset))[0]
            status.best_preset = best.preset
            status.ok = True
            if best.preset == "safe":
                status.action_code = "KEEP_SAFE"
                status.action_label = "Mantener safe como base"
                status.recommendation = "Safe es el candidato mas estable por ahora."
            elif best.preset == "balanced":
                status.action_code = "CANDIDATE_BALANCED"
                status.action_label = "Balanced puede ser candidato por defecto"
                status.recommendation = "Balanced se ve apto; probar sensacion/FPS antes de hacerlo default."
            else:
                status.action_code = "AGGRESSIVE_FOR_TESTS"
                status.action_label = "Aggressive solo para pruebas"
                status.recommendation = "Aggressive esta limpio, pero conviene dejarlo como modo de prueba."
    except Exception as exc:
        status.blocked_reason = f"exception: {exc}"
        status.recommendation = f"Comparador de presets fallo: {exc}"
    return status.to_dict()


def compact_status(stats: Dict[str, Any]) -> str:
    flags = [
        f"found{stats.get('logs_found', 0)}/{stats.get('presets_checked', 0)}",
        str(stats.get("action_code") or "not-ready"),
    ]
    if stats.get("logs_ready_for_comparison"):
        flags.append("compare-ready")
    if stats.get("best_preset"):
        flags.append(f"best={stats.get('best_preset')}")
    if stats.get("ok"):
        flags.append("presetCompareOK")
    return " ".join(flags)


if __name__ == "__main__":
    stats = compare_stream_bridge_presets()
    print("Stream bridge presets:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
