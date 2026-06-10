"""
Stage33 N - comparativa segura OpenGL legacy vs puente seguro.

Antes de pedir logs reales, comparamos la carga estimada de chunks entre la
gestion legacy y el puente Stage33 L/M usando la misma ruta simulada.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Iterable, Set, Tuple

from motor_juegos.world_chunk_stream_bridge import build_world_chunk_stream_plan


ChunkCoord = Tuple[int, int]


@dataclass
class StrategyTotals:
    requests: int = 0
    lod_creates: int = 0
    detail_releases: int = 0
    lod_releases: int = 0
    cancels: int = 0
    final_detail: int = 0
    final_lod: int = 0
    final_queue: int = 0

    def to_dict(self) -> Dict[str, int]:
        return asdict(self)


@dataclass
class StreamBridgeComparisonStatus:
    ok: bool = False
    path_ready: bool = False
    legacy_sim_ready: bool = False
    bridge_sim_ready: bool = False
    comparison_ready: bool = False
    safe_to_try_in_game: bool = False
    centers_tested: int = 0
    legacy_requests: int = 0
    bridge_requests: int = 0
    legacy_lod_creates: int = 0
    bridge_lod_creates: int = 0
    legacy_releases: int = 0
    bridge_releases: int = 0
    request_delta: int = 0
    lod_delta: int = 0
    release_delta: int = 0
    final_detail_delta: int = 0
    final_lod_delta: int = 0
    recommendation: str = ""
    notes: str = ""
    blocked_reason: str = ""

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


def _near(coords: Iterable[ChunkCoord], center: ChunkCoord) -> list[ChunkCoord]:
    cx, cz = center
    return sorted(set(coords), key=lambda c: ((c[0] - cx) ** 2 + (c[1] - cz) ** 2, c[1], c[0]))


def _simulate_legacy(centers: list[ChunkCoord], detail_radius: int, lod_radius: int, max_queue: int) -> StrategyTotals:
    loaded_detail: Set[ChunkCoord] = {(0, 0), (0, 1), (1, 0)}
    loaded_lod: Set[ChunkCoord] = {(-2, 0), (-1, 1), (1, 1), (2, 0)}
    queued: Set[ChunkCoord] = {(2, 0)}
    totals = StrategyTotals()

    for center in centers:
        lod_targets = _square(center, lod_radius)
        detail_targets = _square(center, detail_radius)

        for coord in _near(lod_targets - loaded_lod - loaded_detail, center):
            loaded_lod.add(coord)
            totals.lod_creates += 1

        requestable = detail_targets - loaded_detail - queued
        for coord in _near(requestable, center)[: max(0, max_queue - len(queued))]:
            queued.add(coord)
            totals.requests += 1

        stale_detail = loaded_detail - detail_targets
        stale_lod = {coord for coord in loaded_lod if coord not in lod_targets or coord in loaded_detail}
        loaded_detail.difference_update(stale_detail)
        loaded_lod.difference_update(stale_lod)
        totals.detail_releases += len(stale_detail)
        totals.lod_releases += len(stale_lod)

        completed = _near(queued, center)[:2]
        for coord in completed:
            queued.remove(coord)
            loaded_detail.add(coord)
            loaded_lod.discard(coord)

    totals.final_detail = len(loaded_detail)
    totals.final_lod = len(loaded_lod)
    totals.final_queue = len(queued)
    return totals


def _simulate_bridge(centers: list[ChunkCoord], detail_radius: int, lod_radius: int, max_queue: int) -> StrategyTotals:
    loaded_detail: Set[ChunkCoord] = {(0, 0), (0, 1), (1, 0)}
    loaded_lod: Set[ChunkCoord] = {(-2, 0), (-1, 1), (1, 1), (2, 0)}
    queued: Set[ChunkCoord] = {(2, 0)}
    pending: Set[ChunkCoord] = set()
    totals = StrategyTotals()

    for center in centers:
        plan = build_world_chunk_stream_plan(
            center=center,
            loaded_detail=loaded_detail,
            loaded_lod=loaded_lod,
            queued_detail=queued,
            pending_detail=pending,
            detail_radius=detail_radius,
            lod_radius=lod_radius,
            max_detail_requests=max(0, max_queue - len(queued)),
        )
        totals.requests += len(plan.request_detail)
        totals.lod_creates += len(plan.create_lod)
        totals.detail_releases += len(plan.release_detail)
        totals.lod_releases += len(plan.release_lod)
        totals.cancels += len(plan.cancel_requests)

        loaded_lod.update(plan.create_lod)
        loaded_detail.difference_update(plan.release_detail)
        loaded_lod.difference_update(plan.release_lod)
        queued.difference_update(plan.cancel_requests)
        pending.difference_update(plan.cancel_requests)
        queued.update(plan.request_detail)

        completed = _near(queued, center)[:2]
        for coord in completed:
            queued.remove(coord)
            loaded_detail.add(coord)
            loaded_lod.discard(coord)

    totals.final_detail = len(loaded_detail)
    totals.final_lod = len(loaded_lod)
    totals.final_queue = len(queued)
    return totals


def run_stream_bridge_comparison_probe() -> Dict[str, Any]:
    status = StreamBridgeComparisonStatus()
    try:
        centers = [(0, 0), (1, 0), (2, 1), (3, 1), (4, 2)]
        status.path_ready = True
        status.centers_tested = len(centers)

        legacy = _simulate_legacy(centers, detail_radius=1, lod_radius=2, max_queue=3)
        bridge = _simulate_bridge(centers, detail_radius=1, lod_radius=2, max_queue=3)
        status.legacy_sim_ready = True
        status.bridge_sim_ready = True

        status.legacy_requests = legacy.requests
        status.bridge_requests = bridge.requests
        status.legacy_lod_creates = legacy.lod_creates
        status.bridge_lod_creates = bridge.lod_creates
        status.legacy_releases = legacy.detail_releases + legacy.lod_releases
        status.bridge_releases = bridge.detail_releases + bridge.lod_releases
        status.request_delta = bridge.requests - legacy.requests
        status.lod_delta = bridge.lod_creates - legacy.lod_creates
        status.release_delta = status.bridge_releases - status.legacy_releases
        status.final_detail_delta = bridge.final_detail - legacy.final_detail
        status.final_lod_delta = bridge.final_lod - legacy.final_lod

        status.comparison_ready = True
        status.safe_to_try_in_game = (
            abs(status.request_delta) <= 3
            and abs(status.lod_delta) <= 8
            and abs(status.release_delta) <= 8
            and abs(status.final_detail_delta) <= 3
        )
        status.ok = status.comparison_ready and status.safe_to_try_in_game
        status.recommendation = (
            "Probar LANZAR_OPENGL_STREAM_BRIDGE_SAFE.bat y comparar sensacion/FPS."
            if status.ok
            else "Mantener puente en probe; revisar diferencias antes de prueba jugable."
        )
        status.notes = "Comparativa neutral lista. Todavia no reemplaza OpenGL legacy."
    except Exception as exc:
        status.blocked_reason = f"exception: {exc}"
        status.notes = f"stream bridge comparison probe fallo: {exc}"
    return status.to_dict()


def compact_status(stats: Dict[str, Any]) -> str:
    flags = []
    for key, label in [
        ("path_ready", "path"),
        ("legacy_sim_ready", "legacy"),
        ("bridge_sim_ready", "bridge"),
        ("comparison_ready", "compare"),
        ("safe_to_try_in_game", "try-game"),
        ("ok", "compareOK"),
    ]:
        if stats.get(key):
            flags.append(label)
    if stats.get("comparison_ready"):
        flags.append(f"dReq{stats.get('request_delta')}")
        flags.append(f"dLOD{stats.get('lod_delta')}")
        flags.append(f"dFree{stats.get('release_delta')}")
    return " ".join(flags) if flags else "not-ready"


if __name__ == "__main__":
    stats = run_stream_bridge_comparison_probe()
    print("Stream bridge comparison probe:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
