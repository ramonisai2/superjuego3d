"""Analizador de logs de presets graficos.

Lee logs/preset_runtime_samples.log y resume FPS, escala adaptativa y carga
renderizada para comparar low/balanced/high sin revisar el archivo a mano.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List
import os
import re


LOG_NAME = "preset_runtime_samples.log"
REPORT_NAME = "preset_runtime_report.txt"
RECOMMENDED_PRESET_NAME = "recommended_graphics_preset.txt"
VALID_PRESETS = {"low", "balanced", "high"}
EXPECTED_PRESETS = ("low", "balanced", "high")
MIN_SAMPLES_PER_PRESET = 4
SEVERE_DROP_FPS = 24.0
WORST_SAMPLE_LIMIT = 6
HIGH_VERTICES_HINT = 12000.0
HIGH_LOD_CHUNKS_HINT = 12.0
HIGH_UPLOADS_HINT = 2.0


@dataclass
class PresetRuntimeSummary:
    preset: str
    samples: int = 0
    avg_fps: float = 0.0
    min_fps: float = 0.0
    avg_scale: float = 0.0
    avg_vertices: float = 0.0
    avg_visible_vertices: float = 0.0
    avg_visible_lod_vertices: float = 0.0
    avg_visible_detail_vertices: float = 0.0
    avg_uploads: float = 0.0
    avg_chunk_distance: float = 0.0
    avg_chunk_extra: float = 0.0
    avg_hidden_chunks: float = 0.0
    avg_hidden_entities: float = 0.0
    avg_stream_ms: float = 0.0
    score: float = 0.0
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _find_logs_dir(root: str | None = None) -> Path:
    base = Path(root).resolve() if root else Path(__file__).resolve().parents[2]
    logs_dir = base / "juego3d_v1_5" / "logs"
    if not logs_dir.exists() and (base / "logs").exists():
        logs_dir = base / "logs"
    return logs_dir


def _parse_line(line: str) -> Dict[str, Any]:
    values: Dict[str, Any] = {}
    for key, value in re.findall(r"([A-Za-z0-9_]+)=([A-Za-z0-9_./-]+)", line):
        if key in {"preset", "world", "auto", "resFMP", "session", "event"}:
            values[key] = value
            continue
        try:
            values[key] = float(value)
        except ValueError:
            values[key] = value
    return values


def _average(items: List[float]) -> float:
    return sum(items) / len(items) if items else 0.0


def _positive_values(rows: List[Dict[str, Any]], key: str) -> List[float]:
    return [
        float(row.get(key, 0.0) or 0.0)
        for row in rows
        if key in row and float(row.get(key, 0.0) or 0.0) > 0.0
    ]


def _visible_or_upload_vertices(row: Dict[str, Any]) -> float:
    visible = float(row.get("visibleVerts", 0.0) or 0.0)
    if visible > 0.0:
        return visible
    return float(row.get("verts", 0.0) or 0.0)


def _is_empty_startup_sample(row: Dict[str, Any]) -> bool:
    """Ignora muestras antes de que el mundo haya dibujado algo."""
    return (
        float(row.get("fps", 0.0) or 0.0) <= 0.0
        and float(row.get("verts", 0.0) or 0.0) <= 0.0
        and float(row.get("chunksD", 0.0) or 0.0) <= 0.0
        and float(row.get("chunksLOD", 0.0) or 0.0) <= 0.0
        and float(row.get("ent", 0.0) or 0.0) <= 0.0
    )


def _format_worst_sample(row: Dict[str, Any]) -> str:
    chunk_dist = f"{int(row.get('chunkDist', 0.0) or 0.0):>3}" if "chunkDist" in row else "  -"
    chunk_extra = f"{float(row.get('chunkExtra', 0.0) or 0.0):>4.2f}" if "chunkExtra" in row else "   -"
    detail_dist = f"{int(row.get('detailDist', 0.0) or 0.0):>3}" if "detailDist" in row else "  -"
    detail_near = f"{int(row.get('detailNear', 0.0) or 0.0):>3}" if "detailNear" in row else "  -"
    visible = f"{int(row.get('visibleVerts', 0.0) or 0.0):>7}" if "visibleVerts" in row else "      -"
    visible_lod = f"{int(row.get('visibleLODVerts', 0.0) or 0.0):>7}" if "visibleLODVerts" in row else "      -"
    return (
        f"{row.get('preset') or '-':<8} "
        f"fps={float(row.get('fps', 0.0) or 0.0):>5.1f} "
        f"verts={int(row.get('verts', 0.0) or 0.0):>6} "
        f"vis={visible} "
        f"lodV={visible_lod} "
        f"chunksD={int(row.get('chunksD', 0.0) or 0.0):>2} "
        f"chunksLOD={int(row.get('chunksLOD', 0.0) or 0.0):>2} "
        f"uploads={int(row.get('uploads', 0.0) or 0.0):>2} "
        f"chunkDist={chunk_dist} "
        f"extra={chunk_extra} "
        f"detail={detail_dist}/{detail_near} "
        f"hiddenChunks={int(row.get('hiddenChunks', 0.0) or 0.0):>2} "
        f"session={row.get('session') or '-'}"
    )


def _bottleneck_hint(worst_samples: List[Dict[str, Any]]) -> str:
    if not worst_samples:
        return "Sin muestras suficientes para sugerir cuello de botella."
    avg_vertices = _average([_visible_or_upload_vertices(row) for row in worst_samples])
    avg_lod_chunks = _average([float(row.get("chunksLOD", 0.0) or 0.0) for row in worst_samples])
    avg_lod_vertices = _average(_positive_values(worst_samples, "visibleLODVerts"))
    avg_uploads = _average([float(row.get("uploads", 0.0) or 0.0) for row in worst_samples])
    avg_draw_chunks = _average([float(row.get("chunksD", 0.0) or 0.0) for row in worst_samples])
    if avg_uploads >= HIGH_UPLOADS_HINT:
        return (
            "Probable streaming/carga de chunks: los tirones coinciden con uploads altos. "
            "Revisar generacion, subida de mallas y presupuesto por frame."
        )
    if avg_vertices >= HIGH_VERTICES_HINT or avg_lod_chunks >= HIGH_LOD_CHUNKS_HINT or avg_lod_vertices >= HIGH_VERTICES_HINT:
        return (
            "Probable render/LOD: los tirones coinciden con muchos vertices visibles o chunks LOD, "
            "sin uploads altos. Revisar distancia, impostores y detalle lejano."
        )
    if avg_draw_chunks <= 3.0 and avg_vertices < HIGH_VERTICES_HINT:
        return (
            "Probable CPU/logica o movimiento: los tirones ocurren con poca carga visible. "
            "Revisar contexto del jugador, IA, colisiones y calculos por frame."
        )
    return (
        "Cuello mixto: no domina una sola senal. Revisar log de movimiento junto con este reporte."
    )


def _summarize_preset(preset: str, rows: List[Dict[str, Any]]) -> PresetRuntimeSummary:
    fps = [float(row.get("fps", 0.0) or 0.0) for row in rows]
    scale = [float(row.get("scale", 1.0) or 1.0) for row in rows]
    vertices = [float(row.get("verts", 0.0) or 0.0) for row in rows]
    visible_vertices = _positive_values(rows, "visibleVerts")
    visible_lod_vertices = _positive_values(rows, "visibleLODVerts")
    visible_detail_vertices = _positive_values(rows, "visibleDetailVerts")
    uploads = [float(row.get("uploads", 0.0) or 0.0) for row in rows]
    chunk_distance = _positive_values(rows, "chunkDist")
    chunk_extra = _positive_values(rows, "chunkExtra")
    hidden_chunks = [float(row.get("hiddenChunks", 0.0) or 0.0) for row in rows]
    hidden_entities = [float(row.get("hiddenEnt", 0.0) or 0.0) for row in rows]
    stream_ms = [float(row.get("streamMs", 0.0) or 0.0) for row in rows]
    summary = PresetRuntimeSummary(
        preset=preset,
        samples=len(rows),
        avg_fps=_average(fps),
        min_fps=min(fps) if fps else 0.0,
        avg_scale=_average(scale),
        avg_vertices=_average(vertices),
        avg_visible_vertices=_average(visible_vertices),
        avg_visible_lod_vertices=_average(visible_lod_vertices),
        avg_visible_detail_vertices=_average(visible_detail_vertices),
        avg_uploads=_average(uploads),
        avg_chunk_distance=_average(chunk_distance),
        avg_chunk_extra=_average(chunk_extra),
        avg_hidden_chunks=_average(hidden_chunks),
        avg_hidden_entities=_average(hidden_entities),
        avg_stream_ms=_average(stream_ms),
    )
    summary.score = (
        summary.avg_fps * 10.0
        + summary.min_fps * 3.0
        + summary.avg_scale * 20.0
        - summary.avg_uploads * 2.0
        - summary.avg_stream_ms * 0.05
    )
    if summary.samples < 4:
        summary.notes = "Pocas muestras; jugar mas tiempo antes de decidir."
    elif summary.min_fps < 24.0:
        summary.notes = "Tiene caidas fuertes; conviene bajar detalle o revisar picos."
    elif summary.avg_fps >= 50.0:
        summary.notes = "Fluido en estas muestras."
    else:
        summary.notes = "Jugable, pero observar movimiento real."
    return summary


def analyze_preset_runtime_samples(root: str | None = None, session_mode: str | None = None) -> Dict[str, Any]:
    logs_dir = _find_logs_dir(root)
    path = logs_dir / LOG_NAME
    if not path.exists():
        return {
            "ok": False,
            "logs_dir": str(logs_dir),
            "path": str(path),
            "samples": 0,
            "sessions": 0,
            "latest_session": "",
            "analyzed_session": "all",
            "best_preset": "",
            "ready_presets": [],
            "missing_presets": list(EXPECTED_PRESETS),
            "min_samples_per_preset": MIN_SAMPLES_PER_PRESET,
            "recommendation": "Aun no hay muestras. Ejecuta el juego unos segundos con low/balanced/high.",
            "summaries": [],
        }

    rows_by_preset: Dict[str, List[Dict[str, Any]]] = {}
    sessions: Dict[str, int] = {}
    sample_rows: List[Dict[str, Any]] = []
    ignored_empty_startup_samples = 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        values = _parse_line(line)
        session = str(values.get("session") or "")
        if session:
            sessions[session] = sessions.get(session, 0) + 1
        if values.get("event") == "session_start" or "fps" not in values:
            continue
        if _is_empty_startup_sample(values):
            ignored_empty_startup_samples += 1
            continue
        sample_rows.append(values)

    session_mode = (session_mode or os.environ.get("JUEGO_PRESET_ANALYZE_SESSION", "all")).strip().lower() or "all"
    latest_session = sorted(sessions)[-1] if sessions else ""
    analyzed_session = ""
    if session_mode == "latest":
        analyzed_session = latest_session
    elif session_mode not in {"all", "*"}:
        analyzed_session = session_mode

    if analyzed_session:
        sample_rows = [
            row for row in sample_rows
            if str(row.get("session") or "") == analyzed_session
        ]

    for values in sample_rows:
        preset = str(values.get("preset") or "balanced").lower()
        rows_by_preset.setdefault(preset, []).append(values)

    summaries = [_summarize_preset(preset, rows) for preset, rows in sorted(rows_by_preset.items())]
    worst_samples = sorted(
        sample_rows,
        key=lambda row: float(row.get("fps", 0.0) or 0.0),
    )[:WORST_SAMPLE_LIMIT]
    bottleneck_hint = _bottleneck_hint(worst_samples)
    usable = [item for item in summaries if item.samples >= MIN_SAMPLES_PER_PRESET]
    ready_presets = sorted(item.preset for item in usable if item.preset in VALID_PRESETS)
    missing_presets = [preset for preset in EXPECTED_PRESETS if preset not in ready_presets]
    comparison_ready = not missing_presets
    severe_drop_presets = sorted(
        item.preset for item in usable
        if item.preset in VALID_PRESETS and item.min_fps < SEVERE_DROP_FPS
    )
    has_severe_drops = bool(severe_drop_presets)
    if usable:
        best = max(usable, key=lambda item: item.score)
        scope = f" en sesion {analyzed_session}" if analyzed_session else ""
        if comparison_ready:
            if has_severe_drops:
                drop_text = ", ".join(severe_drop_presets)
                recommendation = (
                    f"Mejor candidato{scope} con comparacion completa: {best.preset}. "
                    f"Pero hay caidas fuertes en: {drop_text}."
                )
                ok = False
            else:
                recommendation = f"Mejor candidato{scope} con comparacion completa: {best.preset}."
                ok = True
        else:
            missing_text = ", ".join(missing_presets)
            recommendation = (
                f"Mejor candidato parcial{scope}: {best.preset}. "
                f"Faltan muestras suficientes de: {missing_text}."
            )
            ok = False
    else:
        best = max(summaries, key=lambda item: item.samples, default=None)
        if analyzed_session:
            recommendation = f"Hay pocas muestras en sesion {analyzed_session}; prueba cada preset al menos 12 segundos."
        else:
            recommendation = "Hay pocas muestras; prueba cada preset al menos 12 segundos."
        ok = False
    return {
        "ok": ok,
        "logs_dir": str(logs_dir),
        "path": str(path),
        "samples": sum(item.samples for item in summaries),
        "ignored_empty_startup_samples": ignored_empty_startup_samples,
        "sessions": len(sessions),
        "latest_session": latest_session,
        "analyzed_session": analyzed_session or "all",
        "best_preset": best.preset if best else "",
        "ready_presets": ready_presets,
        "missing_presets": missing_presets,
        "severe_drop_presets": severe_drop_presets,
        "has_severe_drops": has_severe_drops,
        "worst_samples": worst_samples,
        "bottleneck_hint": bottleneck_hint,
        "min_samples_per_preset": MIN_SAMPLES_PER_PRESET,
        "recommendation": recommendation,
        "summaries": [item.to_dict() for item in summaries],
    }


def compact_status(stats: Dict[str, Any]) -> str:
    status = f"presetSamples {stats.get('samples', 0)}"
    if stats.get("best_preset"):
        status += f" best={stats.get('best_preset')}"
    if stats.get("ok"):
        status += " compareOK"
    return status


def format_preset_runtime_report(stats: Dict[str, Any]) -> str:
    recommended_preset = recommended_graphics_preset(stats)
    confidence = "alta" if stats.get("ok") else "baja"
    lines = [
        "JUEGO 1.6 - REPORTE DE PRESETS GRAFICOS",
        "",
        f"Estado: {'comparacion suficiente' if stats.get('ok') else 'requiere atencion'}",
        f"Muestras analizadas: {int(stats.get('samples', 0) or 0)}",
        f"Muestras vacias ignoradas: {int(stats.get('ignored_empty_startup_samples', 0) or 0)}",
        f"Sesiones detectadas: {int(stats.get('sessions', 0) or 0)}",
        f"Ultima sesion: {stats.get('latest_session') or '-'}",
        f"Sesion analizada: {stats.get('analyzed_session') or 'all'}",
        f"Mejor candidato: {stats.get('best_preset') or '-'}",
        f"Preset recomendado para jugar: {recommended_preset} ({confidence})",
        f"Presets listos: {', '.join(stats.get('ready_presets') or []) or '-'}",
        f"Faltan presets: {', '.join(stats.get('missing_presets') or []) or '-'}",
        f"Presets con caidas fuertes: {', '.join(stats.get('severe_drop_presets') or []) or '-'}",
        f"Pista de cuello de botella: {stats.get('bottleneck_hint') or '-'}",
        f"Minimo por preset: {int(stats.get('min_samples_per_preset', MIN_SAMPLES_PER_PRESET) or MIN_SAMPLES_PER_PRESET)} muestras",
        "",
        f"Recomendacion: {stats.get('recommendation') or '-'}",
        "",
    ]
    summaries = list(stats.get("summaries") or [])
    if not summaries:
        lines.extend([
            "Aun no hay datos por preset.",
            "",
            "Flujo recomendado:",
            "1. Ejecutar PROBAR_PRESETS_OPENGL.bat.",
            "2. Limpiar el log.",
            "3. Probar low, balanced y high caminando 1-2 minutos.",
            "4. Analizar todo el historial.",
        ])
        return "\n".join(lines) + "\n"

    lines.append("Resumen por preset:")
    lines.append("preset      muestras  fps_prom  fps_min  escala  vertices  visibleV  lodV     uploads  chunkDist  extra  stream_ms  nota")
    lines.append("----------  --------  --------  -------  ------  --------  --------  -------  -------  ---------  -----  ---------  ----")
    for item in sorted(summaries, key=lambda row: float(row.get("score", 0.0) or 0.0), reverse=True):
        avg_chunk_distance = float(item.get("avg_chunk_distance", 0.0) or 0.0)
        avg_chunk_extra = float(item.get("avg_chunk_extra", 0.0) or 0.0)
        avg_visible_vertices = float(item.get("avg_visible_vertices", 0.0) or 0.0)
        avg_visible_lod_vertices = float(item.get("avg_visible_lod_vertices", 0.0) or 0.0)
        chunk_distance_text = f"{avg_chunk_distance:>9.0f}" if avg_chunk_distance > 0.0 else "        -"
        chunk_extra_text = f"{avg_chunk_extra:>5.2f}" if avg_chunk_extra > 0.0 else "    -"
        visible_vertices_text = f"{avg_visible_vertices:>8.0f}" if avg_visible_vertices > 0.0 else "       -"
        visible_lod_text = f"{avg_visible_lod_vertices:>7.0f}" if avg_visible_lod_vertices > 0.0 else "      -"
        lines.append(
            f"{str(item.get('preset') or '-')[:10]:<10}  "
            f"{int(item.get('samples', 0) or 0):>8}  "
            f"{float(item.get('avg_fps', 0.0) or 0.0):>8.1f}  "
            f"{float(item.get('min_fps', 0.0) or 0.0):>7.1f}  "
            f"{float(item.get('avg_scale', 0.0) or 0.0):>6.2f}  "
            f"{float(item.get('avg_vertices', 0.0) or 0.0):>8.0f}  "
            f"{visible_vertices_text}  "
            f"{visible_lod_text}  "
            f"{float(item.get('avg_uploads', 0.0) or 0.0):>7.1f}  "
            f"{chunk_distance_text}  "
            f"{chunk_extra_text}  "
            f"{float(item.get('avg_stream_ms', 0.0) or 0.0):>9.1f}  "
            f"{item.get('notes') or ''}"
        )
    worst_samples = list(stats.get("worst_samples") or [])
    if worst_samples:
        lines.extend([
            "",
            "Peores muestras reales:",
            "preset    fps    vertices visibleV lodV    chunksD chunksLOD uploads chunkDist extra detail hiddenChunks session",
            "-------- ----- -------- -------- ------- ------- -------- ------- --------- ----- ------ ------------ -------",
        ])
        for row in worst_samples:
            lines.append(_format_worst_sample(row))
        lines.extend([
            "",
            f"Pista: {stats.get('bottleneck_hint') or '-'}",
        ])
    lines.extend([
        "",
        "Lectura rapida:",
        "- fps_prom alto significa movimiento mas suave.",
        "- fps_min bajo revela tirones o caidas fuertes.",
        "- escala cerca de 1.00 significa que la calidad adaptativa no tuvo que bajar mucho.",
        "- uploads y stream_ms altos pueden indicar carga de chunks o mallas.",
    ])
    return "\n".join(lines) + "\n"


def write_preset_runtime_report(stats: Dict[str, Any], root: str | None = None) -> str:
    logs_dir = _find_logs_dir(root)
    logs_dir.mkdir(parents=True, exist_ok=True)
    report_path = logs_dir / REPORT_NAME
    report_path.write_text(format_preset_runtime_report(stats), encoding="utf-8")
    return str(report_path)


def recommended_graphics_preset(stats: Dict[str, Any]) -> str:
    best = str(stats.get("best_preset") or "").strip().lower()
    if stats.get("ok") and best in VALID_PRESETS:
        return best
    return "balanced"


def format_recommended_preset_file(stats: Dict[str, Any]) -> str:
    preset = recommended_graphics_preset(stats)
    confidence = "ok" if stats.get("ok") else "low"
    reason = str(stats.get("recommendation") or "").replace("\n", " ").strip()
    return "\n".join([
        f"preset={preset}",
        f"confidence={confidence}",
        f"samples={int(stats.get('samples', 0) or 0)}",
        f"ignored_empty_startup_samples={int(stats.get('ignored_empty_startup_samples', 0) or 0)}",
        f"best_preset={stats.get('best_preset') or ''}",
        f"ready_presets={','.join(stats.get('ready_presets') or [])}",
        f"missing_presets={','.join(stats.get('missing_presets') or [])}",
        f"severe_drop_presets={','.join(stats.get('severe_drop_presets') or [])}",
        f"bottleneck_hint={str(stats.get('bottleneck_hint') or '').replace(chr(10), ' ')}",
        f"reason={reason}",
        "",
    ])


def write_recommended_graphics_preset(stats: Dict[str, Any], root: str | None = None) -> str:
    logs_dir = _find_logs_dir(root)
    logs_dir.mkdir(parents=True, exist_ok=True)
    preset_path = logs_dir / RECOMMENDED_PRESET_NAME
    preset_path.write_text(format_recommended_preset_file(stats), encoding="utf-8")
    return str(preset_path)


if __name__ == "__main__":
    stats = analyze_preset_runtime_samples()
    print("Preset runtime samples:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
    print("report:", write_preset_runtime_report(stats))
    print("recommended:", write_recommended_graphics_preset(stats))
