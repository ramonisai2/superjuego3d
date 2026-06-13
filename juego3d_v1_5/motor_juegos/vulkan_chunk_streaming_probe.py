"""
Stage33 J - carga/descarga dinamica de chunks por movimiento.

Objetivo:
- Tomar el anillo centrado en jugador/camara de Stage33 I.
- Simular movimiento entre chunks.
- Calcular que chunks se cargan, se conservan y se descargan.
- Preparar una cola neutral para upload/release Vulkan.
- Mantener OpenGL como modo jugable estable.

Esto aun no reemplaza el gestor real de chunks del juego. Prepara la logica de
streaming para conectarla despues al backend Vulkan persistente.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Iterable, List, Set, Tuple
import math
import time
from motor_juegos.chunk_math import chunk_coord, generate_visible_chunk_ring


ChunkCoord = Tuple[int, int]


@dataclass
class VulkanChunkStreamingStatus:
    ok: bool = False
    player_ring_checked: bool = False
    player_ring_ready: bool = False
    movement_path_ready: bool = False
    streaming_sets_ready: bool = False
    upload_queue_ready: bool = False
    release_queue_ready: bool = False
    draw_list_refresh_ready: bool = False
    chunk_size: float = 64.0
    chunk_radius: int = 1
    path_points: int = 0
    start_chunk_x: int = 0
    start_chunk_z: int = 0
    end_chunk_x: int = 0
    end_chunk_z: int = 0
    loaded_initial_count: int = 0
    load_count: int = 0
    keep_count: int = 0
    unload_count: int = 0
    final_loaded_count: int = 0
    upload_budget_per_frame: int = 2
    release_budget_per_frame: int = 3
    estimated_upload_frames: int = 0
    estimated_release_frames: int = 0
    submitted_frame_count: int = 0
    command_sequence: str = ""
    opengl_fallback_available: bool = True
    needs_native_wrapper: bool = False
    blocked_reason: str = ""
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _ring(center: ChunkCoord, radius: int) -> Set[ChunkCoord]:
    return set(generate_visible_chunk_ring(center, radius))


def _default_path(chunk_size: float) -> List[Tuple[float, float]]:
    # Cruza de chunk 0,0 a chunk 2,1 para forzar load/keep/unload.
    return [
        (32.0, 32.0),
        (chunk_size * 0.9, 32.0),
        (chunk_size * 1.2, 32.0),
        (chunk_size * 2.1, chunk_size * 1.1),
    ]


def _center_from_position(point: Tuple[float, float], chunk_size: float) -> ChunkCoord:
    x, z = point
    return (chunk_coord(x, chunk_size), chunk_coord(z, chunk_size))


def run_vulkan_chunk_streaming_probe(
    path: Iterable[Tuple[float, float]] | None = None,
    chunk_size: float = 64.0,
    radius: int = 1,
    frames: int = 10,
    upload_budget_per_frame: int = 2,
    release_budget_per_frame: int = 3,
) -> Dict[str, Any]:
    status = VulkanChunkStreamingStatus(
        chunk_size=float(chunk_size),
        chunk_radius=max(1, int(radius)),
        upload_budget_per_frame=max(1, int(upload_budget_per_frame)),
        release_budget_per_frame=max(1, int(release_budget_per_frame)),
    )
    try:
        from motor_juegos.vulkan_player_chunk_ring_probe import (
            run_vulkan_player_chunk_ring_probe,
            compact_status as compact_ring,
        )

        points = list(path) if path is not None else _default_path(status.chunk_size)
        if not points:
            status.blocked_reason = "empty movement path"
            status.notes += "Ruta de movimiento vacia. "
            return status.to_dict()

        first_x, first_z = points[0]
        ring_status = run_vulkan_player_chunk_ring_probe(
            player_x=first_x,
            player_z=first_z,
            camera_x=first_x,
            camera_z=first_z,
            chunk_size=status.chunk_size,
            radius=status.chunk_radius,
            frames=1,
        )
        status.player_ring_checked = True
        status.player_ring_ready = bool(ring_status.get("ok") or ring_status.get("centered_draw_list_ready"))
        status.needs_native_wrapper = bool(ring_status.get("needs_native_wrapper"))
        status.blocked_reason = str(ring_status.get("blocked_reason") or "")

        if not status.player_ring_ready:
            status.notes += "Anillo centrado no listo: " + compact_ring(ring_status) + ". "
            return status.to_dict()

        centers = [_center_from_position(point, status.chunk_size) for point in points]
        status.path_points = len(points)
        status.start_chunk_x, status.start_chunk_z = centers[0]
        status.end_chunk_x, status.end_chunk_z = centers[-1]
        status.movement_path_ready = True

        loaded = _ring(centers[0], status.chunk_radius)
        status.loaded_initial_count = len(loaded)
        total_load: Set[ChunkCoord] = set()
        total_keep: Set[ChunkCoord] = set()
        total_unload: Set[ChunkCoord] = set()

        for center in centers[1:]:
            wanted = _ring(center, status.chunk_radius)
            to_load = wanted - loaded
            to_keep = wanted & loaded
            to_unload = loaded - wanted
            total_load.update(to_load)
            total_keep.update(to_keep)
            total_unload.update(to_unload)
            loaded = (loaded | to_load) - to_unload

        status.load_count = len(total_load)
        status.keep_count = len(total_keep)
        status.unload_count = len(total_unload)
        status.final_loaded_count = len(loaded)
        status.streaming_sets_ready = status.final_loaded_count > 0
        status.upload_queue_ready = True
        status.release_queue_ready = True
        status.draw_list_refresh_ready = status.streaming_sets_ready
        status.estimated_upload_frames = int(math.ceil(status.load_count / float(status.upload_budget_per_frame)))
        status.estimated_release_frames = int(math.ceil(status.unload_count / float(status.release_budget_per_frame)))
        status.command_sequence = (
            "movement path > center chunk changed > diff rings > "
            "queue uploads > queue releases > refresh draw list"
        )

        for _ in range(max(1, int(frames))):
            time.sleep(0.001)
            status.submitted_frame_count += 1

        status.ok = (
            status.player_ring_ready
            and status.movement_path_ready
            and status.streaming_sets_ready
            and status.upload_queue_ready
            and status.release_queue_ready
            and status.draw_list_refresh_ready
            and not status.needs_native_wrapper
        )

        if status.ok:
            status.notes += (
                "Streaming de chunks por movimiento preparado. "
                "La siguiente etapa puede conectar estas colas al gestor real de mundo."
            )
        else:
            status.notes += (
                "Streaming preparado, pero el present real confiable todavia requiere "
                "wrapper nativo/backend Vulkan persistente real."
            )
    except Exception as exc:
        status.blocked_reason = f"exception: {exc}"
        status.notes += f"chunk streaming probe fallo: {exc}; "
    return status.to_dict()


def compact_status(stats: Dict[str, Any]) -> str:
    flags = []
    for key, label in [
        ("player_ring_checked", "ring-check"),
        ("player_ring_ready", "ring"),
        ("movement_path_ready", "path"),
        ("streaming_sets_ready", "sets"),
        ("upload_queue_ready", "uploadQ"),
        ("release_queue_ready", "releaseQ"),
        ("draw_list_refresh_ready", "refresh"),
        ("ok", "streamOK"),
        ("needs_native_wrapper", "native"),
    ]:
        if stats.get(key):
            flags.append(label)
    if stats.get("path_points"):
        flags.append(f"path{stats.get('path_points')}")
    if stats.get("streaming_sets_ready"):
        flags.append(f"load{stats.get('load_count')}")
        flags.append(f"unload{stats.get('unload_count')}")
    if stats.get("final_loaded_count"):
        flags.append(f"loaded{stats.get('final_loaded_count')}")
    return " ".join(flags) if flags else "not-ready"


if __name__ == "__main__":
    stats = run_vulkan_chunk_streaming_probe()
    print("Vulkan chunk streaming probe:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
