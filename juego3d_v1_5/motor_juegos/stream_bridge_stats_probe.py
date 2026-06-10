"""
Stage33 M - telemetria del puente seguro de chunks.

Simula llamadas repetidas al gestor para verificar que las estadisticas que
se muestran en el HUD son coherentes antes de pedir logs reales al usuario.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Set, Tuple

from motor_juegos.world_chunk_stream_bridge import build_world_chunk_stream_plan


ChunkCoord = Tuple[int, int]


@dataclass
class StreamBridgeStatsProbeStatus:
    ok: bool = False
    feature_flag_default_off: bool = True
    simulated_calls: int = 0
    centers_tested: int = 0
    detail_requested_total: int = 0
    lod_created_total: int = 0
    detail_released_total: int = 0
    lod_released_total: int = 0
    requests_cancelled_total: int = 0
    final_detail_loaded: int = 0
    final_lod_loaded: int = 0
    final_queue_len: int = 0
    final_pending_len: int = 0
    hud_stats_ready: bool = False
    notes: str = ""
    blocked_reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def run_stream_bridge_stats_probe() -> Dict[str, Any]:
    status = StreamBridgeStatsProbeStatus()
    try:
        centers = [(0, 0), (1, 0), (2, 1), (3, 1)]
        loaded_detail: Set[ChunkCoord] = {(0, 0), (0, 1), (1, 0)}
        loaded_lod: Set[ChunkCoord] = {(-2, 0), (-1, 1), (1, 1), (2, 0)}
        queued_detail: Set[ChunkCoord] = {(2, 0)}
        pending_detail: Set[ChunkCoord] = {(1, 1)}

        for center in centers:
            plan = build_world_chunk_stream_plan(
                center=center,
                loaded_detail=loaded_detail,
                loaded_lod=loaded_lod,
                queued_detail=queued_detail,
                pending_detail=pending_detail,
                detail_radius=1,
                lod_radius=2,
                max_detail_requests=3,
            )
            status.simulated_calls += 1
            status.detail_requested_total += len(plan.request_detail)
            status.lod_created_total += len(plan.create_lod)
            status.detail_released_total += len(plan.release_detail)
            status.lod_released_total += len(plan.release_lod)
            status.requests_cancelled_total += len(plan.cancel_requests)

            loaded_lod.update(plan.create_lod)
            loaded_detail.difference_update(plan.release_detail)
            loaded_lod.difference_update(plan.release_lod)
            queued_detail.difference_update(plan.cancel_requests)
            pending_detail.difference_update(plan.cancel_requests)
            queued_detail.update(plan.request_detail)

            # Simula que hasta dos solicitudes terminan como detalle cargado.
            completed = sorted(queued_detail, key=lambda c: ((c[0] - center[0]) ** 2 + (c[1] - center[1]) ** 2, c[1], c[0]))[:2]
            for coord in completed:
                queued_detail.remove(coord)
                loaded_detail.add(coord)
                loaded_lod.discard(coord)

        status.centers_tested = len(centers)
        status.final_detail_loaded = len(loaded_detail)
        status.final_lod_loaded = len(loaded_lod)
        status.final_queue_len = len(queued_detail)
        status.final_pending_len = len(pending_detail)
        status.hud_stats_ready = (
            status.simulated_calls == status.centers_tested
            and status.final_detail_loaded > 0
            and status.final_lod_loaded > 0
        )
        status.ok = status.feature_flag_default_off and status.hud_stats_ready
        status.notes = "Telemetria del puente lista para revisar en HUD/logs cuando el flag este activo."
    except Exception as exc:
        status.blocked_reason = f"exception: {exc}"
        status.notes = f"stream bridge stats probe fallo: {exc}"
    return status.to_dict()


def compact_status(stats: Dict[str, Any]) -> str:
    flags = []
    for key, label in [
        ("feature_flag_default_off", "flag-off"),
        ("hud_stats_ready", "hud-stats"),
        ("ok", "statsOK"),
    ]:
        if stats.get(key):
            flags.append(label)
    if stats.get("simulated_calls"):
        flags.append(f"calls{stats.get('simulated_calls')}")
    if stats.get("detail_requested_total"):
        flags.append(f"req{stats.get('detail_requested_total')}")
    if stats.get("lod_created_total"):
        flags.append(f"lod{stats.get('lod_created_total')}")
    if stats.get("detail_released_total") or stats.get("lod_released_total"):
        flags.append(f"free{stats.get('detail_released_total', 0) + stats.get('lod_released_total', 0)}")
    return " ".join(flags) if flags else "not-ready"


if __name__ == "__main__":
    stats = run_stream_bridge_stats_probe()
    print("Stream bridge stats probe:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
