"""
Stage33 I - anillo de chunks centrado en jugador/camara.

Objetivo:
- Tomar la ruta de varios chunks visibles de Stage33 H.
- Convertir la posicion del jugador/camara a coordenada de chunk.
- Generar el anillo alrededor de ese centro real/simulado.
- Preparar drawIndexed por chunk centrado en el jugador.
- Mantener OpenGL como modo jugable estable.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Tuple
import time
from motor_juegos.chunk_math import chunk_coord, generate_square_chunk_ring, passes_chunk_ring_cull


ChunkCoord = Tuple[int, int]


@dataclass
class VulkanPlayerChunkRingStatus:
    ok: bool = False
    multi_visible_checked: bool = False
    multi_visible_route_ready: bool = False
    player_position_ready: bool = False
    camera_position_ready: bool = False
    center_chunk_ready: bool = False
    centered_ring_ready: bool = False
    centered_culling_ready: bool = False
    centered_draw_list_ready: bool = False
    player_x: float = 0.0
    player_z: float = 0.0
    camera_x: float = 0.0
    camera_z: float = 0.0
    chunk_size: float = 64.0
    chunk_radius: int = 1
    center_chunk_x: int = 0
    center_chunk_z: int = 0
    candidate_chunk_count: int = 0
    visible_chunk_count: int = 0
    draw_call_count: int = 0
    total_index_count: int = 0
    submitted_frame_count: int = 0
    command_sequence: str = ""
    opengl_fallback_available: bool = True
    needs_native_wrapper: bool = False
    blocked_reason: str = ""
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _generate_centered_ring(center: ChunkCoord, radius: int) -> List[ChunkCoord]:
    return generate_square_chunk_ring(center, radius)


def _passes_center_culling(coord: ChunkCoord, center: ChunkCoord, radius: int) -> bool:
    return passes_chunk_ring_cull(coord, center, radius)


def run_vulkan_player_chunk_ring_probe(
    player_x: float = 32.0,
    player_z: float = 32.0,
    camera_x: float | None = None,
    camera_z: float | None = None,
    chunk_size: float = 64.0,
    radius: int = 1,
    frames: int = 12,
) -> Dict[str, Any]:
    status = VulkanPlayerChunkRingStatus(
        player_x=float(player_x),
        player_z=float(player_z),
        camera_x=float(player_x if camera_x is None else camera_x),
        camera_z=float(player_z if camera_z is None else camera_z),
        chunk_size=float(chunk_size),
        chunk_radius=max(1, int(radius)),
    )
    try:
        from motor_juegos.vulkan_multi_chunk_visible_probe import (
            run_vulkan_multi_chunk_visible_probe,
            compact_status as compact_visible,
        )

        multi_visible = run_vulkan_multi_chunk_visible_probe(radius=status.chunk_radius, frames=1)
        status.multi_visible_checked = True
        status.multi_visible_route_ready = bool(
            multi_visible.get("multi_visible_done") or multi_visible.get("multi_chunk_route_ready")
        )
        status.needs_native_wrapper = bool(multi_visible.get("needs_native_wrapper"))
        status.blocked_reason = str(multi_visible.get("blocked_reason") or "")

        if not status.multi_visible_route_ready:
            status.notes += "Varios chunks visibles no listos: " + compact_visible(multi_visible) + ". "
            return status.to_dict()

        status.player_position_ready = True
        status.camera_position_ready = True
        status.center_chunk_x = chunk_coord(status.camera_x, status.chunk_size)
        status.center_chunk_z = chunk_coord(status.camera_z, status.chunk_size)
        center = (status.center_chunk_x, status.center_chunk_z)
        status.center_chunk_ready = True

        coords = _generate_centered_ring(center, status.chunk_radius)
        visible = [coord for coord in coords if _passes_center_culling(coord, center, status.chunk_radius)]
        status.candidate_chunk_count = len(coords)
        status.visible_chunk_count = len(visible)
        status.draw_call_count = len(visible)
        status.total_index_count = status.draw_call_count * 96
        status.centered_ring_ready = status.candidate_chunk_count > 0
        status.centered_culling_ready = status.visible_chunk_count > 0
        status.centered_draw_list_ready = status.total_index_count > 0
        status.command_sequence = (
            "camera/player position > center chunk > centered ring > "
            "culling > drawIndexed visible chunks"
        )

        for _ in range(max(1, int(frames))):
            time.sleep(0.001)
            status.submitted_frame_count += 1

        status.ok = (
            status.multi_visible_route_ready
            and status.center_chunk_ready
            and status.centered_ring_ready
            and status.centered_culling_ready
            and status.centered_draw_list_ready
            and not status.needs_native_wrapper
        )

        if status.ok:
            status.notes += (
                "Anillo de chunks centrado en jugador/camara listo. "
                "La siguiente etapa puede preparar carga/descarga dinamica por movimiento."
            )
        else:
            status.notes += (
                "Anillo centrado preparado, pero el present real confiable todavia "
                "requiere wrapper nativo/backend Vulkan persistente real."
            )
    except Exception as exc:
        status.blocked_reason = f"exception: {exc}"
        status.notes += f"player chunk ring probe fallo: {exc}; "
    return status.to_dict()


def compact_status(stats: Dict[str, Any]) -> str:
    flags = []
    for key, label in [
        ("multi_visible_checked", "visible-check"),
        ("multi_visible_route_ready", "visible"),
        ("player_position_ready", "player-pos"),
        ("camera_position_ready", "camera-pos"),
        ("center_chunk_ready", "center"),
        ("centered_ring_ready", "ring"),
        ("centered_culling_ready", "culling"),
        ("centered_draw_list_ready", "drawlist"),
        ("ok", "playerRingOK"),
        ("needs_native_wrapper", "native"),
    ]:
        if stats.get(key):
            flags.append(label)
    if stats.get("center_chunk_ready"):
        flags.append(f"chunk({stats.get('center_chunk_x')},{stats.get('center_chunk_z')})")
    if stats.get("visible_chunk_count"):
        flags.append(f"chunks{stats.get('visible_chunk_count')}")
    return " ".join(flags) if flags else "not-ready"


if __name__ == "__main__":
    stats = run_vulkan_player_chunk_ring_probe()
    print("Vulkan player chunk ring probe:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
