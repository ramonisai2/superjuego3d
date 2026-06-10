"""
Stage33 R - presupuestos configurables del puente seguro.

Permite ajustar el puente con variables de entorno sin tocar codigo:
- JUEGO_STREAM_BRIDGE_PRESET=safe|balanced|aggressive
- JUEGO_STREAM_DETAIL_RADIUS
- JUEGO_STREAM_LOD_RADIUS
- JUEGO_STREAM_MAX_REQUESTS
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict
import os


@dataclass
class StreamBridgeBudget:
    preset: str = "safe"
    detail_radius: int = 1
    lod_radius: int = 2
    max_detail_requests: int = 3
    source: str = "defaults"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def compact(self) -> str:
        return (
            f"{self.preset} detail={self.detail_radius} lod={self.lod_radius} "
            f"maxReq={self.max_detail_requests}"
        )


PRESETS = {
    "safe": {"detail_radius": 1, "lod_radius": 2, "max_detail_requests": 2},
    "balanced": {"detail_radius": 1, "lod_radius": 2, "max_detail_requests": 3},
    "aggressive": {"detail_radius": 2, "lod_radius": 3, "max_detail_requests": 4},
}


def _read_int(name: str, default: int, min_value: int, max_value: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return int(default)
    try:
        value = int(raw)
    except ValueError:
        return int(default)
    return max(min_value, min(max_value, value))


def get_stream_bridge_budget(
    default_detail_radius: int = 1,
    default_lod_radius: int = 2,
    default_max_requests: int = 3,
) -> StreamBridgeBudget:
    preset = os.environ.get("JUEGO_STREAM_BRIDGE_PRESET", "safe").strip().lower() or "safe"
    if preset not in PRESETS:
        preset = "safe"

    values = {
        "detail_radius": int(default_detail_radius),
        "lod_radius": int(default_lod_radius),
        "max_detail_requests": int(default_max_requests),
    }
    values.update(PRESETS[preset])

    detail_radius = _read_int("JUEGO_STREAM_DETAIL_RADIUS", values["detail_radius"], 1, 4)
    lod_radius = _read_int("JUEGO_STREAM_LOD_RADIUS", values["lod_radius"], detail_radius, 6)
    max_requests = _read_int("JUEGO_STREAM_MAX_REQUESTS", values["max_detail_requests"], 1, 12)

    return StreamBridgeBudget(
        preset=preset,
        detail_radius=detail_radius,
        lod_radius=max(lod_radius, detail_radius),
        max_detail_requests=max_requests,
        source="env" if any(os.environ.get(k) for k in (
            "JUEGO_STREAM_BRIDGE_PRESET",
            "JUEGO_STREAM_DETAIL_RADIUS",
            "JUEGO_STREAM_LOD_RADIUS",
            "JUEGO_STREAM_MAX_REQUESTS",
        )) else "defaults",
    )


def run_stream_bridge_budget_probe() -> Dict[str, Any]:
    budget = get_stream_bridge_budget()
    return {
        "ok": True,
        "preset": budget.preset,
        "detail_radius": budget.detail_radius,
        "lod_radius": budget.lod_radius,
        "max_detail_requests": budget.max_detail_requests,
        "source": budget.source,
        "notes": "Presupuesto del puente listo.",
    }


def compact_status(stats: Dict[str, Any]) -> str:
    if not stats.get("ok"):
        return "not-ready"
    return (
        f"budgetOK {stats.get('preset')} "
        f"d{stats.get('detail_radius')} l{stats.get('lod_radius')} r{stats.get('max_detail_requests')}"
    )


if __name__ == "__main__":
    stats = run_stream_bridge_budget_probe()
    print("Stream bridge budget:", compact_status(stats))
    for k, v in stats.items():
        print(f"{k}: {v}")
