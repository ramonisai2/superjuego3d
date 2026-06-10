"""
Stage33 P - analizador de logs de playtest.

Lee los logs de Stage33 O y entrega un resumen corto: si faltan logs, si hubo
errores, cuantas lineas STREAM-BRIDGE aparecieron y que archivo conviene revisar.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List
import re


ERROR_MARKERS = ("Traceback", "ERROR", "[ERROR]", "Exception", "EXCEPTION", "SDL2 not found")


@dataclass
class PlaytestLogSummary:
    path: str
    exists: bool = False
    line_count: int = 0
    info_count: int = 0
    stream_bridge_count: int = 0
    error_count: int = 0
    last_chunk: str = ""
    last_stream_bridge: str = ""
    first_error: str = ""
    last_error: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PlaytestLogAnalysisStatus:
    ok: bool = False
    legacy_checked: bool = False
    bridge_checked: bool = False
    legacy_log_exists: bool = False
    bridge_log_exists: bool = False
    logs_ready_for_comparison: bool = False
    bridge_markers_ready: bool = False
    legacy_error_count: int = 0
    bridge_error_count: int = 0
    bridge_stream_lines: int = 0
    recommendation: str = ""
    legacy_summary: Dict[str, Any] | None = None
    bridge_summary: Dict[str, Any] | None = None
    notes: str = ""
    blocked_reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _read_lines(path: Path) -> List[str]:
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return path.read_text(errors="replace").splitlines()


def summarize_log(path: Path) -> PlaytestLogSummary:
    summary = PlaytestLogSummary(path=str(path))
    summary.exists = path.exists()
    if not summary.exists:
        return summary

    lines = _read_lines(path)
    summary.line_count = len(lines)
    chunk_re = re.compile(r"Chunk:\s*\(([-0-9]+),([-0-9]+)\)")

    for line in lines:
        if "[INFO]" in line:
            summary.info_count += 1
            match = chunk_re.search(line)
            if match:
                summary.last_chunk = f"{match.group(1)},{match.group(2)}"
        if "[STREAM-BRIDGE]" in line:
            summary.stream_bridge_count += 1
            summary.last_stream_bridge = line[-240:]
        if any(marker in line for marker in ERROR_MARKERS):
            summary.error_count += 1
            if not summary.first_error:
                summary.first_error = line[-240:]
            summary.last_error = line[-240:]
    return summary


def analyze_playtest_logs(root: str | None = None) -> Dict[str, Any]:
    status = PlaytestLogAnalysisStatus()
    try:
        base = Path(root).resolve() if root else Path(__file__).resolve().parents[2]
        logs_dir = base / "juego3d_v1_5" / "logs"
        if not logs_dir.exists() and (base / "logs").exists():
            logs_dir = base / "logs"

        legacy = summarize_log(logs_dir / "playtest_opengl_legacy.log")
        bridge = summarize_log(logs_dir / "playtest_opengl_bridge.log")

        status.legacy_checked = True
        status.bridge_checked = True
        status.legacy_log_exists = legacy.exists
        status.bridge_log_exists = bridge.exists
        status.logs_ready_for_comparison = legacy.exists and bridge.exists
        status.bridge_markers_ready = bridge.stream_bridge_count > 0
        status.legacy_error_count = legacy.error_count
        status.bridge_error_count = bridge.error_count
        status.bridge_stream_lines = bridge.stream_bridge_count
        status.legacy_summary = legacy.to_dict()
        status.bridge_summary = bridge.to_dict()

        if not legacy.exists and not bridge.exists:
            status.recommendation = "Ejecuta primero los dos lanzadores de playtest."
            status.notes = "No hay logs de playtest todavia."
        elif not legacy.exists:
            status.recommendation = "Falta ejecutar LANZAR_PLAYTEST_OPENGL_LEGACY_LOG.bat."
            status.notes = "Solo falta el log legacy."
        elif not bridge.exists:
            status.recommendation = "Falta ejecutar LANZAR_PLAYTEST_OPENGL_BRIDGE_LOG.bat."
            status.notes = "Solo falta el log del puente."
        elif legacy.error_count and not bridge.error_count:
            status.recommendation = "Revisar primero OpenGL legacy; el fallo no parece del puente."
            status.notes = "Legacy reporta errores y bridge no."
        elif bridge.error_count and not legacy.error_count:
            status.recommendation = "Mandar playtest_opengl_bridge.log; el fallo parece del puente seguro."
            status.notes = "Bridge reporta errores y legacy no."
        elif bridge.exists and not status.bridge_markers_ready:
            status.recommendation = "Revisar si se uso el lanzador bridge; no hay lineas [STREAM-BRIDGE]."
            status.notes = "El log bridge existe pero no muestra telemetria del puente."
        else:
            status.recommendation = "Comparacion lista; si se sintio bien, seguir a ajustar/activar mas integracion."
            status.notes = "Logs legibles y sin diferencias de error obvias."

        status.ok = status.logs_ready_for_comparison and not status.legacy_error_count and not status.bridge_error_count
    except Exception as exc:
        status.blocked_reason = f"exception: {exc}"
        status.notes = f"playtest log analyzer fallo: {exc}"
    return status.to_dict()


def compact_status(stats: Dict[str, Any]) -> str:
    flags = []
    for key, label in [
        ("legacy_checked", "legacy-check"),
        ("bridge_checked", "bridge-check"),
        ("legacy_log_exists", "legacy-log"),
        ("bridge_log_exists", "bridge-log"),
        ("logs_ready_for_comparison", "compare-ready"),
        ("bridge_markers_ready", "bridge-markers"),
        ("ok", "logsOK"),
    ]:
        if stats.get(key):
            flags.append(label)
    if stats.get("legacy_error_count"):
        flags.append(f"legacyErr{stats.get('legacy_error_count')}")
    if stats.get("bridge_error_count"):
        flags.append(f"bridgeErr{stats.get('bridge_error_count')}")
    if stats.get("bridge_stream_lines"):
        flags.append(f"stream{stats.get('bridge_stream_lines')}")
    return " ".join(flags) if flags else "not-ready"


if __name__ == "__main__":
    stats = analyze_playtest_logs()
    print("Playtest log analysis:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
