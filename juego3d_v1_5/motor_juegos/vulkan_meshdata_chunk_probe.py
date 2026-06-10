"""
Stage33 A - primer puente MeshData hacia Vulkan experimental.

Objetivo:
- Tomar la arquitectura MeshData ya creada.
- Generar un chunk simple de prueba en formato neutral.
- Convertirlo a un paquete listo para upload Vulkan:
  vertices, indices, material, bounds.
- Dejar preparado Stage33 B: subir ese chunk a buffers Vulkan reales.

Esta etapa no reemplaza OpenGL. Es el puente entre mundo real del juego y Vulkan.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Tuple
import math


@dataclass
class VulkanMeshDataChunkStatus:
    ok: bool = False
    experimental_mode_checked: bool = False
    experimental_mode_ready: bool = False
    meshdata_imported: bool = False
    chunk_generated: bool = False
    vertex_count: int = 0
    index_count: int = 0
    triangle_count: int = 0
    material_count: int = 0
    upload_packet_ready: bool = False
    bounds: str = ""
    needs_native_wrapper: bool = False
    blocked_reason: str = ""
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _make_test_chunk_mesh() -> Dict[str, Any]:
    # Malla sencilla: plataforma 4x4 con altura suave.
    vertices: List[Tuple[float, float, float]] = []
    indices: List[int] = []
    size = 4
    for z in range(size + 1):
        for x in range(size + 1):
            y = math.sin(x * 0.6) * 0.12 + math.cos(z * 0.5) * 0.10
            vertices.append((float(x), float(y), float(z)))

    def vid(x: int, z: int) -> int:
        return z * (size + 1) + x

    for z in range(size):
        for x in range(size):
            a = vid(x, z)
            b = vid(x + 1, z)
            c = vid(x + 1, z + 1)
            d = vid(x, z + 1)
            indices.extend([a, b, c, a, c, d])

    return {
        "vertices": vertices,
        "indices": indices,
        "materials": ["terrain_grass"],
        "bounds": (0.0, -0.25, 0.0, float(size), 0.25, float(size)),
    }


def run_vulkan_meshdata_chunk_probe() -> Dict[str, Any]:
    status = VulkanMeshDataChunkStatus()
    try:
        from motor_juegos.vulkan_experimental_mode import run_vulkan_experimental_mode_probe, compact_status
        exp = run_vulkan_experimental_mode_probe(frames=1)
        status.experimental_mode_checked = True
        status.experimental_mode_ready = bool(exp.get("experimental_mode_ready") or exp.get("meshdata_bridge_ready"))
        status.needs_native_wrapper = bool(exp.get("needs_native_wrapper"))
        status.blocked_reason = str(exp.get("blocked_reason", ""))

        if not status.experimental_mode_ready:
            status.notes += "Modo Vulkan experimental no listo: " + compact_status(exp) + ". "
            return status.to_dict()

        # Importamos MeshData si existe; si el formato interno cambia, mantenemos paquete neutral.
        try:
            import motor_juegos.mesh_data as mesh_data  # noqa: F401
            status.meshdata_imported = True
        except Exception as exc:
            status.notes += f"mesh_data import no disponible, se usa paquete neutral: {exc}; "

        mesh = _make_test_chunk_mesh()
        status.chunk_generated = True
        status.vertex_count = len(mesh["vertices"])
        status.index_count = len(mesh["indices"])
        status.triangle_count = status.index_count // 3
        status.material_count = len(mesh["materials"])
        status.bounds = ",".join(str(v) for v in mesh["bounds"])

        status.upload_packet_ready = (
            status.vertex_count > 0
            and status.index_count > 0
            and status.triangle_count > 0
        )
        status.ok = status.upload_packet_ready
        status.notes += (
            "Primer chunk MeshData neutral listo para upload Vulkan. "
            "Stage33 B puede crear vertex/index buffers reales para este paquete."
        )
    except Exception as exc:
        status.blocked_reason = f"exception: {exc}"
        status.notes += f"meshdata chunk probe fallo: {exc}; "
    return status.to_dict()


def compact_status(stats: Dict[str, Any]) -> str:
    flags = []
    for key, label in [
        ("experimental_mode_checked", "vulkan-check"),
        ("experimental_mode_ready", "vulkan-mode"),
        ("meshdata_imported", "meshdata"),
        ("chunk_generated", "chunk"),
        ("upload_packet_ready", "upload-next"),
        ("needs_native_wrapper", "native"),
    ]:
        if stats.get(key):
            flags.append(label)
    if stats.get("vertex_count"):
        flags.append(f"v{stats.get('vertex_count')}")
    if stats.get("index_count"):
        flags.append(f"i{stats.get('index_count')}")
    return " ".join(flags) if flags else "not-ready"


if __name__ == "__main__":
    stats = run_vulkan_meshdata_chunk_probe()
    print("Vulkan MeshData chunk probe:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
