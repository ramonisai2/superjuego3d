"""Recomendador para elegir metodo de terreno sin decidir solo por ms."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict

from motor_juegos.terrain_noise_experiment import benchmark_full_chunk_modes


@dataclass
class TerrainMethodAdvice:
    ok: bool = False
    recommended_default: str = "current"
    test_candidate: str = ""
    action_code: str = ""
    action_label: str = ""
    notes: str = ""
    benchmark: Dict[str, Any] | None = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _by_mode(stats: Dict[str, Any], mode: str) -> Dict[str, Any]:
    for item in stats.get("results", []):
        if item.get("mode") == mode:
            return item
    return {}


def advise_terrain_method() -> Dict[str, Any]:
    stats = benchmark_full_chunk_modes()
    advice = TerrainMethodAdvice(ok=bool(stats.get("ok")), benchmark=stats)
    if not advice.ok:
        advice.action_code = "BENCHMARK_FAILED"
        advice.action_label = "No se pudo comparar terreno"
        advice.notes = "Mantener current."
        return advice.to_dict()

    speedups = stats.get("speedups_vs_current", {})
    current = _by_mode(stats, "current")
    fast = _by_mode(stats, "fast_noise")
    lite = _by_mode(stats, "fast_noise_lite")
    fast_speed = float(speedups.get("fast_noise", 0.0) or 0.0)
    lite_speed = float(speedups.get("fast_noise_lite", 0.0) or 0.0)

    current_water = int(current.get("water", 0) or 0)
    fast_water = int(fast.get("water", 0) or 0)
    lite_water = int(lite.get("water", 0) or 0)

    advice.recommended_default = "current"
    if fast_speed >= 1.25:
        advice.test_candidate = "fast_noise"
        advice.action_code = "TEST_FAST_NOISE"
        advice.action_label = "Probar fast_noise visualmente"
        advice.notes = (
            f"fast_noise gana x{fast_speed:.2f} en chunk completo. "
            "No lo hago default hasta confirmar que conserva lagos/biomas."
        )
    else:
        advice.action_code = "KEEP_CURRENT"
        advice.action_label = "Mantener metodo actual"
        advice.notes = "La ganancia de fast_noise no justifica el cambio todavia."

    if lite_speed > fast_speed:
        advice.notes += (
            f" fast_noise_lite gana x{lite_speed:.2f}, pero es candidato de referencia, "
            "no default, porque simplifica mas la identidad del mundo."
        )

    if current_water > 0 and fast_water <= 0:
        advice.notes += " En la muestra fast_noise perdio agua visible; revisar en juego antes de decidir."
    if current_water > 0 and lite_water <= 0:
        advice.notes += " En la muestra lite tambien perdio agua visible."

    return advice.to_dict()


def compact_status(stats: Dict[str, Any]) -> str:
    if not stats.get("ok"):
        return "not-ready"
    parts = [str(stats.get("action_code") or "UNKNOWN")]
    if stats.get("test_candidate"):
        parts.append(f"candidate={stats.get('test_candidate')}")
    parts.append(f"default={stats.get('recommended_default', 'current')}")
    return " ".join(parts)
