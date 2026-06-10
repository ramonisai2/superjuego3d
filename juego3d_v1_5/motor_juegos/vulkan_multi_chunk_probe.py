"""
Stage33 G - varios chunks MeshData en Vulkan experimental.

Objetivo:
- Tomar la ruta del primer chunk visible de Stage33 F.
- Generar un anillo de chunks alrededor del jugador.
- Preparar culling simple por radio.
- Crear una lista neutral de drawIndexed por chunk.
- Mantener OpenGL como modo jugable estable.

Esto todavia no convierte Vulkan en el juego completo. Es una etapa de
preparacion para varios chunks visibles en la ruta experimental.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Tuple
import math
import time


ChunkCoord = Tuple[int, int]


@dataclass
class VulkanMultiChunkStatus:
    ok: bool = False
    first_chunk_checked: bool = False
    first_chunk_route_ready: bool = False
    ring_generated: bool = False
    chunk_radius: int = 1
    chunk_count: int = 0
    culling_planned: bool = False
    culling_ready: bool = False
    visible_chunk_count: int = 0
    culled_chunk_count: int = 0
    draw_list_ready: bool = False
    draw_command_count: int = 0
    total_vertex_count: int = 0
    total_index_count: int = 0
    command_sequence: str = ""
    multi_chunk_route_ready: bool = False
    opengl_fallback_available: bool = True
    needs_native_wrapper: bool = False
    blocked_reason: str = ""
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _generate_chunk_ring(radius: int) -> List[ChunkCoord]:
    radius = max(1, int(radius))
    coords: List[ChunkCoord] = []
    for z in range(-radius, radius + 1):
        for x in range(-radius, radius + 1):
            coords.append((x, z))
    return sorted(coords, key=lambda c: (abs(c[0]) + abs(c[1]), c[1], c[0]))


def _passes_simple_culling(coord: ChunkCoord, radius: int) -> bool:
    x, z = coord
    return math.sqrt(float(x * x + z * z)) <= float(radius) + 0.35


def _make_draw_commands(coords: List[ChunkCoord], radius: int) -> List[Dict[str, Any]]:
    commands: List[Dict[str, Any]] = []
    first_index = 0
    vertex_offset = 0
    chunk_vertex_count = 25
    chunk_index_count = 96

    for coord in coords:
        if not _passes_simple_culling(coord, radius):
            continue
        x, z = coord
        commands.append(
            {
                "coord": coord,
                "material": "terrain_grass",
                "bounds": (
                    float(x * 4),
                    -0.25,
                    float(z * 4),
                    float(x * 4 + 4),
                    0.25,
                    float(z * 4 + 4),
                ),
                "index_count": chunk_index_count,
                "instance_count": 1,
                "first_index": first_index,
                "vertex_offset": vertex_offset,
                "first_instance": len(commands),
            }
        )
        first_index += chunk_index_count
        vertex_offset += chunk_vertex_count

    return commands


def run_vulkan_multi_chunk_probe(radius: int = 1, frames: int = 12) -> Dict[str, Any]:
    status = VulkanMultiChunkStatus(chunk_radius=max(1, int(radius)))
    try:
        from motor_juegos.vulkan_first_chunk_visible_probe import (
            run_vulkan_first_chunk_visible_probe,
            compact_status as compact_first,
        )

        first = run_vulkan_first_chunk_visible_probe(frames=1)
        status.first_chunk_checked = True
        status.first_chunk_route_ready = bool(
            first.get("frame_visible_route_ready") or first.get("visible_chunk_done")
        )
        status.needs_native_wrapper = bool(first.get("needs_native_wrapper"))
        status.blocked_reason = str(first.get("blocked_reason") or "")

        if not status.first_chunk_route_ready:
            status.notes += "Primer chunk visible no listo: " + compact_first(first) + ". "
            return status.to_dict()

        coords = _generate_chunk_ring(status.chunk_radius)
        status.ring_generated = True
        status.chunk_count = len(coords)
        status.culling_planned = True

        draw_commands = _make_draw_commands(coords, status.chunk_radius)
        status.visible_chunk_count = len(draw_commands)
        status.culled_chunk_count = max(0, status.chunk_count - status.visible_chunk_count)
        status.culling_ready = status.visible_chunk_count > 0
        status.draw_command_count = len(draw_commands)
        status.total_vertex_count = status.visible_chunk_count * 25
        status.total_index_count = sum(int(cmd["index_count"]) for cmd in draw_commands)
        status.draw_list_ready = status.draw_command_count > 0 and status.total_index_count > 0

        status.command_sequence = (
            "for chunk in visible_chunks: vkCmdBindVertexBuffers > "
            "vkCmdBindIndexBuffer > vkCmdDrawIndexed"
        )
        status.multi_chunk_route_ready = (
            status.ring_generated
            and status.culling_ready
            and status.draw_list_ready
        )

        for _ in range(max(1, int(frames))):
            time.sleep(0.001)

        status.ok = status.multi_chunk_route_ready and not status.needs_native_wrapper
        if status.ok:
            status.notes += (
                "Anillo de chunks MeshData listo para varios drawIndexed experimentales. "
                "La siguiente etapa puede intentar varios chunks visibles."
            )
        else:
            status.notes += (
                "Anillo de chunks preparado, pero el present real confiable todavia "
                "requiere wrapper nativo/backend Vulkan persistente real."
            )
    except Exception as exc:
        status.blocked_reason = f"exception: {exc}"
        status.notes += f"multi chunk probe fallo: {exc}; "
    return status.to_dict()


def compact_status(stats: Dict[str, Any]) -> str:
    flags = []
    for key, label in [
        ("first_chunk_checked", "first-check"),
        ("first_chunk_route_ready", "first"),
        ("ring_generated", "ring"),
        ("culling_ready", "culling"),
        ("draw_list_ready", "drawlist"),
        ("multi_chunk_route_ready", "multi-next"),
        ("ok", "multiOK"),
        ("needs_native_wrapper", "native"),
    ]:
        if stats.get(key):
            flags.append(label)
    if stats.get("visible_chunk_count"):
        flags.append(f"chunks{stats.get('visible_chunk_count')}")
    if stats.get("total_index_count"):
        flags.append(f"indices{stats.get('total_index_count')}")
    return " ".join(flags) if flags else "not-ready"


if __name__ == "__main__":
    stats = run_vulkan_multi_chunk_probe()
    print("Vulkan multi chunk probe:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
