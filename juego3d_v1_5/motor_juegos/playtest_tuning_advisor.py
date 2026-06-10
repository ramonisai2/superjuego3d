"""
Stage33 Q - recomendador de ajustes segun logs de playtest.

No cambia parametros automaticamente. Lee el resultado del analizador de logs y
devuelve una accion concreta para el siguiente paso.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict

from motor_juegos.playtest_log_analyzer import analyze_playtest_logs


@dataclass
class PlaytestTuningAdvice:
    ok: bool = False
    analysis_checked: bool = False
    action_code: str = ""
    action_label: str = ""
    priority: str = "normal"
    send_log_hint: str = ""
    can_continue_to_next_stage: bool = False
    should_adjust_bridge: bool = False
    suggested_change: str = ""
    notes: str = ""
    blocked_reason: str = ""
    analysis: Dict[str, Any] | None = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _summary_value(summary: Dict[str, Any] | None, key: str, default: Any = 0) -> Any:
    if not isinstance(summary, dict):
        return default
    return summary.get(key, default)


def advise_from_playtest_logs(root: str | None = None) -> Dict[str, Any]:
    advice = PlaytestTuningAdvice()
    try:
        analysis = analyze_playtest_logs(root=root)
        advice.analysis_checked = True
        advice.analysis = analysis

        legacy_exists = bool(analysis.get("legacy_log_exists"))
        bridge_exists = bool(analysis.get("bridge_log_exists"))
        legacy_errors = int(analysis.get("legacy_error_count") or 0)
        bridge_errors = int(analysis.get("bridge_error_count") or 0)
        bridge_markers = bool(analysis.get("bridge_markers_ready"))
        bridge_stream_lines = int(analysis.get("bridge_stream_lines") or 0)
        legacy_info = int(_summary_value(analysis.get("legacy_summary"), "info_count", 0) or 0)
        bridge_info = int(_summary_value(analysis.get("bridge_summary"), "info_count", 0) or 0)

        if not legacy_exists and not bridge_exists:
            advice.action_code = "RUN_BOTH"
            advice.action_label = "Ejecutar ambos playtests primero"
            advice.send_log_hint = "Todavia no mandes logs; aun no existen."
            advice.suggested_change = "Primero corre legacy y luego bridge con los lanzadores de playtest."
        elif not legacy_exists:
            advice.action_code = "RUN_LEGACY"
            advice.action_label = "Falta playtest OpenGL legacy"
            advice.send_log_hint = "No mandes logs todavia; falta la base de comparacion."
            advice.suggested_change = "Ejecuta LANZAR_PLAYTEST_OPENGL_LEGACY_LOG.bat."
        elif not bridge_exists:
            advice.action_code = "RUN_BRIDGE"
            advice.action_label = "Falta playtest OpenGL + puente seguro"
            advice.send_log_hint = "No mandes logs todavia; falta el modo experimental."
            advice.suggested_change = "Ejecuta LANZAR_PLAYTEST_OPENGL_BRIDGE_LOG.bat."
        elif legacy_errors and not bridge_errors:
            advice.action_code = "FIX_LEGACY"
            advice.action_label = "Corregir OpenGL estable antes del puente"
            advice.priority = "high"
            advice.send_log_hint = "Manda playtest_opengl_legacy.log."
            advice.suggested_change = "No ajustar el puente todavia; el fallo ocurre en la base estable."
            advice.should_adjust_bridge = False
        elif bridge_errors and not legacy_errors:
            advice.action_code = "FIX_BRIDGE"
            advice.action_label = "Corregir puente seguro"
            advice.priority = "high"
            advice.send_log_hint = "Manda playtest_opengl_bridge.log."
            advice.suggested_change = "Revisar release/cancel/request del puente y reducir cambios por frame si hay tirones o errores."
            advice.should_adjust_bridge = True
        elif bridge_exists and not bridge_markers:
            advice.action_code = "RERUN_BRIDGE_FLAG"
            advice.action_label = "Repetir bridge con feature flag correcto"
            advice.priority = "normal"
            advice.send_log_hint = "Manda el log bridge solo si el lanzador correcto tambien sale sin [STREAM-BRIDGE]."
            advice.suggested_change = "Usar LANZAR_PLAYTEST_OPENGL_BRIDGE_LOG.bat para asegurar JUEGO_STREAM_BRIDGE_SAFE=1."
        elif bridge_info < max(3, legacy_info // 3):
            advice.action_code = "RERUN_LONGER"
            advice.action_label = "Repetir prueba por mas tiempo"
            advice.send_log_hint = "No mandes logs todavia si la prueba duro muy poco."
            advice.suggested_change = "Camina 1-2 minutos cruzando chunks en ambos modos."
        elif bridge_stream_lines > 0:
            advice.action_code = "ENABLE_NEXT"
            advice.action_label = "Listo para siguiente integracion"
            advice.can_continue_to_next_stage = True
            advice.send_log_hint = "No hace falta mandar logs si la sensacion/FPS fue buena."
            advice.suggested_change = "Seguir a Stage33 R: presupuestos configurables del puente."
        else:
            advice.action_code = "REVIEW_MANUAL"
            advice.action_label = "Revision manual"
            advice.send_log_hint = "Manda ambos logs si algo se sintio raro."
            advice.suggested_change = "Comparar sensacion, FPS y carga de chunks antes de avanzar."

        advice.ok = advice.analysis_checked and bool(advice.action_code)
        advice.notes = "Recomendacion generada desde logs de playtest."
    except Exception as exc:
        advice.blocked_reason = f"exception: {exc}"
        advice.notes = f"playtest tuning advisor fallo: {exc}"
    return advice.to_dict()


def compact_status(stats: Dict[str, Any]) -> str:
    flags = []
    if stats.get("analysis_checked"):
        flags.append("analysis")
    if stats.get("action_code"):
        flags.append(str(stats.get("action_code")))
    if stats.get("should_adjust_bridge"):
        flags.append("adjust-bridge")
    if stats.get("can_continue_to_next_stage"):
        flags.append("next")
    if stats.get("ok"):
        flags.append("adviceOK")
    return " ".join(flags) if flags else "not-ready"


if __name__ == "__main__":
    stats = advise_from_playtest_logs()
    print("Playtest tuning advice:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
