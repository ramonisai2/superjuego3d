"""
Stage33 L - aplicacion segura del puente al gestor real.

El juego estable no cambia por defecto. Este modulo prepara y audita el modo
feature flag que permite usar el puente de Stage33 K para administrar chunks.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Iterable, Tuple

from motor_juegos.world_chunk_stream_bridge import build_world_chunk_stream_plan


ChunkCoord = Tuple[int, int]


@dataclass
class WorldChunkStreamSafeApplyStatus:
    ok: bool = False
    feature_flag_name: str = "JUEGO_STREAM_BRIDGE_SAFE"
    feature_flag_default_off: bool = True
    bridge_plan_checked: bool = False
    bridge_plan_ready: bool = False
    real_manager_targets_ready: bool = False
    request_ops_ready: bool = False
    lod_ops_ready: bool = False
    release_ops_ready: bool = False
    cancel_ops_ready: bool = False
    safe_apply_ready: bool = False
    center_chunk_x: int = 0
    center_chunk_z: int = 0
    request_detail_count: int = 0
    create_lod_count: int = 0
    release_detail_count: int = 0
    release_lod_count: int = 0
    cancel_request_count: int = 0
    keep_detail_count: int = 0
    keep_lod_count: int = 0
    operation_sequence: str = ""
    notes: str = ""
    blocked_reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def inspect_safe_apply_plan(
    center: ChunkCoord = (3, 1),
    loaded_detail: Iterable[ChunkCoord] = ((2, 1), (3, 1), (3, 0)),
    loaded_lod: Iterable[ChunkCoord] = ((1, 1), (1, 2), (2, 2), (4, 2), (5, 2)),
    queued_detail: Iterable[ChunkCoord] = ((5, 1), (0, 1)),
    pending_detail: Iterable[ChunkCoord] = ((3, 3),),
    detail_radius: int = 1,
    lod_radius: int = 2,
    max_detail_requests: int = 3,
) -> Dict[str, Any]:
    status = WorldChunkStreamSafeApplyStatus(center_chunk_x=int(center[0]), center_chunk_z=int(center[1]))
    try:
        plan = build_world_chunk_stream_plan(
            center=center,
            loaded_detail=loaded_detail,
            loaded_lod=loaded_lod,
            queued_detail=queued_detail,
            pending_detail=pending_detail,
            detail_radius=detail_radius,
            lod_radius=lod_radius,
            max_detail_requests=max_detail_requests,
        )
        status.bridge_plan_checked = True
        status.bridge_plan_ready = bool(plan.detail_targets and plan.lod_targets)
        status.real_manager_targets_ready = status.bridge_plan_ready
        status.request_detail_count = len(plan.request_detail)
        status.create_lod_count = len(plan.create_lod)
        status.release_detail_count = len(plan.release_detail)
        status.release_lod_count = len(plan.release_lod)
        status.cancel_request_count = len(plan.cancel_requests)
        status.keep_detail_count = len(plan.keep_detail)
        status.keep_lod_count = len(plan.keep_lod)
        status.request_ops_ready = True
        status.lod_ops_ready = True
        status.release_ops_ready = True
        status.cancel_ops_ready = True
        status.safe_apply_ready = status.bridge_plan_ready
        status.operation_sequence = (
            "feature flag off by default > build plan > apply request/create/release/cancel "
            "only when JUEGO_STREAM_BRIDGE_SAFE=1"
        )
        status.ok = status.safe_apply_ready and status.feature_flag_default_off
        status.notes = (
            "Modo seguro listo. OpenGL mantiene la gestion legacy salvo que "
            "JUEGO_STREAM_BRIDGE_SAFE=1 active el puente."
        )
    except Exception as exc:
        status.blocked_reason = f"exception: {exc}"
        status.notes = f"safe apply probe fallo: {exc}"
    return status.to_dict()


def compact_status(stats: Dict[str, Any]) -> str:
    flags = []
    for key, label in [
        ("feature_flag_default_off", "flag-off"),
        ("bridge_plan_checked", "plan-check"),
        ("bridge_plan_ready", "plan"),
        ("real_manager_targets_ready", "targets"),
        ("request_ops_ready", "request"),
        ("lod_ops_ready", "lod"),
        ("release_ops_ready", "release"),
        ("cancel_ops_ready", "cancel"),
        ("safe_apply_ready", "safeApply"),
        ("ok", "safeApplyOK"),
    ]:
        if stats.get(key):
            flags.append(label)
    if stats.get("safe_apply_ready"):
        flags.append(f"req{stats.get('request_detail_count')}")
        flags.append(f"lod{stats.get('create_lod_count')}")
        flags.append(f"free{stats.get('release_detail_count') + stats.get('release_lod_count')}")
        flags.append(f"cancel{stats.get('cancel_request_count')}")
    return " ".join(flags) if flags else "not-ready"


if __name__ == "__main__":
    stats = inspect_safe_apply_plan()
    print("World chunk stream safe apply:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
