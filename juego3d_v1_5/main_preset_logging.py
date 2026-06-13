"""Logs de muestras de preset grafico y detalle del mundo."""

from __future__ import annotations

import os
import time


def world_detail_debug_status(env, resource_amount_func):
    try:
        status = env.get_world_detail_density_status()
    except Exception:
        status = {"preset": "balanced"}
    status = dict(status)
    status["fibra_amount"] = resource_amount_func("fibra")
    status["madera_amount"] = resource_amount_func("madera")
    status["piedra_amount"] = resource_amount_func("piedra")
    return status


def append_preset_runtime_sample(
    fps,
    *,
    enabled,
    session,
    env,
    resource_amount_func,
    adaptive_quality,
    adaptive_streaming,
    render_stats,
    chunk_render_extra,
    detail_chunk_back_margin,
):
    if not enabled:
        return
    try:
        os.makedirs(os.path.dirname(_preset_sample_log_path()), exist_ok=True)
        world_detail = world_detail_debug_status(env, resource_amount_func)
        line = (
            f"{time.strftime('%Y-%m-%d %H:%M:%S')} "
            f"session={session} "
            f"preset={os.environ.get('JUEGO_GRAPHICS_PRESET', 'balanced')} "
            f"world={world_detail.get('preset', 'balanced')} "
            f"fps={float(fps):.1f} "
            f"fpsAvg={float(adaptive_quality.get('fps_avg', 0.0) or 0.0):.1f} "
            f"auto={adaptive_quality.get('state', 'OK')} "
            f"scale={float(adaptive_quality.get('scale', 1.0) or 1.0):.2f} "
            f"chunksD={render_stats.get('chunks_detalle', 0)} "
            f"chunksLOD={render_stats.get('chunks_lod', 0)} "
            f"hiddenChunks={render_stats.get('chunks_ocultos', 0)} "
            f"ent={render_stats.get('entidades_render', 0)} "
            f"hiddenEnt={render_stats.get('entidades_ocultas', 0)} "
            f"verts={render_stats.get('mesh_vertices', 0)} "
            f"visibleVerts={render_stats.get('visible_chunk_vertices', 0)} "
            f"visibleDetailVerts={render_stats.get('visible_detail_vertices', 0)} "
            f"visibleLODVerts={render_stats.get('visible_lod_vertices', 0)} "
            f"visibleKB={int(render_stats.get('visible_chunk_bytes', 0) or 0)//1024} "
            f"uploads={render_stats.get('uploads_frame', 0)} "
            f"chunkDist={render_stats.get('adaptive_chunk_distance', 0)} "
            f"chunkExtra={float(render_stats.get('adaptive_chunk_extra', chunk_render_extra) or chunk_render_extra):.2f} "
            f"detailDist={render_stats.get('adaptive_detail_chunk_distance', 0)} "
            f"detailNear={render_stats.get('adaptive_detail_near_keep', 0)} "
            f"detailBack={float(render_stats.get('adaptive_detail_back_margin', detail_chunk_back_margin) or detail_chunk_back_margin):.2f} "
            f"streamMs={int(float(adaptive_streaming.get('interval', 0.05)) * 1000)} "
            f"densityG={float(world_detail.get('grass', 0.0) or 0.0):.2f} "
            f"densityD={float(world_detail.get('deco', 0.0) or 0.0):.2f} "
            f"densityR={float(world_detail.get('rock', 0.0) or 0.0):.2f} "
            f"resFMP={world_detail.get('fibra_amount', 1)}/{world_detail.get('madera_amount', 1)}/{world_detail.get('piedra_amount', 1)}"
        )
        with open(_preset_sample_log_path(), "a", encoding="utf-8") as handle:
            handle.write(line + "\n")
    except Exception:
        pass


def append_preset_session_start(*, enabled, session, env):
    if not enabled:
        return
    try:
        os.makedirs(os.path.dirname(_preset_sample_log_path()), exist_ok=True)
        with open(_preset_sample_log_path(), "a", encoding="utf-8") as handle:
            handle.write(
                f"{time.strftime('%Y-%m-%d %H:%M:%S')} "
                f"session={session} "
                f"event=session_start "
                f"preset={os.environ.get('JUEGO_GRAPHICS_PRESET', 'balanced')} "
                f"world={env.get_world_detail_density_status().get('preset', 'balanced')}\n"
            )
    except Exception:
        pass


def update_runtime_logs(
    dt,
    log_timer,
    sample_accum,
    *,
    current_fov,
    chunk_actual_x,
    chunk_actual_z,
    player,
    enemies,
    enable_stream_bridge,
    stream_bridge_stats,
    preset_sample_log_enabled,
    preset_sample_log_interval,
    preset_sample_session,
    engine,
    env,
    resource_amount_func,
    adaptive_quality,
    adaptive_streaming,
    render_stats,
    chunk_render_extra,
    detail_chunk_back_margin,
):
    """Actualiza logs de consola y muestras de preset sin ensuciar main.update."""
    log_timer += dt
    if log_timer >= 0.5:
        print(
            f"[INFO] FOV: {current_fov:.1f} | "
            f"Chunk: ({chunk_actual_x},{chunk_actual_z}) | "
            f"Vida: {player.health:.0f} | Stamina: {player.stamina:.0f} | "
            f"Enemigos: {len(enemies)}"
        )
        if enable_stream_bridge:
            print(
                "[STREAM-BRIDGE] "
                f"calls={stream_bridge_stats.get('calls', 0)} "
                f"center=({stream_bridge_stats.get('last_center_x', 0)},{stream_bridge_stats.get('last_center_z', 0)}) "
                f"req={stream_bridge_stats.get('detail_requested_total', 0)} "
                f"lodQ={stream_bridge_stats.get('lod_queued_total', 0)} "
                f"lod={stream_bridge_stats.get('lod_created_total', 0)} "
                f"freeD={stream_bridge_stats.get('detail_released_total', 0)} "
                f"freeL={stream_bridge_stats.get('lod_released_total', 0)} "
                f"cancel={stream_bridge_stats.get('requests_cancelled_total', 0)} "
                f"queue={stream_bridge_stats.get('queue_len', 0)} "
                f"lodQueue={stream_bridge_stats.get('lod_queue_len', 0)} "
                f"pending={stream_bridge_stats.get('pending_len', 0)} "
                f"loadedD={stream_bridge_stats.get('detail_loaded', 0)} "
                f"loadedL={stream_bridge_stats.get('lod_loaded', 0)}"
            )
        log_timer = 0.0

    if preset_sample_log_enabled:
        sample_accum = float(sample_accum or 0.0) + float(dt)
        if sample_accum >= max(0.5, float(preset_sample_log_interval)):
            sample_accum = 0.0
            sample_fps = engine.clock.get_fps() if engine and hasattr(engine, "clock") else 0.0
            append_preset_runtime_sample(
                sample_fps,
                enabled=preset_sample_log_enabled,
                session=preset_sample_session,
                env=env,
                resource_amount_func=resource_amount_func,
                adaptive_quality=adaptive_quality,
                adaptive_streaming=adaptive_streaming,
                render_stats=render_stats,
                chunk_render_extra=chunk_render_extra,
                detail_chunk_back_margin=detail_chunk_back_margin,
            )
    return log_timer, sample_accum


def _preset_sample_log_path():
    return os.path.join(os.getcwd(), "logs", "preset_runtime_samples.log")
