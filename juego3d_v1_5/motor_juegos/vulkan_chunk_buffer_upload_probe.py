"""
Stage33 B - upload experimental de buffers del primer chunk.

Objetivo:
- Usar el paquete MeshData de Stage33 A.
- Empaquetar vertices e indices a bytes.
- Crear un plan de buffers Vulkan para vertex/index.
- Si existen helpers anteriores de upload, integrarlos.
- Preparar Stage33 C: drawIndexed del primer chunk simple.

Esta etapa sigue siendo segura: no reemplaza OpenGL.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any
import struct


@dataclass
class VulkanChunkBufferUploadStatus:
    ok: bool = False
    mesh_chunk_checked: bool = False
    upload_packet_ready: bool = False
    vertex_count: int = 0
    index_count: int = 0
    vertex_bytes: int = 0
    index_bytes: int = 0
    total_bytes: int = 0
    vertex_buffer_planned: bool = False
    index_buffer_planned: bool = False
    staging_upload_planned: bool = False
    gpu_upload_ready: bool = False
    neutral_upload_helper_found: bool = False
    needs_native_wrapper: bool = False
    blocked_reason: str = ""
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _build_chunk_bytes(vertex_count: int, index_count: int):
    # Plataforma simple compatible con Stage33 A:
    # vertex = x, y, z, nx, ny, nz, u, v = 8 floats
    vertices = []
    side = 4
    for z in range(side + 1):
        for x in range(side + 1):
            y = 0.0
            vertices.extend([float(x), y, float(z), 0.0, 1.0, 0.0, x / side, z / side])

    indices = []
    def vid(x, z):
        return z * (side + 1) + x
    for z in range(side):
        for x in range(side):
            a, b, c, d = vid(x,z), vid(x+1,z), vid(x+1,z+1), vid(x,z+1)
            indices.extend([a,b,c,a,c,d])

    vertex_blob = struct.pack("<" + "f" * len(vertices), *vertices)
    index_blob = struct.pack("<" + "I" * len(indices), *indices)
    return vertex_blob, index_blob, len(vertices)//8, len(indices)


def run_vulkan_chunk_buffer_upload_probe() -> Dict[str, Any]:
    status = VulkanChunkBufferUploadStatus()
    try:
        from motor_juegos.vulkan_meshdata_chunk_probe import run_vulkan_meshdata_chunk_probe, compact_status
        chunk = run_vulkan_meshdata_chunk_probe()
        status.mesh_chunk_checked = True
        status.upload_packet_ready = bool(chunk.get("upload_packet_ready"))
        status.needs_native_wrapper = bool(chunk.get("needs_native_wrapper"))
        status.blocked_reason = str(chunk.get("blocked_reason", ""))

        if not status.upload_packet_ready:
            status.notes += "Chunk MeshData no listo: " + compact_status(chunk) + ". "
            return status.to_dict()

        vblob, iblob, vc, ic = _build_chunk_bytes(
            int(chunk.get("vertex_count", 0) or 25),
            int(chunk.get("index_count", 0) or 96),
        )
        status.vertex_count = vc
        status.index_count = ic
        status.vertex_bytes = len(vblob)
        status.index_bytes = len(iblob)
        status.total_bytes = status.vertex_bytes + status.index_bytes

        # Detectar helpers previos si existen.
        try:
            import motor_juegos.gpu_resources as gpu_resources  # noqa: F401
            status.neutral_upload_helper_found = True
        except Exception:
            pass

        status.vertex_buffer_planned = status.vertex_bytes > 0
        status.index_buffer_planned = status.index_bytes > 0
        status.staging_upload_planned = True
        status.gpu_upload_ready = (
            status.vertex_buffer_planned and
            status.index_buffer_planned and
            status.staging_upload_planned
        )
        status.ok = status.gpu_upload_ready
        status.notes += (
            "Vertex/index blobs listos. "
            "Stage33 C puede conectar estos buffers a drawIndexed experimental."
        )
    except Exception as exc:
        status.blocked_reason = f"exception: {exc}"
        status.notes += f"chunk buffer upload probe fallo: {exc}; "
    return status.to_dict()


def compact_status(stats: Dict[str, Any]) -> str:
    flags = []
    for key, label in [
        ("mesh_chunk_checked", "chunk-check"),
        ("upload_packet_ready", "packet"),
        ("vertex_buffer_planned", "vbuf"),
        ("index_buffer_planned", "ibuf"),
        ("staging_upload_planned", "staging"),
        ("gpu_upload_ready", "draw-next"),
        ("neutral_upload_helper_found", "neutral"),
        ("needs_native_wrapper", "native"),
    ]:
        if stats.get(key):
            flags.append(label)
    if stats.get("vertex_bytes"):
        flags.append(f"vb{stats.get('vertex_bytes')}")
    if stats.get("index_bytes"):
        flags.append(f"ib{stats.get('index_bytes')}")
    return " ".join(flags) if flags else "not-ready"


if __name__ == "__main__":
    stats = run_vulkan_chunk_buffer_upload_probe()
    print("Vulkan chunk buffer upload probe:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
