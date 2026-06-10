"""
Stage33 K - puente entre streaming Vulkan y gestor real de chunks.

Este modulo no importa pygame ni toca el bucle principal. Convierte el diff de
streaming en operaciones compatibles con las estructuras actuales de main.py:
- mundo_chunks: detalle cargado
- mundo_chunks_simple: LOD/simple cargado
- cola_de_peticiones: solicitudes de detalle
- chunks_pendientes: datos recibidos aun sin upload
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any, Dict, Iterable, List, Set, Tuple
import math


ChunkCoord = Tuple[int, int]


@dataclass
class WorldChunkStreamPlan:
    center: ChunkCoord
    detail_targets: Set[ChunkCoord] = field(default_factory=set)
    lod_targets: Set[ChunkCoord] = field(default_factory=set)
    request_detail: List[ChunkCoord] = field(default_factory=list)
    create_lod: List[ChunkCoord] = field(default_factory=list)
    release_detail: List[ChunkCoord] = field(default_factory=list)
    release_lod: List[ChunkCoord] = field(default_factory=list)
    cancel_requests: List[ChunkCoord] = field(default_factory=list)
    keep_detail: List[ChunkCoord] = field(default_factory=list)
    keep_lod: List[ChunkCoord] = field(default_factory=list)

    def summary(self) -> Dict[str, Any]:
        return {
            "center": self.center,
            "detail_targets": len(self.detail_targets),
            "lod_targets": len(self.lod_targets),
            "request_detail": len(self.request_detail),
            "create_lod": len(self.create_lod),
            "release_detail": len(self.release_detail),
            "release_lod": len(self.release_lod),
            "cancel_requests": len(self.cancel_requests),
            "keep_detail": len(self.keep_detail),
            "keep_lod": len(self.keep_lod),
        }


@dataclass
class WorldChunkStreamBridgeStatus:
    ok: bool = False
    streaming_checked: bool = False
    streaming_ready: bool = False
    world_state_ready: bool = False
    targets_ready: bool = False
    operations_ready: bool = False
    queue_plan_ready: bool = False
    release_plan_ready: bool = False
    draw_refresh_ready: bool = False
    center_chunk_x: int = 0
    center_chunk_z: int = 0
    detail_radius: int = 1
    lod_radius: int = 2
    detail_loaded_count: int = 0
    lod_loaded_count: int = 0
    queued_count: int = 0
    pending_count: int = 0
    request_detail_count: int = 0
    create_lod_count: int = 0
    release_detail_count: int = 0
    release_lod_count: int = 0
    cancel_request_count: int = 0
    keep_detail_count: int = 0
    keep_lod_count: int = 0
    operation_sequence: str = ""
    opengl_fallback_available: bool = True
    needs_native_wrapper: bool = False
    blocked_reason: str = ""
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _square(center: ChunkCoord, radius: int) -> Set[ChunkCoord]:
    cx, cz = center
    radius = max(0, int(radius))
    return {
        (cx + dx, cz + dz)
        for dz in range(-radius, radius + 1)
        for dx in range(-radius, radius + 1)
    }


def _sorted_near(coords: Iterable[ChunkCoord], center: ChunkCoord) -> List[ChunkCoord]:
    cx, cz = center
    return sorted(set(coords), key=lambda c: ((c[0] - cx) ** 2 + (c[1] - cz) ** 2, c[1], c[0]))


def build_world_chunk_stream_plan(
    center: ChunkCoord,
    loaded_detail: Iterable[ChunkCoord],
    loaded_lod: Iterable[ChunkCoord],
    queued_detail: Iterable[ChunkCoord],
    pending_detail: Iterable[ChunkCoord],
    detail_radius: int = 1,
    lod_radius: int = 2,
    max_detail_requests: int = 3,
) -> WorldChunkStreamPlan:
    loaded_detail_set = set(loaded_detail)
    loaded_lod_set = set(loaded_lod)
    queued_set = set(queued_detail)
    pending_set = set(pending_detail)

    detail_targets = _square(center, detail_radius)
    lod_targets = _square(center, max(lod_radius, detail_radius)) - detail_targets

    requestable = detail_targets - loaded_detail_set - queued_set - pending_set
    request_detail = _sorted_near(requestable, center)[: max(0, int(max_detail_requests))]

    create_lod = _sorted_near(lod_targets - loaded_lod_set - loaded_detail_set, center)
    release_detail = _sorted_near(loaded_detail_set - detail_targets, center)
    release_lod = _sorted_near(loaded_lod_set - lod_targets - detail_targets, center)
    cancel_requests = _sorted_near((queued_set | pending_set) - detail_targets, center)
    keep_detail = _sorted_near(loaded_detail_set & detail_targets, center)
    keep_lod = _sorted_near(loaded_lod_set & lod_targets, center)

    return WorldChunkStreamPlan(
        center=center,
        detail_targets=detail_targets,
        lod_targets=lod_targets,
        request_detail=request_detail,
        create_lod=create_lod,
        release_detail=release_detail,
        release_lod=release_lod,
        cancel_requests=cancel_requests,
        keep_detail=keep_detail,
        keep_lod=keep_lod,
    )


def run_world_chunk_stream_bridge_probe() -> Dict[str, Any]:
    status = WorldChunkStreamBridgeStatus(detail_radius=1, lod_radius=2)
    try:
        from motor_juegos.vulkan_chunk_streaming_probe import (
            run_vulkan_chunk_streaming_probe,
            compact_status as compact_stream,
        )

        stream = run_vulkan_chunk_streaming_probe(radius=status.detail_radius, frames=1)
        status.streaming_checked = True
        status.streaming_ready = bool(stream.get("ok") or stream.get("streaming_sets_ready"))
        status.needs_native_wrapper = bool(stream.get("needs_native_wrapper"))
        status.blocked_reason = str(stream.get("blocked_reason") or "")

        if not status.streaming_ready:
            status.notes += "Streaming de chunks no listo: " + compact_stream(stream) + ". "
            return status.to_dict()

        center = (int(stream.get("end_chunk_x", 0) or 0), int(stream.get("end_chunk_z", 0) or 0))
        status.center_chunk_x, status.center_chunk_z = center

        loaded_detail = {(center[0] - 1, center[1]), center, (center[0], center[1] - 1)}
        loaded_lod = _square((center[0] - 1, center[1]), 2) - loaded_detail
        queued_detail = {(center[0] + 2, center[1]), (center[0] - 3, center[1])}
        pending_detail = {(center[0], center[1] + 2)}

        status.detail_loaded_count = len(loaded_detail)
        status.lod_loaded_count = len(loaded_lod)
        status.queued_count = len(queued_detail)
        status.pending_count = len(pending_detail)
        status.world_state_ready = True

        plan = build_world_chunk_stream_plan(
            center=center,
            loaded_detail=loaded_detail,
            loaded_lod=loaded_lod,
            queued_detail=queued_detail,
            pending_detail=pending_detail,
            detail_radius=status.detail_radius,
            lod_radius=status.lod_radius,
            max_detail_requests=3,
        )

        status.targets_ready = bool(plan.detail_targets and plan.lod_targets)
        status.request_detail_count = len(plan.request_detail)
        status.create_lod_count = len(plan.create_lod)
        status.release_detail_count = len(plan.release_detail)
        status.release_lod_count = len(plan.release_lod)
        status.cancel_request_count = len(plan.cancel_requests)
        status.keep_detail_count = len(plan.keep_detail)
        status.keep_lod_count = len(plan.keep_lod)
        status.queue_plan_ready = True
        status.release_plan_ready = True
        status.draw_refresh_ready = True
        status.operations_ready = status.targets_ready and status.queue_plan_ready and status.release_plan_ready
        status.operation_sequence = (
            "world state snapshot > target detail/lod rings > request detail > "
            "create lod > release stale handles > cancel stale requests > refresh draw list"
        )

        status.ok = (
            status.streaming_ready
            and status.world_state_ready
            and status.operations_ready
            and status.draw_refresh_ready
            and not status.needs_native_wrapper
        )

        if status.ok:
            status.notes += (
                "Puente de streaming listo para conectar con mundo_chunks, mundo_chunks_simple, "
                "cola_de_peticiones y chunks_pendientes."
            )
        else:
            status.notes += (
                "Puente preparado, pero Vulkan real todavia requiere backend persistente nativo."
            )
    except Exception as exc:
        status.blocked_reason = f"exception: {exc}"
        status.notes += f"world chunk stream bridge probe fallo: {exc}; "
    return status.to_dict()


def compact_status(stats: Dict[str, Any]) -> str:
    flags = []
    for key, label in [
        ("streaming_checked", "stream-check"),
        ("streaming_ready", "stream"),
        ("world_state_ready", "world"),
        ("targets_ready", "targets"),
        ("queue_plan_ready", "queue"),
        ("release_plan_ready", "release"),
        ("draw_refresh_ready", "refresh"),
        ("ok", "bridgeOK"),
        ("needs_native_wrapper", "native"),
    ]:
        if stats.get(key):
            flags.append(label)
    if stats.get("world_state_ready"):
        flags.append(f"center({stats.get('center_chunk_x')},{stats.get('center_chunk_z')})")
    if stats.get("operations_ready"):
        flags.append(f"req{stats.get('request_detail_count')}")
        flags.append(f"lod{stats.get('create_lod_count')}")
        flags.append(f"free{stats.get('release_detail_count') + stats.get('release_lod_count')}")
    return " ".join(flags) if flags else "not-ready"


if __name__ == "__main__":
    stats = run_world_chunk_stream_bridge_probe()
    print("World chunk stream bridge probe:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
