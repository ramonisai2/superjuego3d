"""Analizador de logs [PERF] para tirones al moverse."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List
import re


PERF_LOGS = {
    "legacy": "perf_movimiento_opengl_legacy.log",
    "bridge": "perf_movimiento_opengl_bridge_safe.log",
}


@dataclass
class PerfFileSummary:
    name: str
    path: str
    exists: bool = False
    perf_lines: int = 0
    avg_fps: float = 0.0
    min_fps: float = 0.0
    max_frame_ms: float = 0.0
    max_update_ms: float = 0.0
    max_chunk_ms: float = 0.0
    max_chunk_lod_ms: float = 0.0
    max_chunk_compile_ms: float = 0.0
    max_render3d_ms: float = 0.0
    max_flip_ms: float = 0.0
    likely_bottleneck: str = ""
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _read_lines(path: Path) -> List[str]:
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return path.read_text(errors="replace").splitlines()


def _parse_perf_line(line: str) -> Dict[str, float]:
    values: Dict[str, float] = {}
    for key, value in re.findall(r"([A-Za-z0-9_]+)=([0-9]+(?:\.[0-9]+)?)", line):
        values[key] = float(value)
    return values


def summarize_perf_file(name: str, path: Path) -> PerfFileSummary:
    summary = PerfFileSummary(name=name, path=str(path), exists=path.exists())
    if not summary.exists:
        summary.notes = "Falta ejecutar este log de movimiento."
        return summary

    fps_values: List[float] = []
    section_max = {
        "frame": 0.0,
        "update": 0.0,
        "chunk_total": 0.0,
        "chunk_lod": 0.0,
        "chunk_compile": 0.0,
        "render3d": 0.0,
        "flip": 0.0,
    }
    for line in _read_lines(path):
        if "[PERF]" not in line:
            continue
        summary.perf_lines += 1
        values = _parse_perf_line(line)
        if "fps" in values:
            fps_values.append(values["fps"])
        for key in section_max:
            if key in values:
                section_max[key] = max(section_max[key], values[key])

    if fps_values:
        summary.avg_fps = sum(fps_values) / len(fps_values)
        summary.min_fps = min(fps_values)
    summary.max_frame_ms = section_max["frame"]
    summary.max_update_ms = section_max["update"]
    summary.max_chunk_ms = section_max["chunk_total"]
    summary.max_chunk_lod_ms = section_max["chunk_lod"]
    summary.max_chunk_compile_ms = section_max["chunk_compile"]
    summary.max_render3d_ms = section_max["render3d"]
    summary.max_flip_ms = section_max["flip"]

    candidates = {
        "chunks/update": summary.max_chunk_ms,
        "chunks LOD": summary.max_chunk_lod_ms,
        "chunks detalle/upload": summary.max_chunk_compile_ms,
        "render3d": summary.max_render3d_ms,
        "flip/vsync/driver": summary.max_flip_ms,
        "update general": summary.max_update_ms,
    }
    summary.likely_bottleneck = max(candidates, key=candidates.get)
    if summary.perf_lines <= 0:
        summary.notes = "El log existe, pero no tiene lineas [PERF]."
    elif summary.max_chunk_lod_ms >= 8.0:
        summary.notes = "La creacion de LOD simple parece causar tirones."
    elif summary.max_chunk_compile_ms >= 8.0:
        summary.notes = "La subida/compilacion del chunk detallado parece causar tirones."
    elif summary.max_chunk_ms >= 8.0:
        summary.notes = "Los chunks parecen causar tirones al moverse."
    elif summary.max_render3d_ms >= 8.0:
        summary.notes = "El dibujado 3D parece pesado."
    elif summary.max_flip_ms >= 8.0:
        summary.notes = "El bloqueo de presentacion/driver puede estar pesando."
    else:
        summary.notes = "No hay un pico obvio en este resumen."
    return summary


def _find_logs_dir(root: str | None) -> Path:
    base = Path(root).resolve() if root else Path(__file__).resolve().parents[2]
    logs_dir = base / "juego3d_v1_5" / "logs"
    if not logs_dir.exists() and (base / "logs").exists():
        logs_dir = base / "logs"
    return logs_dir


def analyze_movement_perf_logs(root: str | None = None) -> Dict[str, Any]:
    logs_dir = _find_logs_dir(root)
    summaries = [
        summarize_perf_file(name, logs_dir / filename)
        for name, filename in PERF_LOGS.items()
    ]
    found = [item for item in summaries if item.exists]
    ready = all(item.exists and item.perf_lines > 0 for item in summaries)
    recommendation = "Ejecuta LANZAR_PERF_MOVIMIENTO_OPENGL_LEGACY_LOG.bat primero."
    if found and not ready:
        recommendation = "Falta un log o faltan lineas [PERF]; corre ambos lanzadores de movimiento."
    if ready:
        worst = max(summaries, key=lambda item: item.max_frame_ms)
        recommendation = (
            f"Mayor pico en {worst.name}: {worst.likely_bottleneck}. "
            "Optimizar esa zona antes de insistir con Vulkan."
        )
    return {
        "ok": ready,
        "logs_dir": str(logs_dir),
        "logs_found": len(found),
        "logs_checked": len(summaries),
        "recommendation": recommendation,
        "summaries": [item.to_dict() for item in summaries],
    }


def compact_status(stats: Dict[str, Any]) -> str:
    status = f"perfLogs {stats.get('logs_found', 0)}/{stats.get('logs_checked', 0)}"
    if stats.get("ok"):
        status += " perfCompareOK"
    return status


if __name__ == "__main__":
    stats = analyze_movement_perf_logs()
    print("Movement perf logs:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
